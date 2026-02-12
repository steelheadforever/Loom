# Example: Refinement Loop

How Loom iteratively refines a vague prompt into a validated result.

---

## Scenario

```
/loom build a weather dashboard
```

Intentionally vague -- Loom will discover the missing requirements through iteration.

---

## Iteration 1: Discovery

**Compiler** produces `loom/weather-dashboard/compiled_v1.py` with 2 tasks:
- `research_weather_apis` (researcher, Level 0)
- `design_dashboard` (architect, Level 1)

**Researcher** finds OpenWeatherMap API, returns structured data with patches:
```python
prompt_patches = [
    {"action": "add_context", "key": "weather_api",
     "value": "OpenWeatherMap — free tier, 1000 calls/day, requires API key"}
]
```

**Architect** sets `completed = False` -- blocked because the prompt is too vague:
> "Cannot design without knowing: What features? What tech stack? Real-time or static?"

The architect suggests patches to fill the gaps (assumes React + Node.js, specific weather metrics).

**Merger** validates outputs, applies patches, writes `compiled_v2.py` with enriched context and new implementation tasks. Verdict: `ITERATE`.

---

## Iteration 2: Implementation

`compiled_v2.py` now has clear context (API choice, tech stack, feature list) and 3 tasks:
- `design_dashboard` (architect, Level 0) -- redesigned with full context
- `implement_backend` (coder, Level 1)
- `implement_frontend` (coder, Level 1) -- parallel with backend

**Architect** completes the design with component structure and file layout.

**Two coders** run in parallel:
- Backend coder builds Node.js API server with OpenWeatherMap integration
- Frontend coder builds React UI with search and weather display

Both suggest adding test tasks via patches.

**Merger** applies patches, adds test tasks, writes `compiled_v3.py`. Verdict: `ITERATE`.

---

## Iteration 3: Validation

`compiled_v3.py` has 2 test tasks at Level 0 (both parallel):
- `test_backend` (reviewer)
- `test_frontend` (reviewer)

**Both reviewers** run in parallel, find only low-severity issues (missing rate limiting, missing loading indicator). No new patches needed.

**Merger** sees all tasks completed, no meaningful patches. Verdict: `CONVERGED`.

---

## Final Output

```
loom/weather-dashboard/
  summary.md              # Polished description of what was built
  final_report.md         # 3 iterations, convergence path
  compiled_v1.py          # Vague: 2 tasks, minimal context
  compiled_v2.py          # Refined: 3 tasks, API + stack chosen
  compiled_v3.py          # Validated: 2 test tasks
  outputs/
    researcher_1.py       # API research
    architect_1.py        # System design
    coder_1.py            # Backend implementation
    coder_2.py            # Frontend implementation
    reviewer_1.py         # Backend tests
    reviewer_2.py         # Frontend tests
  logs/
    iteration_1.md
    iteration_2.md
    iteration_3.md
    costs.md
```

---

## Prompt Quality Progression

| Aspect | v1 | v2 | v3 |
|--------|----|----|-----|
| **Clarity** | Vague | Specific | Validated |
| **Context** | Minimal | Rich (API, stack) | Complete |
| **Tasks** | 2 | 3 | 2 (testing) |

---

## Key Points

- **Vague prompts are fine** -- subagents discover missing requirements through execution
- **Patches drive refinement** -- each subagent can suggest improvements to the compiled prompt
- **The merger decides** whether to iterate, converge, or ask the user for clarification
- **3 iterations max** -- hard limit prevents runaway loops
- **Convergence is automatic** -- when no new patches are needed, Loom stops
- **The full evolution is preserved** -- `compiled_v1.py` through `compiled_v3.py` show exactly what changed and why
