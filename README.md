# Loom - Recursive Prompt Refinement for Claude Code

Complex tasks in Claude Code run slowly because they execute sequentially and consume large context windows. Loom fixes this by compiling your prompt into structured Python, distributing work across parallel subagents, and iteratively refining through automated feedback loops.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Quick Start](#quick-start)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [When to Use Loom](#when-to-use-loom)
- [Example](#example)
- [Subagent Types](#subagent-types)
- [Advanced Usage](#advanced-usage)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [Learn More](#learn-more)

---

## Quick Start

1. **Copy the skill file to your Claude Code skills directory:**
   ```bash
   # Global installation (available in all projects)
   cp SKILL.md ~/.claude/skills/loom.md

   # OR: Project-specific installation
   mkdir -p .claude/skills
   cp SKILL.md .claude/skills/loom.md
   ```

2. **Reload skills in Claude Code:**
   ```
   /skills reload
   ```

3. **Verify installation:**
   ```
   /skills list
   ```
   You should see `loom` in the available skills list.

---

## Usage

### Basic Invocation

Invoke loom using the `/loom` command followed by your prompt:

```bash
/loom build a CLI that fetches crypto prices
```

Or ask Claude to use loom:

```
Use loom to analyze this codebase for security vulnerabilities
```

### What Happens Next

1. Loom creates a `loom/` workspace
2. Compiles your prompt into structured Python with tasks, intent, and context
3. Spawns specialized subagents in parallel to execute tasks
4. Collects results and applies improvements
5. Iterates up to 3 times for refinement
6. Presents final results with all artifacts saved

---

## How It Works

Loom follows a 7-step process. See [DIAGRAMS.md](DIAGRAMS.md) for visual flowcharts.

1. **COMPILE** - Transform natural language into structured Python
2. **ANALYZE** - Extract tasks and build dependency graph
3. **ORCHESTRATE** - Match tasks to specialized subagent types
4. **SPAWN** - Launch subagents in parallel (by dependency level)
5. **EXECUTE** - Subagents read compiled state and perform work
6. **COLLECT** - Gather results and check for issues
7. **MERGE** - Apply patches to create next iteration

Then evaluate: if improvements were found, iterate with the refined prompt. If converged or max iterations reached, present final results.

### Key Idea: Context Efficiency Through Compilation

Instead of passing your full prompt to every subagent (expensive, sequential), Loom compiles it to a structured Python file on disk. Each subagent reads only the compiled file -- minimal context, parallel execution. This significantly reduces token usage and enables concurrent work.

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed technical explanation of this approach.

---

## When to Use Loom

**Use Loom when:**
- Complex multi-step tasks that can be broken into subtasks
- Research + implementation workflows (find info, design, build, test)
- Parallel execution would speed things up (independent tasks)
- Iterative refinement would improve quality
- You want artifacts saved for inspection and debugging

**Skip Loom for:**
- Simple one-shot prompts (single file edits, basic queries)
- Purely sequential tasks that can't be parallelized
- Quick throwaway questions or clarifications
- Already well-defined prompts that don't need refinement

---

## Example

**Input:**
```bash
/loom build a CLI that fetches current crypto prices and displays them
```

**Iteration 1 (Discovery):**
- Compiles prompt with 4 tasks: research_apis, design_cli, implement, test
- Spawns researcher -- discovers CoinGecko API is best option
- Patches compiled prompt with API details

**Iteration 2 (Implementation):**
- Recompiles with API context
- Spawns architect (designs CLI structure) and coder (implements it) in parallel
- Produces working `crypto_cli.py` + `requirements.txt`

**Iteration 3 (Validation):**
- Spawns reviewer -- finds missing error handling
- Spawns debugger + coder to fix edge cases
- All tests pass

**Result:** Working CLI with all research, design, and review artifacts saved in `loom/`.

For detailed walkthroughs with full artifacts, see [examples/](examples/).

---

## Subagent Types

Loom has 7 built-in subagent types, automatically selected based on task requirements:

| Type | Good For | Returns |
|------|----------|---------|
| **researcher** | Finding information, web research, API discovery | Structured data with sources |
| **architect** | Design decisions, choosing approaches, tech stack | Design decisions with reasoning |
| **coder** | Implementing features, writing code | Code files or implementations |
| **reviewer** | Checking correctness, finding bugs, validation | Issues list with severity + patches |
| **data_analyst** | Analyzing datasets, statistics, insights | Analysis results with visualizations |
| **documenter** | Writing docs, tutorials, READMEs | Documentation files |
| **debugger** | Fixing broken code, error analysis | Patches and fixes |

Loom can also create **custom subagents** on-the-fly for specialized tasks not covered by built-in types. See [SKILL.md](SKILL.md) for the full subagent registry and prompt templates.

---

## Advanced Usage

### Continuing from Previous State

If a `loom/` directory exists from a previous run, Loom will ask whether to clean and start fresh or continue from the previous iteration.

### Inspecting Artifacts

All loom artifacts are saved for inspection:

```bash
# View compiled prompt evolution
cat loom/compiled_v1.py
cat loom/compiled_v2.py

# View subagent outputs
cat loom/outputs/researcher_1.py

# Read iteration logs
cat loom/logs/iteration_1.md
```

### Debugging Failed Runs

If a subagent fails:
1. Check `loom/outputs/<role>_<N>.py` for `completed = False`
2. Read the `issues` list for blocking problems
3. Review `loom/logs/iteration_<N>.md` for the detailed log

---

## Project Structure

After a loom session, you'll have:

```
loom/
  compiled_v1.py           # Initial compilation
  compiled_v2.py           # After iteration 1
  compiled_v3.py           # After iteration 2 (if needed)
  compiled_final.py        # Copy of best version

  outputs/
    researcher_1.py        # Subagent outputs
    architect_1.py
    coder_1.py
    reviewer_1.py

  logs/
    iteration_1.md         # Detailed iteration logs
    iteration_2.md
    iteration_3.md
```

---

## Requirements

- [Claude Code](https://github.com/anthropics/claude-code) (latest version recommended)
- No external dependencies required
- Works with all Claude models (Sonnet/Opus recommended for best results)

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ways to contribute:
- Report bugs via [GitHub Issues](https://github.com/steelheadforever/loom/issues)
- Submit feature requests for new subagent types or capabilities
- Share examples of interesting loom workflows
- Improve documentation with clarifications or examples

---

## Learn More

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical deep dive into compilation, orchestration, and design decisions
- **[DIAGRAMS.md](DIAGRAMS.md)** - Visual flowcharts and diagrams of the Loom process
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute, issue templates, PR process
- **[SKILL.md](SKILL.md)** - The skill definition itself (subagent registry, prompt templates, patch system)
- **[examples/](examples/)** - Detailed worked examples with full artifacts
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and planned features

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built for the [Claude Code](https://github.com/anthropics/claude-code) community.**
