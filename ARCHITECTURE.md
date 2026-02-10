# Loom Architecture

This document provides a technical deep dive into Loom's internals, design decisions, and implementation details.

---

## Table of Contents

- [Overview](#overview)
- [Core Architecture](#core-architecture)
- [Compilation Engine](#compilation-engine)
- [Orchestration Layer](#orchestration-layer)
- [Subagent System](#subagent-system)
- [Refinement Loop](#refinement-loop)
- [State Management](#state-management)
- [Design Decisions](#design-decisions)
- [Performance Characteristics](#performance-characteristics)
- [Extending Loom](#extending-loom)

---

## Overview

Loom is a **meta-prompt system** that sits on top of Claude Code's agent capabilities. It transforms single-threaded, context-heavy prompting into a structured, parallelized, and iterative process.

### Key Innovation

**Context Efficiency Through Compilation:**

Traditional approach:
```
User Prompt (text) → Claude (reads entire context) → Response
```

Loom approach:
```
User Prompt → Compile to Python → Write to disk
            ↓
Subagent A reads compiled.py (minimal context)
Subagent B reads compiled.py (minimal context)
Subagent C reads compiled.py (minimal context)
            ↓
Results merged → Refined compiled.py → Iterate
```

By moving shared state to disk, Loom eliminates context duplication across subagents and enables true parallelization.

---

## Core Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Loom Orchestrator                    │
│  (Main Claude Code session running loom skill)          │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Compilation  │  │Orchestration │  │  Refinement  │
│   Engine     │  │    Layer     │  │     Loop     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│                    File System                          │
│  loom/compiled_v*.py, outputs/*.py, logs/*.md          │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                  Subagent Pool                          │
│  researcher | architect | coder | reviewer | ...        │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → Natural language prompt
2. **Compilation** → Structured Python representation
3. **Orchestration** → Task analysis + subagent selection
4. **Execution** → Parallel subagent spawning
5. **Collection** → Read results from outputs/
6. **Merging** → Apply patches to compiled prompt
7. **Evaluation** → Converged? Iterate? Present?
8. **Output** → Final deliverables + artifacts

---

## Compilation Engine

### Purpose

Transform ambiguous natural language into structured, parseable Python that subagents can efficiently consume.

### CompiledPrompt Schema

```python
class CompiledPrompt:
    """Structured representation of user's intent"""

    version: int                    # Iteration number
    original: str                   # User's exact prompt

    intent: dict                    # What user wants
    tasks: list[dict]               # Work breakdown
    context: dict                   # Shared knowledge
    deliverables: list[str]         # Expected outputs
```

### Intent Structure

```python
intent = {
    "type": "build_application | analyze_data | research | refactor | debug | document",
    "domain": "web | cli | data | security | ...",
    "goals": ["goal1", "goal2"],
    "success_criteria": ["measurable criterion"]
}
```

### Task Structure

```python
task = {
    "id": "unique_task_identifier",
    "description": "What needs to be done",
    "requires": ["capability1", "capability2"],  # What abilities needed
    "depends_on": ["task_id1", "task_id2"],     # Dependency graph
    "outputs_to": "loom/outputs/role_N.py"      # Where to write results
}
```

### Compilation Algorithm

```python
def compile(user_prompt: str) -> CompiledPrompt:
    # 1. Parse intent
    intent = extract_intent(user_prompt)

    # 2. Break into tasks
    tasks = decompose_into_tasks(user_prompt, intent)

    # 3. Build dependency graph
    tasks = resolve_dependencies(tasks)

    # 4. Extract constraints
    context = extract_context(user_prompt)

    # 5. Identify deliverables
    deliverables = identify_deliverables(user_prompt, tasks)

    return CompiledPrompt(
        version=1,
        original=user_prompt,
        intent=intent,
        tasks=tasks,
        context=context,
        deliverables=deliverables
    )
```

### Why Python?

- **Structured:** Easy to parse and validate
- **Version controllable:** Git-friendly format
- **Executable:** Can be imported and analyzed programmatically
- **Familiar:** Python is widely understood
- **Minimal:** No heavy dependencies

---

## Orchestration Layer

### Purpose

Analyze compiled prompt and decide:
1. Which subagents to spawn
2. In what order (dependency levels)
3. How many in parallel

### Subagent Registry

```python
REGISTRY = {
    "researcher": {
        "good_for": ["finding information", "web research", "API discovery"],
        "tools": ["web_search", "web_fetch", "read", "grep"],
        "returns": "structured data with sources"
    },
    "architect": {
        "good_for": ["design decisions", "choosing approaches", "tech stack"],
        "tools": ["read", "grep", "glob"],
        "returns": "design decisions with reasoning"
    },
    "coder": {
        "good_for": ["implementing features", "writing code"],
        "tools": ["read", "write", "edit", "bash"],
        "returns": "code files or implementations"
    },
    "reviewer": {
        "good_for": ["checking correctness", "finding bugs", "validation"],
        "tools": ["read", "bash", "grep"],
        "returns": "issues list with severity + patches"
    },
    "data_analyst": {
        "good_for": ["analyzing datasets", "statistics", "insights"],
        "tools": ["read", "bash"],
        "returns": "analysis results with visualizations"
    },
    "documenter": {
        "good_for": ["writing docs", "tutorials", "READMEs"],
        "tools": ["read", "write"],
        "returns": "documentation files"
    },
    "debugger": {
        "good_for": ["fixing broken code", "error analysis"],
        "tools": ["read", "edit", "bash"],
        "returns": "patches and fixes"
    }
}
```

### Task-to-Subagent Matching

```python
def match_subagent(task: dict) -> str:
    """Match task to appropriate subagent type"""

    requires = task["requires"]
    description = task["description"].lower()

    # Pattern matching
    if any(kw in description for kw in ["find", "research", "discover", "search"]):
        return "researcher"

    if any(kw in description for kw in ["design", "architecture", "choose", "decide"]):
        return "architect"

    if any(kw in description for kw in ["implement", "build", "create", "write code"]):
        return "coder"

    if any(kw in description for kw in ["review", "check", "validate", "test"]):
        return "reviewer"

    if any(kw in description for kw in ["analyze data", "statistics", "insights"]):
        return "data_analyst"

    if any(kw in description for kw in ["document", "tutorial", "readme"]):
        return "documenter"

    if any(kw in description for kw in ["fix", "debug", "troubleshoot"]):
        return "debugger"

    # Default: general-purpose agent
    return "general-purpose"
```

### Dependency Resolution

```python
def build_spawn_plan(compiled: CompiledPrompt) -> list[dict]:
    """Build execution plan with dependency levels"""

    # Build dependency graph
    graph = {}
    for task in compiled.tasks:
        graph[task["id"]] = {
            "task": task,
            "depends_on": task["depends_on"],
            "level": None
        }

    # Topological sort to assign levels
    level = 0
    while any(node["level"] is None for node in graph.values()):
        for task_id, node in graph.items():
            if node["level"] is not None:
                continue

            # Check if all dependencies are resolved
            deps_resolved = all(
                graph[dep]["level"] is not None
                for dep in node["depends_on"]
            )

            if not node["depends_on"] or deps_resolved:
                node["level"] = level

        level += 1

    # Build spawn plan
    spawn_plan = []
    for task_id, node in graph.items():
        spawn_plan.append({
            "role": match_subagent(node["task"]),
            "task_id": task_id,
            "level": node["level"],
            "output_file": node["task"]["outputs_to"]
        })

    return sorted(spawn_plan, key=lambda x: x["level"])
```

### Parallelization Strategy

```python
def spawn_by_level(spawn_plan: list[dict]):
    """Spawn subagents level by level"""

    max_level = max(agent["level"] for agent in spawn_plan)

    for level in range(max_level + 1):
        # Get all agents at this level
        agents_at_level = [
            agent for agent in spawn_plan
            if agent["level"] == level
        ]

        # Spawn all in parallel
        task_ids = []
        for agent in agents_at_level:
            task_id = spawn_subagent(agent)
            task_ids.append(task_id)

        # Wait for all to complete
        wait_for_completion(task_ids)
```

---

## Subagent System

### Subagent Lifecycle

```
1. Spawn → Task tool called with specialized prompt
2. Read → Subagent reads loom/compiled_v*.py
3. Execute → Subagent performs its task
4. Write → Results written to loom/outputs/*.py
5. Terminate → Control returns to orchestrator
```

### Subagent Prompt Template

Each subagent receives:

```
You are a {{ROLE}} subagent in the Loom system.

YOUR ASSIGNMENT:
1. Read your task from: loom/compiled_v{{N}}.py
   - Look for task_id: "{{TASK_ID}}"
   - Read the full context section
   - Check dependencies: {{DEPENDS_ON}}

2. If dependencies exist, read their outputs first

3. Execute your task: {{TASK_DESCRIPTION}}

4. Write results to: {{OUTPUT_FILE}}

OUTPUT FORMAT (must be valid Python):
[See output schema below]

CRITICAL RULES:
- Return ONLY Python code, no prose
- Be specific and concrete in results
- If blocked, set completed=False
- Use prompt_patches to suggest improvements
```

### Subagent Output Schema

```python
class SubagentOutput:
    """Standard output format for all subagents"""

    task_id: str                    # Which task this completes
    iteration: int                  # Which loom iteration
    completed: bool                 # Success/failure

    results: dict                   # Domain-specific results
    prompt_patches: list[dict]      # Suggested improvements
    issues: list[dict]              # Problems found (optional)
    files_changed: list[str]        # Files modified (optional)
```

### Prompt Patches

Subagents can suggest improvements to the compiled prompt:

```python
prompt_patches = [
    {
        "action": "add_context",
        "key": "api_choice",
        "value": "CoinGecko"
    },
    {
        "action": "update_task",
        "task_id": "implement_backend",
        "field": "description",
        "new_value": "Implement backend using CoinGecko API"
    },
    {
        "action": "add_task",
        "task": {
            "id": "write_tests",
            "description": "Write unit tests for API integration",
            "requires": ["testing"],
            "depends_on": ["implement_backend"]
        }
    },
    {
        "action": "remove_task",
        "task_id": "obsolete_task"
    }
]
```

---

## Refinement Loop

### Purpose

Iteratively improve the compiled prompt based on subagent feedback.

### Loop Algorithm

```python
def refinement_loop(initial_prompt: str, max_iterations=3):
    # Initialize
    compiled = compile(initial_prompt)
    write_file("loom/compiled_v1.py", compiled)

    for iteration in range(1, max_iterations + 1):
        # Orchestrate
        spawn_plan = build_spawn_plan(compiled)

        # Execute
        spawn_by_level(spawn_plan)

        # Collect
        outputs = collect_outputs(spawn_plan)

        # Check for issues
        if any(not output.completed for output in outputs):
            handle_failures(outputs)

        # Extract patches
        all_patches = []
        for output in outputs:
            all_patches.extend(output.prompt_patches)

        # Apply patches
        if all_patches:
            compiled = apply_patches(compiled, all_patches)
            compiled.version = iteration + 1
            write_file(f"loom/compiled_v{iteration+1}.py", compiled)
        else:
            # No improvements suggested - converged
            break

        # Log iteration
        log_iteration(iteration, compiled, outputs, all_patches)

    # Present results
    present_results(compiled, outputs)
```

### Convergence Detection

```python
def has_converged(prev_compiled, curr_compiled) -> bool:
    """Check if prompt has stabilized"""

    # No patches applied
    if prev_compiled == curr_compiled:
        return True

    # All tasks completed, no new tasks added
    if (len(curr_compiled.tasks) == len(prev_compiled.tasks) and
        all(task in prev_compiled.tasks for task in curr_compiled.tasks)):
        return True

    return False
```

### Patch Application

```python
def apply_patches(compiled: CompiledPrompt, patches: list[dict]) -> CompiledPrompt:
    """Apply subagent patches to compiled prompt"""

    for patch in patches:
        action = patch["action"]

        if action == "add_context":
            compiled.context[patch["key"]] = patch["value"]

        elif action == "update_task":
            task = find_task(compiled, patch["task_id"])
            task[patch["field"]] = patch["new_value"]

        elif action == "add_task":
            compiled.tasks.append(patch["task"])

        elif action == "remove_task":
            compiled.tasks = [
                t for t in compiled.tasks
                if t["id"] != patch["task_id"]
            ]

        elif action == "update_intent":
            compiled.intent.update(patch["updates"])

    return compiled
```

---

## State Management

### File-Based State

All state lives on disk, not in context:

```
loom/
├── compiled_v1.py       # Version 1 of compiled prompt
├── compiled_v2.py       # Version 2 (with patches)
├── compiled_v3.py       # Version 3
├── compiled_final.py    # Copy of best version
│
├── outputs/
│   ├── researcher_1.py  # Subagent results
│   ├── architect_1.py
│   └── coder_1.py
│
└── logs/
    ├── iteration_1.md   # Human-readable logs
    ├── iteration_2.md
    └── iteration_3.md
```

### Benefits

1. **Zero Context Overhead:** Subagents read compiled state directly from disk
2. **Parallelization:** Multiple subagents can read same file simultaneously
3. **Debugging:** All artifacts available for inspection
4. **Version Control:** Entire refinement process can be committed to git
5. **Resumability:** Can continue from any iteration

### State Transitions

```
Initial State: loom/ doesn't exist
     ↓
COMPILE: loom/compiled_v1.py created
     ↓
SPAWN: Multiple subagents read compiled_v1.py
     ↓
COLLECT: Read loom/outputs/*.py
     ↓
MERGE: loom/compiled_v2.py created
     ↓
ITERATE: Repeat with v2
```

---

## Design Decisions

### Why Python for Compiled Prompts?

**Considered alternatives:**
- JSON: Less expressive, no comments, harder to read
- YAML: Too flexible, parsing ambiguity
- Custom DSL: Learning curve, tooling overhead
- Markdown: Not structured enough

**Why Python won:**
- Universally understood by developers
- Native support for comments and documentation
- Can be imported and analyzed programmatically
- Version control friendly
- Balance of human-readable and machine-parseable

### Why File-Based State?

**Considered alternatives:**
- In-context state: Context window limits, expensive
- Database: Overkill, dependencies, complexity
- Message passing: Race conditions, harder to debug

**Why files won:**
- Simple, no dependencies
- Debuggable (just cat the file)
- Version controllable
- Enables parallelization
- Zero context overhead

### Why Up to 3 Iterations?

**Considered alternatives:**
- Fixed 1 iteration: Misses refinement opportunities
- Unlimited iterations: Can loop forever, expensive
- User-configurable: Added complexity

**Why 3 iterations:**
- Empirically sufficient (v1=rough, v2=good, v3=polished)
- Bounded cost
- Forces convergence thinking
- Can exit early if converged

### Why Specialized Subagents?

**Considered alternatives:**
- Single general-purpose agent: Lacks specialization benefits
- User-defined agents: Requires configuration, steep learning curve
- Dynamic agent generation: Expensive, unpredictable

**Why specialized agents:**
- Clear capabilities and tool access
- Predictable behavior
- Easier to reason about
- Can be optimized per role
- Balance of flexibility and structure

---

## Performance Characteristics

### Time Complexity

**Sequential execution (no loom):**
```
Time = Task1 + Task2 + Task3 + ... + TaskN
```

**Loom (parallel execution):**
```
Time = max(Level0_tasks) + max(Level1_tasks) + ... + max(LevelK_tasks) + Overhead
```

Where `Overhead = compilation + orchestration + merging ≈ 10-20 seconds`

### Space Complexity

- **Compiled prompts:** O(N) where N = number of tasks
- **Subagent outputs:** O(M) where M = number of subagents
- **Total disk usage:** Typically < 1MB per session

### Context Usage

- **Orchestrator:** Fixed context (skill instructions)
- **Each subagent:** O(1) - reads only compiled.py, not full history
- **Total context saved:** O(N × M) where N=subagents, M=context size

**Savings:** 3-10x context reduction vs. sequential execution

### Real-World Performance

**Example: Build CLI application**
- Sequential: ~5 minutes (research → design → code → review)
- Loom (parallel): ~2 minutes (research + design in parallel, then code + review)
- **Speedup: 2.5x**

**Example: Security audit (3 parallel reviewers)**
- Sequential: ~15 minutes
- Loom (parallel): ~5 minutes
- **Speedup: 3x**

---

## Extending Loom

### Adding Custom Subagent Types

Edit the REGISTRY in orchestration layer:

```python
REGISTRY["performance_optimizer"] = {
    "good_for": ["profiling", "optimization", "benchmarking"],
    "tools": ["read", "bash", "grep"],
    "returns": "performance analysis with recommendations"
}
```

Update pattern matching:

```python
if any(kw in description for kw in ["optimize", "performance", "profile"]):
    return "performance_optimizer"
```

### Custom Compilation Templates

Create domain-specific CompiledPrompt subclasses:

```python
class DataAnalysisPrompt(CompiledPrompt):
    """Specialized for data analysis tasks"""

    dataset_info: dict      # Dataset metadata
    analysis_type: str      # Type of analysis
    visualization_needs: list[str]
```

### Custom Patch Actions

Extend patch application logic:

```python
elif action == "update_dataset_info":
    compiled.dataset_info.update(patch["updates"])
```

### Integration with External Systems

Subagents can integrate with external tools:

```python
class DeployerOutput:
    """Subagent that deploys code"""

    results = {
        "deployment_url": "https://...",
        "deployment_logs": "...",
        "status": "success"
    }
```

---

## Debugging and Introspection

### Viewing Compilation

```bash
cat loom/compiled_v1.py
```

### Tracking Evolution

```bash
diff loom/compiled_v1.py loom/compiled_v2.py
```

### Inspecting Subagent Outputs

```bash
cat loom/outputs/researcher_1.py
cat loom/outputs/coder_1.py
```

### Reading Iteration Logs

```bash
cat loom/logs/iteration_1.md
```

### Common Issues

**Subagent failed:**
- Check `loom/outputs/{{role}}_{{N}}.py` for `completed = False`
- Read `issues` list for error details

**Compilation seems wrong:**
- Review `loom/compiled_v1.py` intent and tasks
- Iteration 2 should improve based on subagent feedback

**Infinite loop:**
- Check if patches are creating new tasks endlessly
- Review convergence logic

---

## Future Enhancements

Potential improvements for future versions:

1. **Dynamic iteration limits** based on task complexity
2. **Subagent result caching** to avoid redundant work
3. **Parallel iteration** (multiple refinement branches)
4. **Cost tracking** and optimization
5. **Visual dashboards** for loom sessions
6. **Prompt library** for common task patterns
7. **Automated subagent generation** based on task analysis
8. **Integration with CI/CD** pipelines
9. **Telemetry and analytics** for optimization
10. **Multi-project loom** (cross-project coordination)

---

## Conclusion

Loom's architecture prioritizes:
- **Efficiency:** Minimal context overhead through file-based state
- **Parallelization:** Aggressive concurrent execution
- **Iterative refinement:** Automated improvement loops
- **Debuggability:** All artifacts saved for inspection
- **Simplicity:** No external dependencies, pure Claude Code

The result is a meta-prompt system that transforms complex tasks from single-threaded, context-heavy operations into structured, parallelized, self-refining programs.

---

**Questions or ideas for improvements?** Open an issue or discussion on GitHub!
