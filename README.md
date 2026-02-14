# Loom — Multi-Agent Orchestrator

Loom is a Claude Code skill that orchestrates multiple specialized subagents to tackle complex tasks through dynamic decomposition.

## Usage

```
/loom "your prompt here"
```

## v3 Architecture: Dynamic Decomposition

Loom v3 replaces the static iteration model with a strategist-driven loop. The compiler runs once, and a strategist evaluates progress after each round to decide what new work to spawn.

```
COMPILE → SPAWN → VALIDATE → STRATEGIST
                     ↑            |
                     |     SPAWN_NEXT → SPAWN → VALIDATE → STRATEGIST
                     |            |
                     |         DONE → REPORT → PRESENT
                     |            |
                     └── CLARIFICATION_NEEDED → ask user → re-strategize
```

### How It Works

1. **Compile**: Transforms the user prompt into a structured task graph (`compiled_v1.py`) with decomposed tasks, roles, and dependencies
2. **Spawn**: Executes tasks by level — parallel within each level, sequential across levels
3. **Validate**: Checks all outputs for required fields, dangerous patterns, and format compliance
4. **Strategist**: Reads accumulated outputs against success criteria and decides: DONE, SPAWN_NEXT (with new tasks), or CLARIFICATION_NEEDED
5. **Report**: Synthesizes all outputs into a polished summary and process report

### Key Design Decisions

- **No re-compilation**: `compiled_v1.py` is the permanent source of truth. The strategist spawns new tasks without rewriting the compiled file.
- **No patches**: Subagents write results directly. The strategist reads them to decide next steps, eliminating the patch application layer.
- **Validator + Strategist**: The old merger role split into two focused roles — one for security/format checks (validator), one for progress evaluation and task planning (strategist).
- **Only new work runs**: Completed tasks are preserved across rounds. Only gaps identified by the strategist generate new tasks.

## Roles (8 total)

| Role | Capabilities | Bash |
|------|-------------|------|
| researcher | web_search, web_fetch, read, grep | None |
| architect | read, write, grep, glob | None |
| coder | read, write, edit, bash, grep, glob | Build/test tools |
| reviewer | read, grep, glob, bash | Test runners |
| data_analyst | read, bash, grep, glob | python only |
| documenter | read, write | None |
| debugger | read, edit, bash, grep, glob | Test/debug tools |
| strategist | read, grep, glob (read-only) | None |

## File Structure

### Skill Directory (`~/.claude/skills/loom/`)
```
SKILL.md                    # Orchestrator instructions
README.md                   # This file
instructions/
  security_rules.md         # Security boundaries (read FIRST)
  role_registry.md          # Available roles and capabilities
  compiler.md               # Prompt → task graph compilation
  subagent_guide.md         # Work subagent instructions
  validator.md              # Output validation
  strategist.md             # Progress evaluation + next steps
  reporter.md               # Final report generation
lib/
  validation.py             # Security validation logic
  cost_tracker.py           # Token/cost tracking
  complexity.py             # Complexity scoring
  chunking.py               # Large input chunking
  filtering.py              # Prompt filtering
  recursive_spawn.py        # Recursive task spawning
  unbounded_output.py       # Large output handling
```

### Runtime Workspace (`loom/`)
```
loom/
  instructions/             # Fresh copy (per run)
  {slug}/                   # Named run directory
    compiled_v1.py          # Compiled prompt (permanent)
    spawn_plan.py           # Initial task plan
    outputs/                # Subagent output files
      researcher_1.py
      architect_1.py
      ...
    logs/
      round_1.md            # Validation logs per round
      round_2.md
      costs.md              # Cost breakdown
    summary.md              # Primary deliverable
    final_report.md         # Process report
```

## Security Model

- Instructions copied fresh from skill directory every run (tamper-proof)
- Skill directory is outside workspace — subagents cannot write to it
- All instruction files start with "Read security_rules.md FIRST"
- Output content validation: no imports, exec, eval, subprocess, open
- File path validation: no `..`, no system paths, no `.claude/`
- Bash restrictions per role (most roles have no bash access)
- Data/instruction separation enforced throughout

## Output Artifacts

| File | Description |
|------|-------------|
| `summary.md` | Polished answer to the user's prompt |
| `final_report.md` | Process log with rounds, decisions, deliverables |
| `logs/costs.md` | Token usage and cost breakdown |
| `compiled_v1.py` | Structured task decomposition |
| `outputs/*.py` | Individual subagent results |
| `logs/round_*.md` | Per-round validation logs |

## v2 vs v3

| Aspect | v2 (Static) | v3 (Dynamic) |
|--------|------------|--------------|
| Compilation | Re-compiles each iteration | Compiles once |
| Loop control | Merger decides ITERATE/CONVERGED | Strategist decides DONE/SPAWN_NEXT |
| Feedback | Patches applied to next compiled version | Strategist reads outputs directly |
| What re-runs | Everything re-runs each iteration | Only new tasks run each round |
| Max cycles | 3 iterations | 5 rounds (ceiling 10) |
| Validation | Merger validates + merges + decides | Validator validates, strategist decides |
