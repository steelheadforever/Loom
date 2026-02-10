# Loom Examples

Detailed walkthroughs of Loom's core capabilities, each showing full artifacts and step-by-step execution.

## Examples

### [Prompt Compilation](prompt-compilation.md)
How Loom transforms a natural language prompt into structured Python. Shows the compiled output, dependency graph, and how context accumulates across iterations. Uses a crypto CLI as the example.

### [Parallel Execution](parallel-execution.md)
How Loom orchestrates multiple subagents concurrently. Shows a security audit where 3 reviewers run in parallel at Level 1, with detailed spawn plans, execution logs, and timing comparisons.

### [Refinement Loop](refinement-loop.md)
The full 3-iteration cycle from vague prompt to validated result. Shows how each iteration discovers missing requirements, adds context, and converges. Uses a weather dashboard as the example.

## Getting Started

If you're new to Loom, start with [Prompt Compilation](prompt-compilation.md) to understand the basics, then read [Parallel Execution](parallel-execution.md) to see parallelization in action.

---

## Related Documentation

- [README.md](../README.md) - Overview and quick start
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Technical deep dive
- [DIAGRAMS.md](../DIAGRAMS.md) - Visual flowcharts
- [SKILL.md](../SKILL.md) - The skill definition
