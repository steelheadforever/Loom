# Example: Parallel Subagent Execution

This example demonstrates how Loom orchestrates multiple subagents in parallel to significantly speed up execution.

---

## Scenario: Security Audit

**Input:**
```
/loom perform comprehensive security audit of the authentication system
```

---

## Compiled Prompt Analysis

### Tasks with Dependencies

```python
tasks = [
    {
        "id": "map_auth_surface",
        "description": "Identify all authentication-related files and entry points",
        "requires": ["code_analysis"],
        "depends_on": [],  # Level 0
        "outputs_to": "loom/outputs/architect_1.py"
    },
    {
        "id": "audit_auth_flow",
        "description": "Review authentication flow logic for vulnerabilities",
        "requires": ["security_review"],
        "depends_on": ["map_auth_surface"],  # Level 1
        "outputs_to": "loom/outputs/reviewer_1.py"
    },
    {
        "id": "audit_input_validation",
        "description": "Check all input validation in auth endpoints",
        "requires": ["security_review"],
        "depends_on": ["map_auth_surface"],  # Level 1 (parallel with audit_auth_flow)
        "outputs_to": "loom/outputs/reviewer_2.py"
    },
    {
        "id": "audit_dependencies",
        "description": "Scan authentication dependencies for known vulnerabilities",
        "requires": ["security_review"],
        "depends_on": ["map_auth_surface"],  # Level 1 (parallel with others)
        "outputs_to": "loom/outputs/reviewer_3.py"
    },
    {
        "id": "aggregate_findings",
        "description": "Compile all findings into comprehensive security report",
        "requires": ["reporting"],
        "depends_on": ["audit_auth_flow", "audit_input_validation", "audit_dependencies"],  # Level 2
        "outputs_to": "loom/outputs/documenter_1.py"
    }
]
```

---

## Dependency Graph

```
                  map_auth_surface
                   (architect_1)
                    Level 0
                        |
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
audit_auth_flow  audit_input      audit_dependencies
  (reviewer_1)   validation          (reviewer_3)
                (reviewer_2)
    Level 1         Level 1           Level 1
    (parallel)     (parallel)        (parallel)
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ▼
                aggregate_findings
                  (documenter_1)
                     Level 2
```

---

## Execution Timeline

### Sequential Execution (Traditional)

```
Time: 0min          5min         10min        15min        20min
      |------------|------------|------------|------------|
      map_auth     audit_auth   audit_input  audit_deps   aggregate
      (5 min)      (5 min)      (5 min)      (5 min)      (5 min)

Total: 25 minutes
```

### Parallel Execution (Loom)

```
Time: 0min          5min         10min        15min
      |------------|------------|------------|
      map_auth     ┌─ audit_auth ─┐
      (5 min)      ├─ audit_input ─┤  aggregate
                   └─ audit_deps ──┘  (5 min)
                   (5 min, parallel)

Total: 15 minutes
Speedup: 1.67x
```

---

## Spawn Plan

```python
spawn_plan = [
    {
        "role": "architect",
        "task_id": "map_auth_surface",
        "level": 0,
        "output_file": "loom/outputs/architect_1.py"
    },
    {
        "role": "reviewer",
        "task_id": "audit_auth_flow",
        "level": 1,
        "output_file": "loom/outputs/reviewer_1.py"
    },
    {
        "role": "reviewer",
        "task_id": "audit_input_validation",
        "level": 1,
        "output_file": "loom/outputs/reviewer_2.py"
    },
    {
        "role": "reviewer",
        "task_id": "audit_dependencies",
        "level": 1,
        "output_file": "loom/outputs/reviewer_3.py"
    },
    {
        "role": "documenter",
        "task_id": "aggregate_findings",
        "level": 2,
        "output_file": "loom/outputs/documenter_1.py"
    }
]
```

---

## Detailed Execution Log

### Level 0: Map Attack Surface

**Time: 0:00 - 5:00**

```
[Loom] Spawning Level 0 agents...
[Loom] → architect_1 (map_auth_surface)

[architect_1] Reading: loom/compiled_v1.py
[architect_1] Analyzing codebase...
[architect_1] Found auth files: auth.py, middleware.py, session.py, validators.py
[architect_1] Entry points: /login, /logout, /register, /reset-password
[architect_1] Writing: loom/outputs/architect_1.py
[architect_1] ✓ Complete

[Loom] Level 0 complete. Proceeding to Level 1...
```

**Output:** `loom/outputs/architect_1.py`
```python
class ArchitectOutput:
    task_id = "map_auth_surface"
    iteration = 1
    completed = True

    results = {
        "auth_files": [
            "src/auth/auth.py",
            "src/auth/middleware.py",
            "src/auth/session.py",
            "src/auth/validators.py"
        ],
        "entry_points": [
            {"path": "/login", "method": "POST", "file": "auth.py"},
            {"path": "/logout", "method": "POST", "file": "auth.py"},
            {"path": "/register", "method": "POST", "file": "auth.py"},
            {"path": "/reset-password", "method": "POST", "file": "auth.py"}
        ],
        "external_deps": [
            "bcrypt",
            "PyJWT",
            "cryptography"
        ]
    }

    prompt_patches = [
        {
            "action": "add_context",
            "key": "auth_surface_map",
            "value": {
                "files": 4,
                "endpoints": 4,
                "dependencies": 3
            }
        }
    ]
```

