# Example: Recursive Refinement Loop

This example demonstrates how Loom iteratively refines prompts through automated feedback loops, progressively improving quality.

---

## Scenario: Build a Weather Dashboard

**Initial User Prompt:**
```
/loom build a weather dashboard
```

*(Intentionally vague to demonstrate refinement)*

---

## Iteration 1: Discovery Phase

### Compiled Prompt v1

```python
class CompiledPrompt:
    version = 1
    original = "build a weather dashboard"

    intent = {
        "type": "build_application",
        "domain": "web",
        "goals": [
            "Display weather information",
            "Create dashboard interface"
        ],
        "success_criteria": [
            "Weather data is displayed",
            "UI is functional"
        ]
    }

    tasks = [
        {
            "id": "research_weather_apis",
            "description": "Find weather APIs suitable for dashboard",
            "requires": ["research"],
            "depends_on": [],
            "outputs_to": "loom/outputs/researcher_1.py"
        },
        {
            "id": "design_dashboard",
            "description": "Design dashboard UI and architecture",
            "requires": ["design"],
            "depends_on": ["research_weather_apis"],
            "outputs_to": "loom/outputs/architect_1.py"
        }
    ]

    context = {
        "constraints": ["User prompt is vague - need more details"],
        "preferences": {}
    }

    deliverables = ["Weather dashboard application"]
```

### Execution

**Researcher Output:**
```python
class ResearcherOutput:
    task_id = "research_weather_apis"
    iteration = 1
    completed = True

    results = {
        "recommended_api": "OpenWeatherMap",
        "alternatives": ["WeatherAPI", "Weatherstack"],
        "api_key_required": True,
        "free_tier": "1000 calls/day"
    }

    prompt_patches = [
        {
            "action": "add_context",
            "key": "weather_api",
            "value": {
                "name": "OpenWeatherMap",
                "endpoint": "https://api.openweathermap.org/data/2.5/weather",
                "requires_key": True,
                "free_tier": "1000 calls/day"
            }
        },
        {
            "action": "add_task",
            "task": {
                "id": "clarify_requirements",
                "description": "Need clarification: Real-time updates? Multi-location? Historical data?",
                "requires": ["user_input"],
                "depends_on": [],
                "outputs_to": "loom/outputs/meta_1.py"
            }
        }
    ]

    issues = [
        {
            "severity": "medium",
            "message": "User prompt too vague - missing key requirements"
        }
    ]
```

**Architect Output:**
```python
class ArchitectOutput:
    task_id = "design_dashboard"
    iteration = 1
    completed = False  # Blocked!

    results = {
        "message": "Cannot design without knowing: What features? What tech stack? Real-time or static?"
    }

    prompt_patches = [
        {
            "action": "update_intent",
            "updates": {
                "goals": [
                    "Display current weather for user-specified location",
                    "Show temperature, conditions, humidity, wind",
                    "Responsive web interface",
                    "Search for locations"
                ]
            }
        },
        {
            "action": "add_context",
            "key": "tech_stack",
            "value": {
                "frontend": "React (assumption)",
                "backend": "Node.js + Express (assumption)",
                "styling": "Tailwind CSS (assumption)"
            }
        },
        {
            "action": "add_task",
            "task": {
                "id": "implement_backend",
                "description": "Build backend API server with weather API integration",
                "requires": ["coding"],
                "depends_on": ["design_dashboard"],
                "outputs_to": "loom/outputs/coder_1.py"
            }
        },
        {
            "action": "add_task",
            "task": {
                "id": "implement_frontend",
                "description": "Build React frontend with weather display",
                "requires": ["coding"],
                "depends_on": ["design_dashboard"],
                "outputs_to": "loom/outputs/coder_2.py"
            }
        }
    ]

    issues = [
        {
            "severity": "high",
            "message": "Requirements too vague. Made assumptions about tech stack and features."
        }
    ]
```

### Iteration 1 Summary

```markdown
# Iteration 1

## What Happened
- Researcher found OpenWeatherMap API
- Architect identified missing requirements
- Architect made assumptions to proceed

## Issues Discovered
- User prompt too vague (missing features, tech stack)
- Cannot proceed without more details

## Improvements Applied
- Added context: weather API details
- Clarified goals: specific weather metrics to display
- Added assumptions: tech stack (React, Node.js)
- Added tasks: implement_backend, implement_frontend

## Decision
→ Iterate with refined prompt (v2)
```

