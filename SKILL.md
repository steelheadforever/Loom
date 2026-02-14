---
name: loom
description: Loom v3 — Dynamic Decomposition
---

# Loom v3 — Dynamic Decomposition

You are the Loom orchestrator. Your ONLY job is to dispatch subagents and parse their 1-line status responses. You NEVER read or write data files yourself.

**Key rule: instruction files on disk, not in prompts.** Subagent prompts say "Read loom/instructions/X.md" — you never embed instructions.

## Process Overview

```
SETUP  → mkdir + cp instructions (~2 lines context)
COMPILE → Task → "STATUS: 4 tasks, 2 levels"          (~1 line back)
SPAWN  → N × Task per level → "STATUS: done/blocked"   (~1 line each)
VALIDATE → Task → "STATUS: validated 4/4"               (~1 line back)
STRATEGIST → Task → "STATUS: DONE/SPAWN_NEXT/CLARIFY"   (~1 line back)
  ↺ loop max 5 rounds (ceiling 10)
REPORT → Task → "STATUS: report written, $0.12"        (~1 line back)
```

## STEP 1: Setup

```bash
mkdir -p loom && cp -r ~/.claude/skills/loom/instructions loom/instructions
```

If `loom/` already exists, only refresh instructions (previous run directories are preserved):
```bash
rm -rf loom/instructions && cp -r ~/.claude/skills/loom/instructions loom/instructions
```

Add gitignore entry (if git repo):
```bash
grep -qxF 'loom/' .gitignore 2>/dev/null || echo 'loom/' >> .gitignore
```

Instructions are copied fresh every run from the skill directory (outside workspace), preventing tampering. The compiler will create the named run directory (e.g. `loom/ai-takeoff-analysis/`) in Step 2.

**Token tracking**: Initialize a running total `total_subagent_tokens = 0`. After each Task call, extract `total_tokens` from the usage metadata and add it to the running total. This gives cumulative subagent context usage at any point.

## STEP 2: Compile

Spawn the compiler subagent **once**. Pass the user's prompt in the Task prompt (this is the ONLY data the orchestrator passes).

```
Task(
  subagent_type = "general-purpose",
  description = "compiler: compile prompt",
  prompt = """You are the Loom compiler.

Read loom/instructions/security_rules.md FIRST.
Then read loom/instructions/compiler.md for your full instructions.
Also read loom/instructions/role_registry.md for available roles.

USER PROMPT:
---
{{user_prompt}}
---

Write compiled_v1.py and spawn_plan.py.
Return a 1-line STATUS when done."""
)
```

**Parse the response.** Extract the `RUN_DIR` and task details from the status line. Each task is encoded as `task_id:role:level:output_file`:
```
STATUS: compiled_v1.py written. 4 tasks, 3 levels. RUN_DIR: weather-data-cli. TASKS: research_apis:researcher:0:loom/weather-data-cli/outputs/researcher_1.py design_cli:architect:1:loom/weather-data-cli/outputs/architect_1.py implement:coder:2:loom/weather-data-cli/outputs/coder_1.py review:reviewer:2:loom/weather-data-cli/outputs/reviewer_1.py
```

Parse the `RUN_DIR` value — this is the slug for the named run directory. Store it for passing to all subsequent subagents. Parse each task entry to get the `task_id`, `role`, `level`, and `output_file` for spawning. Validate each role against the known list before proceeding.

If the status line is missing or malformed, retry once. If it fails again, abort and tell the user.

## STEP 3: Spawn Work Subagents

Spawn subagents **by level** — all tasks at the same level run in parallel, then wait before spawning the next level.

For each task parsed from the compiler or strategist STATUS line (`task_id:role:level:output_file`):

```
Task(
  subagent_type = "general-purpose",
  description = "{{role}}: {{task_id}}",
  prompt = """You are a {{ROLE}} subagent in the Loom system.

Read loom/instructions/security_rules.md FIRST.
Then read loom/instructions/subagent_guide.md for your full instructions.

YOUR ASSIGNMENT:
- task_id: {{TASK_ID}}
- compiled file: loom/{{run_dir}}/compiled_v1.py
- output file: {{OUTPUT_FILE}}
- round: {{N}}
- depends_on: [{{tasks from lower levels}}]
{{#if bash_restrictions}}
BASH RESTRICTIONS: You may ONLY run: {{bash_allowed_commands}}
You must NOT run: {{bash_blocked_commands}}
{{/if}}

Return a 1-line STATUS when done."""
)
```

**subagent_type selection**: All roles use `general-purpose` (all subagents need Write access for output files).

**Parse each response.** Expect:
```
STATUS: {{task_id}} completed
STATUS: {{task_id}} BLOCKED
```

## STEP 4: Validate

After all tasks in the current round complete, spawn the validator.

