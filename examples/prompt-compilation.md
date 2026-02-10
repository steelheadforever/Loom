# Example: Prompt Compilation

This example demonstrates how Loom compiles a natural language prompt into structured Python.

---

## Input Prompt

```
/loom build a CLI that fetches current crypto prices from an API and displays them in a table
```

---

## Compiled Output: `loom/compiled_v1.py`

```python
class CompiledPrompt:
    """Iteration 1 - Initial compilation of crypto CLI request"""

    version = 1
    original = "build a CLI that fetches current crypto prices from an API and displays them in a table"

    # What the user wants
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
            "Table formatting is readable",
            "Code is well-structured"
        ]
    }

    # Work breakdown
    tasks = [
        {
            "id": "research_apis",
            "description": "Find suitable cryptocurrency price APIs (free, reliable, good documentation)",
            "requires": ["web_search", "api_research"],
            "depends_on": [],
            "outputs_to": "loom/outputs/researcher_1.py"
        },
        {
            "id": "design_cli_structure",
            "description": "Design CLI architecture: argument parsing, API client, table formatter",
            "requires": ["design", "architecture"],
            "depends_on": ["research_apis"],
            "outputs_to": "loom/outputs/architect_1.py"
        },
        {
            "id": "implement_cli",
            "description": "Implement the CLI tool with API integration and table display",
            "requires": ["python", "coding"],
            "depends_on": ["design_cli_structure"],
            "outputs_to": "loom/outputs/coder_1.py"
        },
        {
            "id": "test_cli",
            "description": "Test CLI functionality, check error handling, validate output format",
            "requires": ["testing", "validation"],
            "depends_on": ["implement_cli"],
            "outputs_to": "loom/outputs/reviewer_1.py"
        }
    ]

    # Context for subagents
    context = {
        "constraints": [
            "Use Python for implementation",
            "CLI should be simple to run (no complex setup)",
            "Handle API errors gracefully",
            "Free API preferred (no API key if possible)"
        ],
        "preferences": {
            "table_library": "prefer built-in or minimal dependencies"
        },
        "existing_state": None
    }

    # Expected outputs
    deliverables = [
        "Working CLI script (crypto_prices.py)",
        "requirements.txt with dependencies",
        "Basic README with usage instructions",
        "Error handling for common issues"
    ]
```

---

## Analysis

### What Loom Did

1. **Extracted Intent:**
   - Type: `build_application`
   - Domain: `cli`
   - Clear goals and success criteria

2. **Broke Down Work:**
   - 4 discrete tasks with clear descriptions
   - Identified dependencies (research → design → implement → test)
   - Assigned appropriate capabilities to each task

3. **Captured Context:**
   - Constraints (Python, simple setup, error handling, free API)
   - Preferences (minimal dependencies)
   - No existing state to consider

4. **Identified Deliverables:**
   - CLI script
   - Dependencies file
   - Documentation
   - Error handling

### Dependency Graph

```
research_apis (Level 0)
      ↓
design_cli_structure (Level 1)
      ↓
implement_cli (Level 2)
      ↓
test_cli (Level 3)
```

This is a **sequential pipeline** - each task depends on the previous.

### Next Steps

With this compiled prompt:
1. Loom will spawn **researcher** at Level 0
2. Wait for completion, then spawn **architect** at Level 1
3. Wait for completion, then spawn **coder** at Level 2
4. Wait for completion, then spawn **reviewer** at Level 3

Each subagent reads `compiled_v1.py` to understand their task and context.

---

## Benefits of Compilation

### Before (Plain Text)
```
"build a CLI that fetches current crypto prices from an API and displays them in a table"
```
- Ambiguous (which API? what table format? what language?)
- No structure (how to parallelize?)
- No context preservation (each subagent needs full prompt)

### After (Compiled Python)
```python
intent = {...}      # Clear goals
tasks = [...]       # Structured work breakdown
context = {...}     # Explicit constraints
deliverables = [...] # Expected outputs
```
- Explicit (decisions captured)
- Structured (parallelizable by dependency graph)
- Efficient (subagents read from disk)
- Analyzable (can diff versions)

---

## Iteration 2 Changes

After researcher returns API choice, `compiled_v2.py` might look like:

```python
# Changes from v1:
# - Added context: api_choice = "CoinGecko"
# - Added context: api_endpoint = "https://api.coingecko.com/api/v3/simple/price"
# - Updated task: implement_cli now specifies CoinGecko API

class CompiledPrompt:
    version = 2
    # ... same as v1 ...

    context = {
        "constraints": [...],
        "preferences": {...},
        "existing_state": None,

        # NEW: API choice from researcher
        "api_choice": "CoinGecko",
        "api_endpoint": "https://api.coingecko.com/api/v3/simple/price",
        "api_rate_limit": "50 calls/minute",
        "api_notes": "Free, no API key required, well-documented"
    }

    tasks = [
        # research_apis task removed (completed)
        {
            "id": "design_cli_structure",
            # ... same as v1 ...
        },
        {
            "id": "implement_cli",
            "description": "Implement CLI using CoinGecko API (/api/v3/simple/price endpoint)",  # UPDATED
            # ... rest same as v1 ...
        },
        # ...
    ]
```

---

## Key Takeaways

1. **Compilation adds structure** to ambiguous prompts
2. **Dependencies are explicit**, enabling intelligent scheduling
3. **Context accumulates** across iterations (API choice added in v2)
4. **Subagents get zero-context overhead** by reading from disk
5. **Evolution is trackable** through version diffs

---

## Try It Yourself

```bash
/loom <your complex prompt>

# Then inspect the compilation:
cat loom/compiled_v1.py
```

Notice how Loom transforms your natural language into structured, executable Python!