---

### Level 1: Parallel Security Reviews

**Time: 5:00 - 10:00**

```
[Loom] Spawning Level 1 agents in parallel...
[Loom] → reviewer_1 (audit_auth_flow)
[Loom] → reviewer_2 (audit_input_validation)
[Loom] → reviewer_3 (audit_dependencies)

[reviewer_1] Reading: loom/compiled_v1.py
[reviewer_1] Reading dependency: loom/outputs/architect_1.py
[reviewer_1] Auditing authentication flow...

[reviewer_2] Reading: loom/compiled_v1.py
[reviewer_2] Reading dependency: loom/outputs/architect_1.py
[reviewer_2] Checking input validation...

[reviewer_3] Reading: loom/compiled_v1.py
[reviewer_3] Reading dependency: loom/outputs/architect_1.py
[reviewer_3] Scanning dependencies...

[reviewer_1] Found 3 issues in auth flow
[reviewer_1] Writing: loom/outputs/reviewer_1.py
[reviewer_1] ✓ Complete

[reviewer_2] Found 5 issues in input validation
[reviewer_2] Writing: loom/outputs/reviewer_2.py
[reviewer_2] ✓ Complete

[reviewer_3] Found 4 issues in dependencies
[reviewer_3] Writing: loom/outputs/reviewer_3.py
[reviewer_3] ✓ Complete

[Loom] Level 1 complete (3 agents in 5 minutes). Proceeding to Level 2...
```

**Key Insight:** All 3 reviewers ran **simultaneously** because they had no dependencies on each other. Sequential execution would take 15 minutes; parallel took only 5.

---

### Level 2: Aggregate Findings

**Time: 10:00 - 15:00**

```
[Loom] Spawning Level 2 agents...
[Loom] → documenter_1 (aggregate_findings)

[documenter_1] Reading: loom/compiled_v1.py
[documenter_1] Reading dependencies:
[documenter_1]   - loom/outputs/reviewer_1.py
[documenter_1]   - loom/outputs/reviewer_2.py
[documenter_1]   - loom/outputs/reviewer_3.py
[documenter_1] Compiling security report...
[documenter_1] Total findings: 12 (3 critical, 5 medium, 4 low)
[documenter_1] Writing: loom/outputs/documenter_1.py
[documenter_1] ✓ Complete

[Loom] All levels complete!
```

---

## Final Results

### Findings Summary

```
🔒 SECURITY AUDIT RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Issues Found: 12
- 🔴 Critical: 3
- 🟠 Medium: 5
- 🟡 Low: 4

Breakdown by Area:
- Auth Flow: 3 issues
- Input Validation: 5 issues
- Dependencies: 4 issues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Execution Time: 15 minutes
Sequential Time Would Be: 25 minutes
Speedup: 1.67x
```

### Artifacts Generated

```
loom/
├── compiled_v1.py
├── outputs/
│   ├── architect_1.py    (auth surface map)
│   ├── reviewer_1.py     (auth flow audit)
│   ├── reviewer_2.py     (input validation audit)
│   ├── reviewer_3.py     (dependency audit)
│   └── documenter_1.py   (final report)
└── logs/
    └── iteration_1.md
```

---

## Parallelization Benefits

### Time Savings

```
Sequential: 5 + 5 + 5 + 5 + 5 = 25 minutes
Parallel:   5 + max(5,5,5) + 5 = 15 minutes
Savings:    10 minutes (40% faster)
```

### Context Efficiency

**Sequential (traditional):**
```
Total context = 5 subagents × full prompt context
              = significant token usage
```

**Parallel (Loom):**
```
Total context = 5 subagents × compiled.py size
              = minimal token usage
All read from disk, no context duplication
```

### Scalability

More parallel tasks = even better speedup:

```
3 parallel tasks at level 1: 1.67x speedup
5 parallel tasks at level 1: 2.5x speedup
10 parallel tasks at level 1: 4x speedup
```

---

## Key Takeaways

1. **Dependency-aware scheduling** enables intelligent parallelization
2. **Level-based execution** maximizes concurrency while respecting dependencies
3. **File-based state** allows multiple subagents to read compiled prompt simultaneously
4. **Real-world speedups** of 1.5x - 3x are common
5. **No coordination overhead** - subagents are independent and stateless

---

## When Parallelization Works Best

✅ **Great for:**
- Multiple independent analyses (security reviews, code audits)
- Research tasks that can be split (API comparison, literature review)
- Testing multiple approaches (A/B testing, experiments)
- Fan-out/fan-in patterns (gather data → process → aggregate)

❌ **Limited for:**
- Purely sequential pipelines (step 1 → step 2 → step 3)
- Tasks with shared mutable state
- Very short tasks (overhead > benefit)

---

## Try It Yourself

Create a prompt with parallelizable tasks:

```bash
/loom analyze the codebase for:
1. Security vulnerabilities
2. Performance bottlenecks
3. Code quality issues
4. Documentation gaps

Then create a comprehensive report.
```

Watch Loom spawn 4 parallel reviewers at Level 1, then aggregate at Level 2!

Check execution timeline:
```bash
cat loom/logs/iteration_1.md
```

---

**Parallel execution is one of Loom's superpowers. Use it to speed up complex, multi-faceted tasks!**
