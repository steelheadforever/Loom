# Loom - Parallel Prompt Orchestration for Claude Code

Loom compiles your prompt into a structured task graph, distributes work across parallel subagents, and iteratively refines through automated feedback loops. Each run gets its own named directory with a human-readable summary as the primary output.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Quick Start](#quick-start)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [When to Use Loom](#when-to-use-loom)
- [Example](#example)
- [Roles](#roles)
- [Project Structure](#project-structure)
- [Advanced Usage](#advanced-usage)
- [Requirements](#requirements)
- [Contributing](#contributing)

---

## Quick Start

1. **Copy the skill to your Claude Code skills directory:**
   ```bash
   # Create the skill directory
   mkdir -p ~/.claude/skills/loom/

   # Copy skill and instruction files
   cp SKILL.md ~/.claude/skills/loom/
   cp -r instructions ~/.claude/skills/loom/
   ```

2. **Invoke it:**
   ```
   /loom what are the tradeoffs between REST and GraphQL?
   ```

That's it. Loom creates a `loom/` workspace, runs the full pipeline, and presents results.

---

## Usage

Invoke with `/loom` followed by your prompt:

```
/loom build a CLI that fetches crypto prices
/loom analyze this codebase for security vulnerabilities
/loom what does AI takeoff mean for society?
```

Loom works for both **research/analysis** prompts and **build/implement** prompts.

---

## How It Works

Loom is a **thin orchestrator** -- it dispatches subagents and parses their one-line status responses. It never reads or writes data files itself. All heavy lifting happens in isolated subagent contexts.

```
SETUP   → copy instructions to workspace
COMPILE → compiler generates task graph + named run directory
SPAWN   → work subagents execute by dependency level (parallel within levels)
MERGE   → merger validates outputs, applies patches, decides: iterate or converge
REPORT  → reporter writes human-readable summary + process log
PRESENT → orchestrator shows results to user
```

The loop runs up to 3 iterations. Each iteration can refine the task graph based on what subagents discover.

### Key Design Decisions

**Compiled prompts on disk, not in context.** Your prompt is compiled into a structured Python file that subagents read from disk. This means each subagent gets minimal context overhead and multiple subagents can work in parallel.

**Instructions on disk, not in prompts.** Subagent prompts say "Read `loom/instructions/X.md`" rather than embedding instructions inline. This keeps the orchestrator's context small and instructions tamper-proof (copied fresh from the skill directory each run).

**Named run directories.** Each run gets a directory named after the prompt (e.g. `loom/ai-takeoff-analysis/`), so multiple runs coexist and you can browse past results.

**Security by design.** All subagent outputs are validated by the merger before being incorporated. Outputs must be structured data only -- no imports, no executable code, no shell commands.

---

## When to Use Loom

**Good fit:**
- Multi-step tasks that decompose into subtasks
- Research + synthesis workflows
- Tasks with independent subtasks that benefit from parallel execution
- Prompts where iterative refinement improves quality
- When you want a polished, saved summary document

**Skip Loom for:**
- Simple single-file edits or quick questions
- Purely sequential tasks with no parallelism
- Tasks where you already know exactly what you want done

---

## Example

```
/loom do you believe we are in AI takeoff? and what does that mean for all of us?
```

**What happens:**

1. **Compile** -- Generates `loom/ai-takeoff-analysis/` with a task graph: two parallel researchers (evidence + implications), then an architect to synthesize, then a reviewer
2. **Spawn Level 0** -- Two researchers run in parallel, gathering evidence and analyzing implications
3. **Spawn Level 1** -- Architect synthesizes findings into a structured analysis
4. **Spawn Level 2** -- Reviewer validates, rates quality, suggests context patches
5. **Merge** -- Applies patches, decides convergence
6. **Report** -- Writes `summary.md` (the actual answer) and `final_report.md` (process log)

**Result:**
```
loom/ai-takeoff-analysis/
  summary.md              ← human-readable answer (the main deliverable)
  final_report.md         ← process log (iterations, patches, decisions)
  compiled_v1.py          ← initial task graph
  compiled_v2.py          ← refined after merge
  outputs/                ← raw subagent outputs
  logs/                   ← iteration logs + cost breakdown
```

See [examples/](examples/) for detailed walkthroughs.

---

## Roles

Loom has 7 built-in roles, assigned by the compiler based on task requirements:

| Role | Good For | Bash Access |
|------|----------|-------------|
| **researcher** | Web research, API discovery, documentation lookup | None |
| **architect** | Design decisions, synthesis, tradeoff analysis | None |
| **coder** | Writing code, building features | Limited (test/build tools) |
| **reviewer** | Validation, code review, finding bugs | Limited (test tools) |
| **data_analyst** | Data analysis, statistics, insights | Limited (python only) |
| **documenter** | Writing docs, tutorials, READMEs | None |
| **debugger** | Fixing bugs, error analysis, troubleshooting | Limited (test/build tools) |

Bash access is restricted per role as a security measure. See [instructions/role_registry.md](instructions/role_registry.md) for details.

---

## Project Structure

After a Loom run, the workspace looks like:

```
loom/
  instructions/                  # Copied fresh each run (read-only)
    security_rules.md
    compiler.md
    subagent_guide.md
    merger.md
    reporter.md
    role_registry.md

  ai-takeoff-analysis/           # Named run directory
    summary.md                   # Human-readable answer
    final_report.md              # Process log
    compiled_v1.py               # Initial task graph
    compiled_v2.py               # After merge (with patches applied)
    spawn_plan.py                # Dependency-level spawn plan
    outputs/
      researcher_1.py            # Subagent outputs (structured data)
      researcher_2.py
      architect_1.py
      reviewer_1.py
    logs/
      iteration_1.md             # What happened this iteration
      costs.md                   # Token/cost estimates

  refactor-auth-system/          # Another run (preserved)
    summary.md
    ...
```

Multiple runs coexist under `loom/`. Each is self-contained.

---

## Advanced Usage

### Inspecting Artifacts

```bash
# Read the summary (main deliverable)
cat loom/ai-takeoff-analysis/summary.md

# See how the prompt was compiled
cat loom/ai-takeoff-analysis/compiled_v1.py

# Check what a specific subagent produced
cat loom/ai-takeoff-analysis/outputs/researcher_1.py

# Review iteration decisions
cat loom/ai-takeoff-analysis/logs/iteration_1.md
```

### Debugging Failed Runs

If a subagent fails:
1. Check the output file for `completed = False` and the `results` field for the blocker
2. Check `logs/error_*.md` for status line failures
3. Review `logs/iteration_*.md` for the merger's assessment

### Multiple Runs

Previous run directories are preserved when you start a new Loom run. Only `loom/instructions/` is refreshed.

---

## Requirements

- [Claude Code](https://github.com/anthropics/claude-code)
- No external dependencies

---

## Contributing

Contributions welcome:
- Report bugs via [GitHub Issues](https://github.com/steelheadforever/loom/issues)
- Submit feature requests
- Share examples of interesting Loom workflows
- Improve documentation

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built for the [Claude Code](https://github.com/anthropics/claude-code) community.**
