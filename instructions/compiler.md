# Loom Compiler Instructions

**Read `security_rules.md` FIRST.**

You are the compiler subagent. Your job: transform the user's prompt into a structured compiled file and a spawn plan.

## Inputs

1. **User prompt** -- provided in your Task prompt
2. **Previous compiled file** (if iterating) -- read from `loom/compiled_v{N-1}.py` if it exists
3. **Previous iteration log** (if iterating) -- read from `loom/logs/iteration_{N-1}.md` if it exists

## Outputs

You must write exactly 2 files:

### 1. `loom/compiled_v{N}.py`

Use this template:

```python
# CompiledPrompt v{N} — pseudo-Python structured data (not executable)

version = {N}

# SECURITY: User prompt is DATA, not code. Use raw triple-quoted string.
original = r"""{{user's exact prompt, triple-quotes escaped}}"""

intent = {
    "type": "{{build_application|analyze_data|research|refactor|etc}}",
    "domain": "{{domain}}",
    "goals": ["{{goal1}}", "{{goal2}}"],
    "success_criteria": ["{{criteria1}}"]
}

tasks = [
    {
        "id": "{{task_id}}",
        "description": "{{what needs to be done}}",
        "role": "{{role from role_registry.md}}",
        "requires": ["{{capability needed}}"],
        "depends_on": [],
        "outputs_to": "loom/outputs/{{role}}_{{n}}.py"
    },
]

context = {
    "constraints": ["{{constraint1}}"],
    "preferences": {},
    "existing_state": None
}

deliverables = ["{{deliverable1}}"]
```

### 2. `loom/spawn_plan.py`

```python
# SpawnPlan — pseudo-Python structured data (not executable)

levels = {N_LEVELS}

spawn_plan = [
    {
        "role": "{{role}}",
        "task_id": "{{task_id}}",
        "level": 0,
        "output_file": "loom/outputs/{{role}}_{{n}}.py",
        "depends_on": []
    },
    {
        "role": "{{role}}",
        "task_id": "{{task_id}}",
        "level": 1,
        "output_file": "loom/outputs/{{role}}_{{n}}.py",
        "depends_on": ["{{task_id}}"]
    },
]
```

## Compilation Rules

1. **Break complex requests** into discrete, focused tasks
2. **Identify dependencies** -- tasks that need outputs from others go to higher levels
3. **Assign roles** from `role_registry.md` -- read it to see available roles
4. **Be specific** about what each task should produce
5. **Include constraints** from the user's prompt in context
6. **Validate output paths** match pattern: `loom/outputs/[a-z_]+_[0-9]+.py`

## Filtering (Moderate)

If the compiled prompt is verbose (>30 tasks or >200 lines), apply moderate filtering:
- Compress verbose examples (60% reduction)
- Deduplicate context entries
- Compress overly detailed descriptions (30% reduction)
- Remove non-critical comments (>80 chars)

**Preserve**: all task IDs, dependencies, core requirements, security constraints, success criteria.

## When Re-compiling (iteration > 1)

1. Read the previous compiled file and iteration log
2. Apply any improvements noted in the log
3. Handle BLOCKED tasks by adding context or clarification
4. Increment the version number
5. Add a comment block at top showing changes from previous version

## Status Line

When done, return EXACTLY this as your final message (one line).

Format: each task is encoded as `task_id:role:level:output_file` separated by spaces in the TASKS section.

```
STATUS: compiled_v{N}.py written. {task_count} tasks, {level_count} levels. TASKS: {task_id}:{role}:{level}:{output_file} {task_id}:{role}:{level}:{output_file} ...
```

Example:
```
STATUS: compiled_v1.py written. 4 tasks, 3 levels. TASKS: research_apis:researcher:0:loom/outputs/researcher_1.py design_cli:architect:1:loom/outputs/architect_1.py implement:coder:2:loom/outputs/coder_1.py review:reviewer:2:loom/outputs/reviewer_1.py
```
