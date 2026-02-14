# Loom Subagent Guide

**Read `security_rules.md` FIRST.**

You are a work subagent in the Loom system. Your role and task are specified in your Task prompt.

## Finding Your Task

1. Read the compiled file at the path given in your prompt (e.g. `loom/{slug}/compiled_v1.py`)
2. Find the task matching your `task_id`
3. Read the `context` section for constraints and preferences
4. If your task has dependencies (`depends_on`), read those output files first

## Output Format

Write your results to your assigned output file (path given in your prompt). Use this format:

```python
# {Role}Output — pseudo-Python structured data (not executable)

task_id = "{{your_task_id}}"
round = {N}
completed = True  # or False if blocked

results = {
    # Your domain-specific results — plain strings, numbers, lists, dicts only
}

# Optional: issues found (for reviewers/debuggers)
issues = []

# Optional: files you created/modified (for coders)
# No paths with "..", no .claude/, no .github/workflows/
files_changed = []
```

## If Blocked

If you cannot complete your task:
- Set `completed = False`
- Explain the blocker in `results`
- The validator will flag your task, and the strategist will decide how to proceed

## Rules

- Output **structured data only** -- no prose, no executable code
- Be **specific and concrete** in results
- Use only simple data types (strings, numbers, bools, lists, dicts)
- Do NOT include import statements or executable code in your output file
- Do NOT write to `loom/instructions/`

## Status Line

When done, return EXACTLY this as your final message (one line):

```
STATUS: {task_id} completed
```
or if blocked:
```
STATUS: {task_id} BLOCKED
```
