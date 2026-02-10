# Changelog

All notable changes to the Loom project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-10

### Added
- Initial release of loom skill for Claude Code
- **Prompt-to-Python compilation engine**
  - Transforms natural language prompts into structured Python representations
  - Includes CompiledPrompt class template with intent, tasks, context, deliverables
  - Version tracking for compiled prompt evolution
- **Parallel subagent orchestration system**
  - 7 built-in subagent types: researcher, architect, coder, reviewer, data_analyst, documenter, debugger
  - Dependency-aware task scheduling with multi-level parallel execution
  - Custom subagent creation for specialized tasks
  - Task tool integration for spawning subagents
- **Recursive refinement feedback loop**
  - Up to 3 iterations with automatic convergence detection
  - Patch-based prompt updates from subagent feedback
  - Iteration logging with detailed session history
- **Loom workspace structure**
  - `loom/compiled_v*.py` for prompt evolution tracking
  - `loom/outputs/*.py` for subagent result storage
  - `loom/logs/iteration_*.md` for detailed iteration logs
- **Comprehensive skill documentation**
  - Step-by-step orchestration process
  - Subagent prompt templates
  - Patch action system (add_context, update_task, add_task, etc.)
  - Best practices and special cases
  - Example session walkthrough
- **State management**
  - Continue from previous loom session or start fresh
  - All artifacts saved to disk for inspection
  - Zero context overhead through file-based state

### Documentation
- README.md with installation, usage, and examples
- LICENSE (MIT)
- CHANGELOG.md (this file)
- Detailed inline documentation in SKILL.md

## [Unreleased]

### Planned
- ARCHITECTURE.md with technical deep dive
- Example workflows in examples/ directory
- CONTRIBUTING.md with contribution guidelines
- Integration examples with common workflows
- Performance benchmarks and metrics
- Video walkthrough of loom in action

---

## Version History

### 0.1.0 (2026-02-10)
Initial public release of loom skill for the Claude Code community.

---

**Note:** This project is in active development. Features and APIs may change as we gather feedback from the community.

For the latest updates, see the [GitHub repository](https://github.com/yourusername/loom).
