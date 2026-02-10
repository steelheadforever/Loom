# Contributing to Loom

Thank you for your interest in contributing to Loom! This document provides guidelines and information for contributors.

---

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Reporting Issues](#reporting-issues)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Code Contributions](#code-contributions)
- [Documentation Improvements](#documentation-improvements)
- [Sharing Examples](#sharing-examples)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

---

## Ways to Contribute

There are many ways to contribute to Loom:

### 🐛 Report Bugs
Found a bug? Report it via [GitHub Issues](../../issues) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Loom artifacts (compiled_v*.py, outputs, logs) if applicable
- Claude Code version

### 💡 Suggest Features
Have an idea for improvement? Open a [Feature Request](../../issues/new?template=feature_request.md):
- Describe the feature and use case
- Explain why it would be valuable
- Provide examples if possible

### 📖 Improve Documentation
Help make Loom easier to understand:
- Fix typos or unclear explanations
- Add examples and use cases
- Improve installation instructions
- Translate documentation (future)

### 🎯 Share Examples
Share interesting workflows:
- Create example markdown files in `examples/`
- Document real-world use cases
- Show creative Loom applications

### 🔧 Submit Code
Improve Loom's implementation:
- Fix bugs
- Add subagent types
- Optimize compilation logic
- Enhance orchestration

### 💬 Help Others
Support the community:
- Answer questions in [Discussions](../../discussions)
- Review pull requests
- Share tips and tricks

---

## Getting Started

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/loom.git
   cd loom
   ```

2. **Install the skill locally**
   ```bash
   cp SKILL.md ~/.claude/skills/loom.md
   # OR for project-specific:
   mkdir -p .claude/skills
   cp SKILL.md .claude/skills/loom.md
   ```

3. **Try it out**
   ```bash
   # In Claude Code:
   /loom build a simple CLI

   # Inspect artifacts:
   cat loom/compiled_v1.py
   cat loom/outputs/*.py
   cat loom/logs/iteration_1.md
   ```

4. **Make your changes**
   - Edit SKILL.md for skill logic changes
   - Edit documentation files for docs improvements
   - Add examples in examples/ directory

5. **Test thoroughly**
   - Run loom with various prompts
   - Check that artifacts are generated correctly
   - Verify refinement loop works as expected

6. **Submit a pull request**
   - Clear description of changes
   - Reference related issues
   - Include examples if applicable

---

## Reporting Issues

### Before Submitting

- Check [existing issues](../../issues) to avoid duplicates
- Try the latest version of Loom
- Verify it's a Loom issue, not a Claude Code issue

### Issue Template

```markdown
## Description
[Clear description of the issue]

## Steps to Reproduce
1. Run `/loom <your prompt>`
2. Observe iteration X
3. See error in ...

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happened]

## Artifacts
<details>
<summary>loom/compiled_v1.py</summary>

```python
[paste compiled prompt]
```
</details>

<details>
<summary>Error output</summary>

```
[paste error]
```
</details>

## Environment
- Claude Code version: [e.g., 1.2.3]
- Loom version: [e.g., 0.1.0]
- OS: [e.g., macOS 14.0]
```

---

## Suggesting Enhancements

### Feature Request Template

```markdown
## Feature Description
[What feature do you want?]

## Use Case
[Why is this valuable? What problem does it solve?]

## Example
[Show how it would work]

## Alternatives Considered
[What alternatives did you consider?]
```

### Good Enhancement Suggestions

✅ **Specific:** "Add a 'debugger' subagent for fixing broken code"
❌ **Vague:** "Make it better"

✅ **Motivated:** Explains the problem it solves
❌ **Unmotivated:** No clear use case

✅ **Example-driven:** Shows how it would work
❌ **Abstract:** Hard to visualize

---

## Code Contributions

### What to Contribute

**High-value contributions:**
- New subagent types for specialized tasks
- Improvements to compilation logic
- Better convergence detection
- Optimization of orchestration
- Bug fixes with test cases

**Lower priority (but still welcome):**
- Code style improvements (unless fixing real issues)
- Minor refactoring without clear benefits
- Premature optimizations

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -main
   git checkout -b feature/your-feature-name
   ```

2. **Make focused changes**
   - One feature/fix per PR
   - Keep changes minimal and focused
   - Don't mix unrelated changes

3. **Test thoroughly**
   - Test with multiple prompts
   - Verify backward compatibility
   - Check edge cases

4. **Write good commit messages**
   ```
   Add weather-focused researcher subagent

   - Specializes in finding weather APIs and climate data
   - Includes pattern matching for weather-related keywords
   - Tested with weather dashboard example
   ```

5. **Submit PR with description**
   ```markdown
   ## Changes
   [What changed and why]

   ## Testing
   [How you tested it]

   ## Examples
   [Usage examples if applicable]

   Fixes #123
   ```

6. **Respond to feedback**
   - Address review comments
   - Update based on suggestions
   - Be open to discussion

### Code Style

**SKILL.md style:**
- Clear, concise instructions
- Code examples use Python
- Step-by-step format
- Explain the "why" not just "what"

**Documentation style:**
- Use markdown formatting
- Include code examples
- Show before/after when relevant
- Keep explanations beginner-friendly

---

## Documentation Improvements

### What to Improve

- **Clarity:** Simplify confusing explanations
- **Completeness:** Fill gaps in documentation
- **Examples:** Add real-world use cases
- **Accuracy:** Fix outdated information

### Documentation Structure

```
loom/
├── README.md              # Overview, installation, quick start
├── ARCHITECTURE.md        # Technical deep dive
├── CONTRIBUTING.md        # This file
├── examples/
│   ├── *.md              # Detailed examples
└── SKILL.md              # The skill itself
```

### Style Guide

- **Be concise** - Respect reader's time
- **Show, don't tell** - Examples over explanations
- **Progressive disclosure** - Simple first, advanced later
- **Active voice** - "Loom compiles prompts" not "Prompts are compiled by Loom"
- **Code blocks** - Always specify language for syntax highlighting

---

## Sharing Examples

### Creating Example Files

1. **Pick a real scenario** you've used Loom for

2. **Document the journey:**
   - Initial prompt
   - What Loom did in each iteration
   - Artifacts generated
   - Final results

3. **Show before/after:**
   - v1 vs v2 vs v3 compiled prompts
   - What improved in each iteration

4. **Explain takeaways:**
   - What worked well
   - What didn't
   - Lessons learned

### Example Template

```markdown
# Example: [Title]

## Scenario
[What task were you trying to accomplish?]

## Input Prompt
```
/loom [your prompt]
```

## Iteration 1
### Compiled Prompt v1
[Show compiled_v1.py]

### Execution
[What subagents ran? What happened?]

### Results
[What was produced? Any issues?]

## Iteration 2
[Repeat for iteration 2]

## Final Results
[Show final deliverables]

## Key Takeaways
[What did you learn?]
```

---

## Development Setup

### Prerequisites

- Claude Code (latest version)
- No other dependencies required

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/loom.git
cd loom

# Install the skill
cp SKILL.md ~/.claude/skills/loom.md

# Reload skills in Claude Code
/skills reload
```

### Testing Changes

```bash
# Test with a simple prompt
/loom build a hello world CLI

# Check artifacts
ls -la loom/
cat loom/compiled_v1.py
cat loom/outputs/*.py
cat loom/logs/iteration_1.md

# Test with a complex prompt
/loom perform security audit of authentication system

# Verify refinement loop
diff loom/compiled_v1.py loom/compiled_v2.py
```

---

## Style Guidelines

### Skill Instructions (SKILL.md)

```markdown
## Good Examples

✓ "Write to: loom/compiled_v1.py"
✓ "Spawn researcher to find APIs"
✓ "Apply patches to create v2"

## Bad Examples

❌ "Maybe write to a file" (vague)
❌ "Do some research" (non-specific)
❌ "Update the prompt somehow" (unclear)
```

### Documentation

```markdown
## Good Examples

✓ Clear headings with emoji (## 🔄 Refinement Loop)
✓ Code examples with language tags (```python)
✓ Short paragraphs (2-3 sentences max)
✓ Bullet points for lists
✓ Tables for comparisons

## Bad Examples

❌ Wall of text (hard to scan)
❌ No code examples (hard to understand)
❌ Vague descriptions (hard to follow)
```

### Commit Messages

```markdown
## Good Examples

✓ "Add performance-optimizer subagent type"
✓ "Fix compilation error for nested tasks"
✓ "Update README with Windows installation notes"

## Bad Examples

❌ "Update stuff"
❌ "Fix bug"
❌ "Changes"
```

---

## Community

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Questions, ideas, show-and-tell
- **Pull Requests:** Code review and discussion

### Code of Conduct

We expect all contributors to:
- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards others

Unacceptable behavior:
- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Spam or self-promotion

### Getting Help

**Stuck? Ask for help!**
- Open a [Discussion](../../discussions) for questions
- Tag maintainers in PRs if you need guidance
- Check existing issues for similar problems

---

## Recognition

Contributors will be:
- Listed in release notes
- Credited in documentation
- Thanked in the community

Significant contributions may lead to:
- Maintainer status
- Decision-making input
- Featured examples

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

Don't hesitate to ask! Open a [Discussion](../../discussions) or comment on an issue.

**Thank you for contributing to Loom!** 🎉