---

## Iteration 2: Implementation Phase

### Compiled Prompt v2

```python
"""
Changes from v1:
- Added context: weather_api (OpenWeatherMap details)
- Added context: tech_stack (React, Node.js, Tailwind)
- Updated intent: More specific goals (temperature, conditions, humidity, wind, search)
- Added task: implement_backend
- Added task: implement_frontend
"""

class CompiledPrompt:
    version = 2
    original = "build a weather dashboard"

    intent = {
        "type": "build_application",
        "domain": "web",
        "goals": [
            "Display current weather for user-specified location",
            "Show: temperature, conditions, humidity, wind speed",
            "Responsive web interface",
            "Location search functionality"
        ],
        "success_criteria": [
            "Weather data displayed accurately",
            "UI is responsive on mobile/desktop",
            "Search works for valid locations",
            "Error handling for invalid inputs"
        ]
    }

    tasks = [
        # research_weather_apis - REMOVED (completed in v1)
        {
            "id": "design_dashboard",
            "description": "Design dashboard UI and architecture with React + Node.js",
            "requires": ["design"],
            "depends_on": [],
            "outputs_to": "loom/outputs/architect_2.py"
        },
        {
            "id": "implement_backend",
            "description": "Build Node.js backend with OpenWeatherMap API integration",
            "requires": ["coding"],
            "depends_on": ["design_dashboard"],
            "outputs_to": "loom/outputs/coder_1.py"
        },
        {
            "id": "implement_frontend",
            "description": "Build React frontend with weather display and search",
            "requires": ["coding"],
            "depends_on": ["design_dashboard"],
            "outputs_to": "loom/outputs/coder_2.py"
        }
    ]

    context = {
        "constraints": [
            "Use OpenWeatherMap API",
            "React for frontend, Node.js for backend",
            "Responsive design required"
        ],
        "preferences": {
            "styling": "Tailwind CSS"
        },
        "weather_api": {
            "name": "OpenWeatherMap",
            "endpoint": "https://api.openweathermap.org/data/2.5/weather",
            "requires_key": True,
            "free_tier": "1000 calls/day"
        },
        "tech_stack": {
            "frontend": "React",
            "backend": "Node.js + Express",
            "styling": "Tailwind CSS"
        }
    }

    deliverables = [
        "Backend server (Node.js) with API endpoints",
        "Frontend app (React) with weather display",
        "README with setup instructions",
        "Environment variable template (.env.example)"
    ]
```

### Execution

**Architect Output:**
```python
class ArchitectOutput:
    task_id = "design_dashboard"
    iteration = 2
    completed = True

    results = {
        "architecture": {
            "backend": {
                "entry": "server.js",
                "routes": "/api/weather?location=<city>",
                "env_vars": ["OPENWEATHER_API_KEY", "PORT"]
            },
            "frontend": {
                "entry": "src/App.jsx",
                "components": ["SearchBar", "WeatherCard", "ErrorMessage"],
                "state": "useState for location and weather data"
            }
        },
        "file_structure": """
weather-dashboard/
├── backend/
│   ├── server.js
│   ├── package.json
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── SearchBar.jsx
│   │   │   ├── WeatherCard.jsx
│   │   │   └── ErrorMessage.jsx
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
└── README.md
"""
    }

    prompt_patches = []  # Design is solid, no changes needed
```

**Coder 1 Output (Backend):**
```python
class CoderOutput:
    task_id = "implement_backend"
    iteration = 2
    completed = True

    results = {
        "message": "Backend implemented with weather API integration"
    }

    files_changed = [
        "backend/server.js",
        "backend/package.json",
        "backend/.env.example"
    ]

    prompt_patches = [
        {
            "action": "add_task",
            "task": {
                "id": "test_backend",
                "description": "Test backend API endpoints and error handling",
                "requires": ["testing"],
                "depends_on": ["implement_backend"],
                "outputs_to": "loom/outputs/reviewer_1.py"
            }
        }
    ]
```

**Coder 2 Output (Frontend):**
```python
class CoderOutput:
    task_id = "implement_frontend"
    iteration = 2
    completed = True

    results = {
        "message": "React frontend implemented with weather display"
    }

    files_changed = [
        "frontend/src/App.jsx",
        "frontend/src/components/SearchBar.jsx",
        "frontend/src/components/WeatherCard.jsx",
        "frontend/src/components/ErrorMessage.jsx",
        "frontend/package.json",
        "frontend/tailwind.config.js"
    ]

    prompt_patches = [
        {
            "action": "add_task",
            "task": {
                "id": "test_frontend",
                "description": "Test UI responsiveness and search functionality",
                "requires": ["testing"],
                "depends_on": ["implement_frontend"],
                "outputs_to": "loom/outputs/reviewer_2.py"
            }
        }
    ]
```

