# Loom Role Registry

**Read `security_rules.md` FIRST.**

## Available Roles

### researcher
- **Good for**: finding information, web research, documentation lookup, API discovery
- **Tools**: web_search, web_fetch, read, grep
- **Returns**: structured data with sources
- **Bash access**: NONE (research is read-only)
- **subagent_type**: `general-purpose`

### architect
- **Good for**: design decisions, choosing approaches, tech stack, tradeoff analysis
- **Tools**: read, write, grep, glob
- **Returns**: design decisions with reasoning
- **Bash access**: NONE (design is read/write only)
- **subagent_type**: `general-purpose`

### coder
- **Good for**: implementing features, writing code, building applications
- **Tools**: read, write, edit, bash, grep, glob
- **Returns**: code files or implementations
- **Bash allowed**: `pytest`, `python`, `python3`, `npm`, `npm test`, `npx`, `pip install`, `cargo`, `cargo test`, `go test`, `make`, `eslint`, `prettier`, `black`, `ruff`, `mypy`, `tsc`
- **Bash blocked**: `curl`, `wget`, `ssh`, `scp`, `nc`, `ncat`, `sh -c`, `bash -c`, `eval`, `exec`
- **subagent_type**: `general-purpose`

### reviewer
- **Good for**: checking correctness, finding bugs, code review, validation
- **Tools**: read, grep, glob, bash
- **Returns**: issues list with severity + patches
- **Bash allowed**: `pytest`, `python -m pytest`, `npm test`, `cargo test`, `go test`, `make test`
- **Bash blocked**: `curl`, `wget`, `ssh`, `scp`, `nc`, `ncat`, `sh -c`, `bash -c`, `eval`, `exec`
- **subagent_type**: `general-purpose`

### data_analyst
- **Good for**: analyzing datasets, statistics, data cleaning, insights
- **Tools**: read, bash, grep, glob
- **Returns**: analysis results with visualizations
- **Bash allowed**: `python`, `python3`
- **Bash blocked**: `curl`, `wget`, `ssh`, `scp`, `nc`, `ncat`, `sh -c`, `bash -c`, `eval`, `exec`
- **subagent_type**: `general-purpose`

### documenter
- **Good for**: writing docs, tutorials, API documentation, READMEs
- **Tools**: read, write
- **Returns**: documentation files
- **Bash access**: NONE (documentation is read/write only)
- **subagent_type**: `general-purpose`

### debugger
- **Good for**: fixing broken code, error analysis, troubleshooting
- **Tools**: read, edit, bash, grep, glob
- **Returns**: patches and fixes
- **Bash allowed**: `pytest`, `python`, `python3`, `npm test`, `node`, `cargo test`, `go test`, `make test`
- **Bash blocked**: `curl`, `wget`, `ssh`, `scp`, `nc`, `ncat`, `sh -c`, `bash -c`, `eval`, `exec`
- **subagent_type**: `general-purpose`

## Role Selection Rules

- Task requires external info → `researcher`
- Task involves design choices → `architect`
- Task is implementation → `coder`
- Task is validation/review → `reviewer`
- Task involves data analysis → `data_analyst`
- Task is documentation → `documenter`
- Task is fixing bugs → `debugger`

## Custom Roles

If no standard role fits:
1. **Requires user approval** before spawning
2. **Default: NO bash access** (tools: read, write, edit, grep, glob)
3. If user approves bash, apply coder/debugger restrictions
4. Orchestrator writes task instructions (never copy raw user input)
