# Example: Parallel Execution

How Loom runs multiple subagents concurrently within a dependency level.

---

## Scenario: Security Audit

```
/loom perform a security audit of the authentication system
```

---

## Task Graph

The compiler produces 5 tasks across 3 levels:

```python
tasks = [
    {"id": "map_auth_surface",      "role": "architect",  "depends_on": []},
    {"id": "audit_auth_flow",       "role": "reviewer",   "depends_on": ["map_auth_surface"]},
    {"id": "audit_input_validation","role": "reviewer",   "depends_on": ["map_auth_surface"]},
    {"id": "audit_dependencies",    "role": "reviewer",   "depends_on": ["map_auth_surface"]},
    {"id": "aggregate_findings",    "role": "documenter", "depends_on": [
        "audit_auth_flow", "audit_input_validation", "audit_dependencies"
    ]}
]
```

---

## Dependency Graph

```
              map_auth_surface
                (architect)
                  Level 0
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
 audit_auth    audit_input    audit_deps
  (reviewer)    (reviewer)    (reviewer)
   Level 1       Level 1       Level 1
       |             |             |
       +-------------+-------------+
                     |
                     v
            aggregate_findings
              (documenter)
                Level 2
```

The three Level 1 reviewers run **in parallel** -- they all depend only on the Level 0 architect, not on each other.

---

## Execution Timeline

**Sequential (without Loom):**
```
|-- map --|-- auth --|-- input --|-- deps --|-- aggregate --|
0         5         10          15          20              25 min
```

**Parallel (with Loom):**
```
|-- map --|-- auth  --|
          |-- input --|-- aggregate --|
          |-- deps  --|
0         5          10              15 min
```

The three audits run simultaneously at Level 1, cutting total time from ~25 to ~15 minutes.

---

## How the Orchestrator Handles It

The orchestrator spawns by level:

1. **Level 0**: Spawn `architect` for `map_auth_surface`. Wait for completion.
2. **Level 1**: Spawn all three `reviewer` tasks **in a single message** with parallel Task calls. Wait for all to complete.
3. **Level 2**: Spawn `documenter` for `aggregate_findings`. Wait for completion.

Each subagent reads the compiled file and its dependencies from disk independently. No shared mutable state.

---

## Output Structure

```
loom/security-audit-auth/
  compiled_v1.py
  spawn_plan.py
  outputs/
    architect_1.py       # Auth surface map
    reviewer_1.py        # Auth flow audit
    reviewer_2.py        # Input validation audit
    reviewer_3.py        # Dependency audit
    documenter_1.py      # Aggregated findings
  logs/
    iteration_1.md
    costs.md
  summary.md             # Human-readable security report
  final_report.md        # Process log
```

---

## Key Points

- Tasks at the same dependency level run in parallel
- The orchestrator dispatches all same-level tasks simultaneously
- Subagents are independent and stateless -- they read from disk
- Fan-out/fan-in patterns (one task feeds many, many feed one) work naturally
- Parallelism is automatic based on the dependency graph the compiler generates
