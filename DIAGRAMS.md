# Loom Visual Diagrams

Visual reference for how Loom works. These diagrams are in Mermaid format and render on GitHub.

For the technical explanation behind these diagrams, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Table of Contents

- [High-Level Overview](#high-level-overview)
- [Detailed Process Flow](#detailed-process-flow)
- [Parallel Execution Model](#parallel-execution-model)
- [System Architecture](#system-architecture)
- [Iteration Timeline](#iteration-timeline)
- [Data Flow Through Iterations](#data-flow-through-iterations)
- [Context Efficiency Comparison](#context-efficiency-comparison)
- [Patch-Based Refinement](#patch-based-refinement)
- [File System State Evolution](#file-system-state-evolution)

---

## High-Level Overview

```mermaid
flowchart TB
    subgraph Input["INPUT"]
        A[User Prompt<br/>Natural Language]
    end

    subgraph Core["LOOM CORE"]
        B[Compilation Engine<br/>Text to Python]
        C[Orchestration Layer<br/>Parallel Subagents]
        D[Refinement Loop<br/>Iterative Improvement]
    end

    subgraph Output["OUTPUT"]
        E[Deliverables<br/>Code, Docs, Analysis]
        F[Artifacts<br/>compiled_v*.py, outputs/, logs/]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    D --> F
    D -.iterate.-> B

    style Input fill:#e1f5ff
    style Core fill:#fff4e1
    style Output fill:#e8f5e9
```

---

## Detailed Process Flow

The 7-step process that Loom follows for every invocation. See [ARCHITECTURE.md - Core Architecture](ARCHITECTURE.md#core-architecture) for implementation details.

```mermaid
flowchart TD
    Start([User: /loom prompt]) --> Setup[Create loom/ workspace]

    Setup --> Compile[COMPILE<br/>Transform to Python<br/>loom/compiled_v1.py]

    Compile --> Analyze[ANALYZE<br/>Extract tasks and dependencies<br/>Build dependency graph]

    Analyze --> Orchestrate[ORCHESTRATE<br/>Match tasks to subagent types<br/>Group by dependency level]

    Orchestrate --> Spawn[SPAWN<br/>Launch subagents in parallel<br/>by level]

    Spawn --> Execute[EXECUTE<br/>Subagents read compiled.py<br/>Perform specialized tasks]

    Execute --> Collect[COLLECT<br/>Read loom/outputs/*.py<br/>Check for issues]

    Collect --> Merge[MERGE<br/>Apply prompt_patches<br/>Create compiled_v2.py]

    Merge --> Evaluate{EVALUATE<br/>Should iterate?}

    Evaluate -->|Yes<br/>Improvements found| Spawn
    Evaluate -->|No<br/>Converged or<br/>Max iterations| Present[PRESENT<br/>Show results and artifacts]

    Present --> End([Complete])

    style Start fill:#4CAF50,color:#fff
    style End fill:#4CAF50,color:#fff
    style Compile fill:#2196F3,color:#fff
    style Orchestrate fill:#FF9800,color:#fff
    style Execute fill:#9C27B0,color:#fff
    style Merge fill:#F44336,color:#fff
    style Evaluate fill:#FF5722,color:#fff
    style Present fill:#4CAF50,color:#fff
```

---

## Parallel Execution Model

Tasks are grouped by dependency level. All tasks at the same level run concurrently. See [ARCHITECTURE.md - Orchestration Layer](ARCHITECTURE.md#orchestration-layer) for the scheduling algorithm.

```mermaid
graph TB
    subgraph Level0["LEVEL 0: No Dependencies"]
        L0A[researcher_1<br/>Find APIs]
        L0B[architect_1<br/>Map codebase]
    end

    subgraph Level1["LEVEL 1: Depends on Level 0"]
        L1A[coder_1<br/>Implement backend]
        L1B[coder_2<br/>Implement frontend]
        L1C[architect_2<br/>Design system]
    end

    subgraph Level2["LEVEL 2: Depends on Level 1"]
        L2A[reviewer_1<br/>Test backend]
        L2B[reviewer_2<br/>Test frontend]
    end

    subgraph Level3["LEVEL 3: Depends on Level 2"]
        L3A[documenter_1<br/>Write docs]
    end

    Start([Compiled Prompt<br/>compiled_v1.py]) --> L0A & L0B

    L0A --> L1A & L1C
    L0B --> L1A & L1C
    L0A --> L1B
    L0B --> L1B

    L1A --> L2A
    L1B --> L2B

    L2A --> L3A
    L2B --> L3A

    L3A --> End([Results Aggregated])

    style Level0 fill:#c8e6c9
    style Level1 fill:#fff9c4
    style Level2 fill:#ffccbc
    style Level3 fill:#b3e5fc
    style Start fill:#4CAF50,color:#fff
    style End fill:#4CAF50,color:#fff
```

---

## System Architecture

How the orchestrator, file system, and subagent pool interact. See [ARCHITECTURE.md - Core Architecture](ARCHITECTURE.md#core-architecture).

```mermaid
graph TB
    subgraph User["USER LAYER"]
        UI[Claude Code Interface]
    end

    subgraph Orchestrator["LOOM ORCHESTRATOR"]
        LE[Loom Engine<br/>SKILL.md]
        CE[Compilation Engine]
        OE[Orchestration Engine]
        RE[Refinement Engine]

        LE --> CE
        LE --> OE
        LE --> RE
    end

    subgraph FileSystem["FILE SYSTEM STATE"]
        FS1[compiled_v*.py]
        FS2[outputs/*.py]
        FS3[logs/*.md]
    end

    subgraph Subagents["SUBAGENT POOL"]
        SA1[Researcher]
        SA2[Architect]
        SA3[Coder]
        SA4[Reviewer]
        SA5[Debugger]
        SA6[Data Analyst]
        SA7[Documenter]
        SA8[Custom...]
    end

    UI -->|/loom prompt| LE

    CE -->|write| FS1
    OE -->|spawn| SA1 & SA2 & SA3 & SA4 & SA5 & SA6 & SA7 & SA8
    SA1 & SA2 & SA3 & SA4 & SA5 & SA6 & SA7 & SA8 -->|read| FS1
    SA1 & SA2 & SA3 & SA4 & SA5 & SA6 & SA7 & SA8 -->|write| FS2
    RE -->|read| FS2
    RE -->|write| FS1
    RE -->|log| FS3

    LE -->|present| UI

    style User fill:#e8eaf6
    style Orchestrator fill:#fff3e0
    style FileSystem fill:#e0f2f1
    style Subagents fill:#fce4ec
```

---

## Iteration Timeline

Example timeline showing how parallelization saves time compared to sequential execution.

```mermaid
gantt
    title Loom Execution Timeline (Weather Dashboard)
    dateFormat X
    axisFormat %M:%S

    section Iteration 1
    Compile v1           :done, c1, 0, 30s
    Spawn researcher     :done, s1, after c1, 5min
    Spawn architect      :done, s2, after s1, 5min
    Collect results      :done, col1, after s2, 30s
    Merge patches to v2  :done, m1, after col1, 30s

    section Iteration 2
    Spawn architect      :done, s3, after m1, 5min
    Spawn coders (parallel) :done, s4, after s3, 5min
    Collect results      :done, col2, after s4, 30s
    Merge patches to v3  :done, m2, after col2, 30s

    section Iteration 3
    Spawn reviewers (parallel) :done, s5, after m2, 5min
    Collect results      :done, col3, after s5, 30s
    Converged - Present  :done, pres, after col3, 1min
```

---

## Data Flow Through Iterations

How the compiled prompt evolves from vague to validated across 3 iterations.

```mermaid
graph LR
    subgraph Iteration1["ITERATION 1: Discovery"]
        I1_Input["User Prompt<br/>(vague)"]
        I1_Compiled["compiled_v1.py<br/>2 tasks<br/>minimal context"]
        I1_Outputs["outputs/<br/>researcher_1.py<br/>architect_1.py"]
        I1_Issues["Issues:<br/>- Missing requirements<br/>- Vague specs"]

        I1_Input --> I1_Compiled
        I1_Compiled --> I1_Outputs
        I1_Outputs --> I1_Issues
    end

    subgraph Iteration2["ITERATION 2: Implementation"]
        I2_Compiled["compiled_v2.py<br/>4 tasks<br/>+ API context<br/>+ tech stack"]
        I2_Outputs["outputs/<br/>architect_2.py<br/>coder_1.py<br/>coder_2.py"]
        I2_Issues["Issues:<br/>- Missing tests"]

        I2_Compiled --> I2_Outputs
        I2_Outputs --> I2_Issues
    end

    subgraph Iteration3["ITERATION 3: Validation"]
        I3_Compiled["compiled_v3.py<br/>2 tasks<br/>+ test requirements"]
        I3_Outputs["outputs/<br/>reviewer_1.py<br/>reviewer_2.py"]
        I3_Done["All tests pass<br/>No new patches<br/>CONVERGED"]

        I3_Compiled --> I3_Outputs
        I3_Outputs --> I3_Done
    end

    I1_Issues -.patches.-> I2_Compiled
    I2_Issues -.patches.-> I3_Compiled

    style I1_Input fill:#ffcdd2
    style I1_Issues fill:#ffcdd2
    style I2_Issues fill:#fff9c4
    style I3_Done fill:#c8e6c9
```

---

## Context Efficiency Comparison

Why compilation matters: traditional approach duplicates context across every agent. Loom writes state to disk once and agents read it independently.

```mermaid
graph TB
    subgraph Traditional["TRADITIONAL APPROACH"]
        T1[User Prompt<br/>1000 tokens]
        T2[Agent 1 reads full context<br/>1000 tokens]
        T3[Agent 2 reads full context<br/>1000 tokens]
        T4[Agent 3 reads full context<br/>1000 tokens]
        T5[Agent 4 reads full context<br/>1000 tokens]
        T_Total["Total Context: 4000 tokens<br/>Sequential execution"]

        T1 --> T2 --> T3 --> T4 --> T5 --> T_Total
    end

    subgraph Loom["LOOM APPROACH"]
        L1[User Prompt<br/>1000 tokens]
        L2[Compile to Python<br/>200 tokens]
        L3[Write to disk: compiled.py]
        L4[Agent 1 reads compiled.py<br/>200 tokens]
        L5[Agent 2 reads compiled.py<br/>200 tokens]
        L6[Agent 3 reads compiled.py<br/>200 tokens]
        L7[Agent 4 reads compiled.py<br/>200 tokens]
        L_Total["Total Context: 800 tokens<br/>Parallel execution"]

        L1 --> L2 --> L3
        L3 --> L4 & L5 & L6 & L7
        L4 & L5 & L6 & L7 --> L_Total
    end

    style Traditional fill:#ffcdd2
    style Loom fill:#c8e6c9
    style T_Total fill:#ef5350,color:#fff
    style L_Total fill:#66bb6a,color:#fff
```

---

## Patch-Based Refinement

How subagents suggest improvements to the compiled prompt through structured patches. See [ARCHITECTURE.md - Refinement Loop](ARCHITECTURE.md#refinement-loop).

```mermaid
sequenceDiagram
    participant U as User
    participant L as Loom Orchestrator
    participant C as compiled_v1.py
    participant S as Subagent
    participant O as outputs/agent_1.py
    participant C2 as compiled_v2.py

    U->>L: /loom build a CLI
    L->>C: Write compiled_v1.py
    Note over C: version=1<br/>tasks=[...]<br/>context={}

    L->>S: Spawn subagent
    S->>C: Read compiled prompt
    S->>S: Execute task
    S->>O: Write results + patches
    Note over O: prompt_patches=[<br/>  {action: "add_context"},<br/>  {action: "add_task"}<br/>]

    L->>O: Read subagent output
    L->>C2: Apply patches
    Note over C2: version=2<br/>tasks=[...new...]<br/>context={...added...}

    L->>L: Iterate with v2
```

---

## File System State Evolution

How the `loom/` workspace grows across iterations.

```mermaid
graph TD
    subgraph Init["Initial State"]
        I1[loom/<br/>empty]
    end

    subgraph After_I1["After Iteration 1"]
        A1[loom/<br/>compiled_v1.py<br/>outputs/researcher_1.py<br/>outputs/architect_1.py<br/>logs/iteration_1.md]
    end

    subgraph After_I2["After Iteration 2"]
        A2[loom/<br/>compiled_v1.py<br/>compiled_v2.py<br/>outputs/architect_2.py<br/>outputs/coder_1.py<br/>outputs/coder_2.py<br/>logs/iteration_2.md]
    end

    subgraph After_I3["After Iteration 3"]
        A3[loom/<br/>compiled_v3.py<br/>compiled_final.py<br/>outputs/reviewer_1.py<br/>outputs/reviewer_2.py<br/>logs/iteration_3.md]
    end

    Init --> After_I1
    After_I1 --> After_I2
    After_I2 --> After_I3

    style Init fill:#ffebee
    style After_I1 fill:#fff3e0
    style After_I2 fill:#e8f5e9
    style After_I3 fill:#c8e6c9
```

---

## Related Documentation

- [README.md](README.md) - Overview and quick start
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details behind these diagrams
- [SKILL.md](SKILL.md) - The skill definition (operational reference)
- [examples/](examples/) - Worked examples showing these flows in action
