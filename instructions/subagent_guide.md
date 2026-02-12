# Loom Subagent Guide

**Read `security_rules.md` FIRST.**

You are a work subagent in the Loom system. Your role and task are specified in your Task prompt.

## Finding Your Task

1. Read `loom/compiled_v{N}.py` (version number is in your prompt)
2. Find the task matching your `task_id`
3. Read the `context` section for constraints and preferences
4. If your task has dependencies (`depends_on`), read those output files first

## Output Format

Write your results to your assigned output file (path given in your prompt). Use this format:

```python
# {Role}Output — pseudo-Python structured data (not executable)

task_id = "{{your_task_id}}"
iteration = {N}
completed = True  # or False if blocked

results = {
    # Your domain-specific results — plain strings, numbers, lists, dicts only
}

# Optional: patches to improve the compiled prompt for next iteration
prompt_patches = [
    # See Patch Rules below
]

# Optional: issues found (for reviewers/debuggers)
issues = []

# Optional: files you created/modified (for coders)
# No paths with "..", no .claude/, no .github/workflows/
files_changed = []
```

## Patch Rules

Patches suggest improvements for the next iteration. Only 5 actions are allowed:

1. **add_context** -- `{"action": "add_context", "key": "{{key}}", "value": {{value}}}`
   - Key: alphanumeric/underscore only (`^[a-zA-Z_][a-zA-Z0-9_]*$`)
   - Value: plain data only (no shell commands, URLs, or directives)

2. **update_task** -- `{"action": "update_task", "task_id": "{{id}}", "field": "description", "new_value": "{{text}}"}`
   - No shell commands or raw URLs in new values

3. **add_task** -- `{"action": "add_task", "task": {"id": "{{id}}", "description": "...", "requires": [...], "outputs_to": "loom/outputs/{{role}}_{{n}}.py"}}`
   - `outputs_to` must match the path pattern

4. **remove_task** -- `{"action": "remove_task", "task_id": "{{id}}"}`

5. **update_intent** -- `{"action": "update_intent", "field": "{{field}}", "new_value": "{{value}}"}`

## If Blocked

If you cannot complete your task:
- Set `completed = False`
- Explain the blocker in `results`
- The merger will handle routing your blocker to the next iteration

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