### Iteration 2 Summary

```markdown
# Iteration 2

## What Happened
- Architect designed complete system architecture
- Backend coder implemented Node.js API server
- Frontend coder implemented React weather display
- Both coders suggested adding tests

## Issues Discovered
- No tests yet (added to v3)

## Improvements Applied
- Added task: test_backend
- Added task: test_frontend

## Decision
→ Iterate for testing and validation (v3)
```

---

## Iteration 3: Validation Phase

### Compiled Prompt v3

```python
"""
Changes from v2:
- Removed completed tasks: design_dashboard, implement_backend, implement_frontend
- Added task: test_backend (from coder_1 patch)
- Added task: test_frontend (from coder_2 patch)
- Updated deliverables: added test files
"""

class CompiledPrompt:
    version = 3
    # ... (intent and context same as v2) ...

    tasks = [
        {
            "id": "test_backend",
            "description": "Test backend API endpoints, error handling, API integration",
            "requires": ["testing"],
            "depends_on": [],
            "outputs_to": "loom/outputs/reviewer_1.py"
        },
        {
            "id": "test_frontend",
            "description": "Test UI responsiveness, search functionality, error states",
            "requires": ["testing"],
            "depends_on": [],
            "outputs_to": "loom/outputs/reviewer_2.py"
        }
    ]

    deliverables = [
        "Backend server (Node.js) with API endpoints [done]",
        "Frontend app (React) with weather display [done]",
        "README with setup instructions",
        "Environment variable template (.env.example) [done]",
        "Test results and validation"  # NEW
    ]
```

### Execution

**Reviewer 1 Output (Backend Tests):**
```python
class ReviewerOutput:
    task_id = "test_backend"
    iteration = 3
    completed = True

    results = {
        "tests_passed": [
            "GET /api/weather?location=London returns 200",
            "Weather data structure is correct",
            "API key from env is used correctly"
        ],
        "issues_found": [
            {
                "severity": "low",
                "file": "server.js",
                "line": 45,
                "issue": "Missing rate limiting for API calls",
                "fix": "Add express-rate-limit middleware"
            }
        ]
    }

    prompt_patches = [
        {
            "action": "add_context",
            "key": "known_issues",
            "value": {
                "backend": ["Missing rate limiting (low severity)"]
            }
        }
    ]
```

**Reviewer 2 Output (Frontend Tests):**
```python
class ReviewerOutput:
    task_id = "test_frontend"
    iteration = 3
    completed = True

    results = {
        "tests_passed": [
            "UI renders on mobile and desktop",
            "Search submits correctly",
            "Weather data displays properly",
            "Error messages show for invalid locations"
        ],
        "issues_found": [
            {
                "severity": "low",
                "file": "App.jsx",
                "line": 28,
                "issue": "Loading state not shown during API call",
                "fix": "Add loading spinner component"
            }
        ]
    }

    prompt_patches = [
        {
            "action": "add_context",
            "key": "known_issues",
            "value": {
                "frontend": ["Missing loading indicator (low severity)"]
            }
        }
    ]
```

### Iteration 3 Summary

```markdown
# Iteration 3

## What Happened
- Backend reviewer tested API endpoints (all passed)
- Frontend reviewer tested UI (all passed)
- Found 2 low-severity issues (rate limiting, loading state)

## Issues Discovered
- Backend: Missing rate limiting
- Frontend: Missing loading indicator
(Both low severity, not blocking)

## Improvements Applied
- Documented known issues in context

## Decision
→ Converged! Core functionality complete.
   Low-severity issues can be addressed later.
```

---

## Final Results

### LOOM RESULTS