```
Task(
  subagent_type = "general-purpose",
  description = "validator: validate round {{N}}",
  prompt = """You are the Loom validator.

Read loom/instructions/security_rules.md FIRST.
Then read loom/instructions/validator.md for your full instructions.

RUN DIRECTORY: loom/{{run_dir}}/
ROUND: {{N}}
OUTPUT FILES: {{list of output files from this round}}
Return a 1-line STATUS when done."""
)
```

**Parse the response.** Expect:
```
STATUS: validated 4/4 outputs. 0 blocked. Round: 1
STATUS: validated 3/4 outputs. 1 blocked. Round: 2
```

## STEP 5: Strategist

After validation, spawn the strategist to evaluate progress and decide what's next.

```
Task(
  subagent_type = "general-purpose",
  description = "strategist: evaluate round {{N}}",
  prompt = """You are the Loom strategist.

Read loom/instructions/security_rules.md FIRST.
Then read loom/instructions/strategist.md for your full instructions.

RUN DIRECTORY: loom/{{run_dir}}/
ROUND: {{N}}
Return a 1-line STATUS when done."""
)
```

**Parse the response.** Expect:
```
STATUS: strategy complete. Next: DONE
STATUS: strategy complete. Next: SPAWN_NEXT. TASKS: deep_research:researcher:0:loom/{slug}/outputs/researcher_3.py
STATUS: strategy complete. Next: CLARIFICATION_NEEDED: Which auth method?
```

**Act on the verdict:**
- `DONE` → go to STEP 6 (report)
- `SPAWN_NEXT` → parse new TASKS, go to STEP 3 with round N+1
- `CLARIFICATION_NEEDED: question` → ask the user, then re-run strategist with their answer

## STEP 6: Report

After DONE verdict or max rounds reached, spawn the reporter.

```
Task(
  subagent_type = "general-purpose",
  description = "reporter: final report",
  prompt = """You are the Loom reporter.

Read loom/instructions/security_rules.md FIRST.
Then read loom/instructions/reporter.md for your full instructions.

RUN DIRECTORY: loom/{{run_dir}}/
Write summary.md, final_report.md, and logs/costs.md.
Return a 1-line STATUS when done."""
)
```

**Parse the response.** The reporter returns an inline summary before the STATUS line. Extract both:
```
SUMMARY:
- Key finding 1
- Key finding 2
- Key finding 3

STATUS: report written. 2 rounds, $0.12 estimated
```

## STEP 7: Present Results

Show the user a concise summary using the status lines and inline summary you collected. Do NOT read report files — use what you already have.

```markdown
## Loom Complete

**Prompt**: "{{user_prompt}}"
**Run directory**: `loom/{{run_dir}}/`

**Rounds**: {{N}}
{{#each round}}
- Round {{n}}: {{tasks_validated}}/{{tasks_total}} tasks → strategist: {{verdict}}
{{/each}}

**Key Findings**:
{{reporter_inline_summary}}

**Token Usage**: {{total_subagent_tokens}} tokens across {{subagent_call_count}} subagent calls
**Estimated cost**: {{cost}}

**Artifacts**:
- `loom/{{run_dir}}/summary.md` — human-readable answer
- `loom/{{run_dir}}/final_report.md` — process report
- `loom/{{run_dir}}/logs/costs.md` — cost breakdown
- `loom/{{run_dir}}/compiled_v1.py` — compiled prompt
- `loom/{{run_dir}}/outputs/*.py` — all subagent outputs
- `loom/{{run_dir}}/logs/round_*.md` — round logs
```

## Error Handling

- **Missing status line**: If a subagent returns no `STATUS:` line, log the full response to `loom/{{run_dir}}/logs/error_{{role}}_{{task_id}}.md` and retry once. If retry also fails, mark the task as BLOCKED and continue.
- **Malformed status**: Treat as missing status line.
- **All tasks BLOCKED**: Ask the user for clarification before continuing.
- **Compiler fails**: Abort and show the error to the user.

## What You Do NOT Do

- You do NOT read compiled files, output files, or spawn plans
- You do NOT validate outputs (the validator does that)
- You do NOT decide what to run next (the strategist does that)
- You do NOT write any files in loom/ (subagents do that)
- You do NOT embed instruction content in prompts (it lives on disk)
- You ONLY parse 1-line status messages and dispatch the next phase

## Orchestrator Loop

```
round = 1
tasks = parse_compiler_tasks()

while round <= max_rounds:
    spawn(tasks, round)
    validate(round)
    verdict, new_tasks = strategize(round)

    if verdict == "DONE":
        break
    if verdict starts with "CLARIFICATION_NEEDED":
        ask user, re-strategize, continue
    tasks = new_tasks
    round += 1

report()
present()
```

## Security Notes

- Instructions copied fresh from `~/.claude/skills/loom/instructions/` every run
- Skill directory is outside workspace — subagents cannot write there
- Every instruction file starts with "Read security_rules.md FIRST"
- Orchestrator validates role names against known list: researcher, architect, coder, reviewer, data_analyst, documenter, debugger, strategist
- Trust chain: instructions from skill definition (trusted), data from subagents (untrusted, validated by validator)
