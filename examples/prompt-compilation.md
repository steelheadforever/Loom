# Example: Prompt Compilation

How Loom transforms a natural language prompt into a structured task graph on disk.

---

## Input

```
/loom build a CLI that fetches current crypto prices from an API and displays them in a table
```

---

## What the Compiler Produces

The compiler generates a kebab-case slug from the prompt (`crypto-price-cli`), creates the run directory, and writes two files.

### `loom/crypto-price-cli/compiled_v1.py`

```python
# CompiledPrompt v1 — pseudo-Python structured data (not executable)

version = 1
run_dir = "loom/crypto-price-cli"

original = r"""build a CLI that fetches current crypto prices from an API and displays them in a table"""

intent = {
    "type": "build_application",
    "domain": "cli",
    "goals": [
        "Fetch cryptocurrency prices from API",
        "Display prices in formatted table",
        "Make it executable as command-line tool"
    ],
    "success_criteria": [
        "CLI runs without errors",
        "Prices are current and accurate",
        "Table formatting is readable"
    ]
}

tasks = [
    {
        "id": "research_apis",
        "description": "Find suitable cryptocurrency price APIs (free, reliable)",
        "role": "researcher",
        "requires": ["web_search"],
        "depends_on": [],
        "outputs_to": "loom/crypto-price-cli/outputs/researcher_1.py"
    },
    {
        "id": "design_cli",
        "description": "Design CLI architecture: argument parsing, API client, table formatter",
        "role": "architect",
        "requires": ["design"],
        "depends_on": ["research_apis"],
        "outputs_to": "loom/crypto-price-cli/outputs/architect_1.py"
    },
    {
        "id": "implement_cli",
        "description": "Implement the CLI tool with API integration and table display",
        "role": "coder",
        "requires": ["python"],
        "depends_on": ["design_cli"],
        "outputs_to": "loom/crypto-price-cli/outputs/coder_1.py"
    },
    {
        "id": "review_cli",
        "description": "Test CLI functionality, check error handling, validate output",
        "role": "reviewer",
        "requires": ["testing"],
        "depends_on": ["implement_cli"],
        "outputs_to": "loom/crypto-price-cli/outputs/reviewer_1.py"
    }
]

context = {
    "constraints": [
        "Use Python for implementation",
        "Free API preferred (no API key if possible)",
        "Handle API errors gracefully"
    ],
    "preferences": {},
    "existing_state": None
}

deliverables = [
    "Working CLI script",
    "requirements.txt with dependencies"
]
```

### `loom/crypto-price-cli/spawn_plan.py`

```python
# SpawnPlan — pseudo-Python structured data (not executable)

run_dir = "loom/crypto-price-cli"
levels = 4

spawn_plan = [
    {"role": "researcher", "task_id": "research_apis", "level": 0,
     "output_file": "loom/crypto-price-cli/outputs/researcher_1.py", "depends_on": []},
    {"role": "architect", "task_id": "design_cli", "level": 1,
     "output_file": "loom/crypto-price-cli/outputs/architect_1.py", "depends_on": ["research_apis"]},
    {"role": "coder", "task_id": "implement_cli", "level": 2,
     "output_file": "loom/crypto-price-cli/outputs/coder_1.py", "depends_on": ["design_cli"]},
    {"role": "reviewer", "task_id": "review_cli", "level": 3,
     "output_file": "loom/crypto-price-cli/outputs/reviewer_1.py", "depends_on": ["implement_cli"]}
]
```

---

## Dependency Graph

```
research_apis     (Level 0 — researcher)
      |
design_cli        (Level 1 — architect)
      |
implement_cli     (Level 2 — coder)
      |
review_cli        (Level 3 — reviewer)
```

This is a sequential pipeline -- each task depends on the previous. For a parallel example, see [Parallel Execution](parallel-execution.md).

---

## Compiler STATUS Line

The compiler returns a single line that the orchestrator parses:

```
STATUS: compiled_v1.py written. 4 tasks, 4 levels. RUN_DIR: crypto-price-cli. TASKS: research_apis:researcher:0:loom/crypto-price-cli/outputs/researcher_1.py design_cli:architect:1:loom/crypto-price-cli/outputs/architect_1.py implement_cli:coder:2:loom/crypto-price-cli/outputs/coder_1.py review_cli:reviewer:3:loom/crypto-price-cli/outputs/reviewer_1.py
```

The orchestrator extracts:
- **RUN_DIR**: `crypto-price-cli` (passed to all subsequent subagents)
- **TASKS**: parsed into task_id, role, level, output_file tuples for spawning

---

## How Context Evolves

After the researcher runs, they might suggest patches like:

```python
prompt_patches = [
    {
        "action": "add_context",
        "key": "api_choice",
        "value": "CoinGecko — free, no key required, 50 calls/min"
    }
]
```

The merger applies this patch to create `compiled_v2.py`, which now includes the API choice in its `context` dict. Subsequent subagents see this enriched context when they read the compiled file.

---

## Key Points

- The compiled file is **structured data**, not executable code
- All paths include the **named run directory** (`loom/crypto-price-cli/`)
- Each subagent reads the compiled file from disk -- no prompt bloat
- Patches from subagents feed back into the next compiled version
- The orchestrator only sees the STATUS line, never the compiled file contents