```markdown
---
Original: "build a weather dashboard"
---

### Iteration 1 (Discovery)
[done] Compiled → loom/compiled_v1.py
  Tasks: 2 (research, design)

[done] Spawned 2 agents
  - researcher: Found OpenWeatherMap API
  - architect: Identified missing requirements

[note] Improvements needed:
  - Clarified specific weather metrics to display
  - Made tech stack decisions (React, Node.js)
  - Added implementation tasks

### Iteration 2 (Implementation)
[done] Recompiled → loom/compiled_v2.py
  Added context: weather_api, tech_stack
  Added tasks: implement_backend, implement_frontend

[done] Spawned 3 agents
  - architect: Designed system architecture
  - coder (backend): Built Node.js API server
  - coder (frontend): Built React weather UI

[done] Improvements suggested:
  - Add testing tasks

### Iteration 3 (Validation)
[done] Recompiled → loom/compiled_v3.py
  Added tasks: test_backend, test_frontend

[done] Spawned 2 reviewers
  - reviewer (backend): All tests passed [done]
  - reviewer (frontend): All tests passed [done]

[done] Minor issues found (low severity, documented)

---

### DELIVERABLES

[done] Backend server with OpenWeatherMap integration
[done] React frontend with weather display
[done] Responsive design (mobile + desktop)
[done] Location search functionality
[done] Error handling for invalid inputs
[done] README with setup instructions
[done] .env.example template
[done] Test validation results

Known Issues (low severity):
- Backend: Missing rate limiting
- Frontend: Missing loading indicator

### LOOM STATE

loom/
├── compiled_v1.py → v2.py → v3.py (evolution)
├── outputs/
│   ├── researcher_1.py
│   ├── architect_1.py, architect_2.py
│   ├── coder_1.py, coder_2.py
│   └── reviewer_1.py, reviewer_2.py
└── logs/
    ├── iteration_1.md
    ├── iteration_2.md
    └── iteration_3.md

---
```

---

## Evolution Analysis

### Prompt Quality Progression

**v1 (Vague):**
```
"build a weather dashboard"
→ 2 tasks, minimal context, blocked architect
```

**v2 (Refined):**
```
Added: weather API, tech stack, specific features
→ 3 tasks, clear implementation path
```

**v3 (Validated):**
```
Added: testing tasks, validation results
→ 2 tasks, quality assurance
```

### Key Improvements Across Iterations

| Aspect | v1 | v2 | v3 |
|--------|----|----|-----|
| **Clarity** | Vague | Specific | Validated |
| **Context** | Minimal | Rich (API, stack) | Complete |
| **Tasks** | 2 | 3 | 2 (testing) |
| **Completeness** | 20% | 80% | 100% |
| **Issues** | Many unknowns | Implementation ready | Production ready |

---

## Why Refinement Works

### 1. **Discovery in v1**
- Subagents identify missing requirements
- Suggest patches to fill gaps
- Make necessary assumptions

### 2. **Implementation in v2**
- Clear context enables productive work
- Subagents can execute confidently
- Suggest validation tasks

### 3. **Validation in v3**
- Quality assurance catches issues
- Minor problems documented
- Converged solution

---

## Convergence Detection

Loom stops iterating when:

[done] **No new patches suggested**
```python
if len(all_patches) == 0:
    break  # Converged
```

[done] **All tasks completed successfully**
```python
if all(output.completed for output in outputs):
    break  # Success
```

[done] **Maximum iterations reached**
```python
if iteration >= 3:
    break  # Max iterations
```

[done] **Prompt stabilized (v{{N}} == v{{N-1}})**
```python
if compiled_v3 == compiled_v2:
    break  # No changes
```

---

## Key Takeaways

1. **Vague prompts are okay** - Loom refines them automatically
2. **Subagents discover missing requirements** through execution
3. **Each iteration improves** on the previous through patches
4. **Convergence is automatic** - stops when no more improvements
5. **Full audit trail** - evolution tracked in compiled_v*.py files

---

## Try It Yourself

Start with a vague prompt and watch Loom refine it:

```bash
/loom build a todo app

# Then watch the evolution:
cat loom/compiled_v1.py  # Initial compilation
cat loom/compiled_v2.py  # After discovering requirements
cat loom/compiled_v3.py  # Final refined version

# See what changed:
diff loom/compiled_v1.py loom/compiled_v2.py
```

---

Recursive refinement transforms rough ideas into validated solutions through automated feedback loops.

---

## Other Examples

- [Prompt Compilation](prompt-compilation.md) - How Loom compiles prompts to Python
- [Parallel Execution](parallel-execution.md) - How Loom runs multiple subagents concurrently

## Related Documentation

- [README.md](../README.md) - Overview and quick start
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Technical deep dive into the refinement loop
- [DIAGRAMS.md](../DIAGRAMS.md) - Visual flowcharts
