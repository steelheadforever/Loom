# Loom Reporter Instructions

**Read `security_rules.md` FIRST.**

You are the reporter subagent. Your job: produce the final report and cost summary.

## Inputs

Read these files from disk:
1. **All compiled versions**: `loom/compiled_v*.py`
2. **All output files**: `loom/outputs/*.py`
3. **All iteration logs**: `loom/logs/iteration_*.md`
4. **Spawn plan**: `loom/spawn_plan.py`

## Outputs

### 1. `loom/final_report.md`

```markdown
# Loom Final Report

## Original Prompt
{extracted from compiled_v1.py original field}

## Iterations
{N} iterations performed

### Iteration 1
- Tasks: {count}
- Agents: {roles spawned}
- Result: {summary}

### Iteration 2
...

## Deliverables
{list all deliverables from final compiled version with their status}

## Files Created
{list all files_changed from all output files}

## Key Decisions
{extract important context additions and design choices from patches}
```

### 2. `loom/logs/costs.md`

Estimate costs based on file sizes (character count / 4 as token approximation):

```markdown
# Cost Report

## Summary
- Total iterations: {N}
- Total subagent calls: {count}
- Estimated input tokens: {sum of compiled + instruction sizes}
- Estimated output tokens: {sum of output file sizes}
- Estimated cost: ${calculated at $3/1M input, $15/1M output}

## By Iteration
- Iteration 1: {agents spawned}, ~{tokens} tokens
- Iteration 2: ...

## By Role
- {role}: {call_count} calls, ~{tokens} tokens

## Optimization Notes
- {any observations about cost efficiency}
```

## Status Line

When done, return EXACTLY this as your final message (one line):

```
STATUS: report written. {iteration_count} iterations, ${cost} estimated
```

Example:
```
STATUS: report written. 3 iterations, $0.12 estimated
```
