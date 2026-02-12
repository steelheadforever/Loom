"""
Filtering Strategy for Loom-RLM
Pre-processes compiled prompts to reduce context while preserving critical information.
Target: 20-40% token reduction (moderate filtering).
"""

from typing import Dict, List, Any
import re


class FilterStrategy:
    """
    Applies moderate filtering to reduce context overhead.

    Filtering targets:
    - Redundant task descriptions
    - Verbose examples
    - Low-priority context
    - Repetitive constraints

    Preserves:
    - Task IDs and dependencies
    - Core requirements
    - Security constraints
    - Critical context
    """

    # Target reduction range
    MIN_REDUCTION_PCT = 20
    MAX_REDUCTION_PCT = 40

    def __init__(self):
        self.stats = {
            "original_size": 0,
            "filtered_size": 0,
            "tokens_removed": 0,
            "reduction_pct": 0.0,
            "filters_applied": []
        }

    def analyze(self, compiled_prompt: str) -> Dict[str, Any]:
        """
        Analyze compiled prompt and estimate filtering impact.

        Args:
            compiled_prompt: The compiled prompt content

        Returns:
            Analysis dict with estimated savings and filter plan
        """
        try:
            from .cost_tracker import CostTracker
        except ImportError:
            from cost_tracker import CostTracker

        original_tokens = CostTracker.estimate_tokens(compiled_prompt)

        # Identify filterable content
        analysis = {
            "original_tokens": original_tokens,
            "filterable_content": [],
            "estimated_savings": 0,
            "recommended_filters": []
        }

        # Check for verbose examples in docstrings
        example_matches = re.findall(
            r'"""[^"]*?Example[^"]*?"""',
            compiled_prompt,
            re.DOTALL | re.IGNORECASE
        )
        if example_matches:
            example_tokens = sum(CostTracker.estimate_tokens(ex) for ex in example_matches)
            # Can safely remove 60% of verbose examples
            savings = int(example_tokens * 0.6)
            analysis["filterable_content"].append({
                "type": "verbose_examples",
                "count": len(example_matches),
                "tokens": example_tokens,
                "potential_savings": savings
            })
            analysis["estimated_savings"] += savings
            analysis["recommended_filters"].append("compress_examples")

        # Check for repetitive context entries
        context_pattern = r'"[^"]+"\s*:\s*"[^"]+"'
        context_matches = re.findall(context_pattern, compiled_prompt)
        if len(context_matches) > 10:
            # Deduplicate similar context entries
            unique_contexts = set(context_matches)
            if len(context_matches) - len(unique_contexts) > 3:
                redundant_tokens = CostTracker.estimate_tokens(
                    "".join(context_matches[len(unique_contexts):])
                )
                analysis["filterable_content"].append({
                    "type": "redundant_context",
                    "count": len(context_matches) - len(unique_contexts),
                    "tokens": redundant_tokens,
                    "potential_savings": redundant_tokens
                })
                analysis["estimated_savings"] += redundant_tokens
                analysis["recommended_filters"].append("deduplicate_context")

        # Check for overly detailed task descriptions
        task_desc_pattern = r'"description"\s*:\s*"([^"]{200,})"'
        long_descs = re.findall(task_desc_pattern, compiled_prompt)
        if long_descs:
            desc_tokens = sum(CostTracker.estimate_tokens(d) for d in long_descs)
            # Can compress long descriptions by 30%
            savings = int(desc_tokens * 0.3)
            analysis["filterable_content"].append({
                "type": "verbose_descriptions",
                "count": len(long_descs),
                "tokens": desc_tokens,
                "potential_savings": savings
            })
            analysis["estimated_savings"] += savings
            analysis["recommended_filters"].append("compress_descriptions")

        # Calculate projected reduction percentage
        analysis["reduction_pct"] = (
            analysis["estimated_savings"] / original_tokens * 100
            if original_tokens > 0 else 0
        )

        return analysis

    def apply(self, compiled_prompt: str) -> str:
        """
        Apply moderate filtering to reduce context.

        Args:
            compiled_prompt: Original compiled prompt content

        Returns:
            Filtered compiled prompt
        """
        try:
            from .cost_tracker import CostTracker
        except ImportError:
            from cost_tracker import CostTracker

        self.stats["original_size"] = len(compiled_prompt)
        original_tokens = CostTracker.estimate_tokens(compiled_prompt)
        self.stats["filters_applied"] = []

        filtered = compiled_prompt

        # Filter 1: Compress verbose examples
        filtered = self._compress_examples(filtered)

        # Filter 2: Deduplicate redundant context
        filtered = self._deduplicate_context(filtered)

        # Filter 3: Compress overly detailed descriptions
        filtered = self._compress_descriptions(filtered)

        # Filter 4: Remove low-priority comments
        filtered = self._remove_verbose_comments(filtered)

        # Calculate final stats
        self.stats["filtered_size"] = len(filtered)
        filtered_tokens = CostTracker.estimate_tokens(filtered)
        self.stats["tokens_removed"] = original_tokens - filtered_tokens
        self.stats["reduction_pct"] = (
            (self.stats["tokens_removed"] / original_tokens * 100)
            if original_tokens > 0 else 0
        )

        return filtered

    def _compress_examples(self, text: str) -> str:
        """
        Compress verbose examples in docstrings.
        Keeps first example, shortens others.
        """
        def compress_example(match):
            example_text = match.group(0)
            # If example is long (>300 chars), keep only first 150 chars
            if len(example_text) > 300:
                compressed = example_text[:150] + "...\n    \"\"\""
                return compressed
            return example_text

        pattern = r'"""[^"]*?Example[^"]*?"""'
        filtered = re.sub(pattern, compress_example, text, flags=re.DOTALL | re.IGNORECASE)

        if filtered != text:
            self.stats["filters_applied"].append("compress_examples")

        return filtered

    def _deduplicate_context(self, text: str) -> str:
        """
        Remove duplicate context entries while preserving order.
        """
        # Extract context section
        context_pattern = r'(context\s*=\s*{[^}]+})'
        match = re.search(context_pattern, text, re.DOTALL)

        if not match:
            return text

        context_section = match.group(1)

        # Find all key-value pairs
        kv_pattern = r'"([^"]+)"\s*:\s*("[^"]*"|\[[^\]]*\]|{[^}]*})'
        pairs = re.findall(kv_pattern, context_section)

        # Deduplicate while preserving order
        seen = set()
        unique_pairs = []
        for key, value in pairs:
            if key not in seen:
                seen.add(key)
                unique_pairs.append((key, value))

        # Reconstruct context section if we removed duplicates
        if len(unique_pairs) < len(pairs):
            new_context = "context = {\n"
            for key, value in unique_pairs:
                new_context += f'        "{key}": {value},\n'
            new_context += "    }"

            filtered = text.replace(context_section, new_context)
            self.stats["filters_applied"].append("deduplicate_context")
            return filtered

        return text

    def _compress_descriptions(self, text: str) -> str:
        """
        Compress overly verbose task descriptions.
        Target: reduce descriptions >200 chars by 30%.
        """
        def compress_desc(match):
            desc = match.group(1)
            if len(desc) > 200:
                # Keep first 70% of description
                keep_length = int(len(desc) * 0.7)
                return f'"description": "{desc[:keep_length]}..."'
            return match.group(0)

        pattern = r'"description"\s*:\s*"([^"]{200,})"'
        filtered = re.sub(pattern, compress_desc, text)

        if filtered != text:
            self.stats["filters_applied"].append("compress_descriptions")

        return filtered

    def _remove_verbose_comments(self, text: str) -> str:
        """
        Remove non-critical comments (not security or validation related).
        """
        lines = text.split("\n")
        filtered_lines = []

        for line in lines:
            # Keep security-related comments
            if "SECURITY" in line.upper() or "CRITICAL" in line.upper():
                filtered_lines.append(line)
                continue

            # Keep short comments (< 80 chars)
            if "#" in line and len(line.strip()) < 80:
                filtered_lines.append(line)
                continue

            # Remove verbose comments (>80 chars, not security-related)
            if "#" in line and len(line.strip()) >= 80:
                # Keep the code part, remove the comment
                code_part = line.split("#")[0]
                if code_part.strip():
                    filtered_lines.append(code_part.rstrip())
                continue

            # Keep non-comment lines
            filtered_lines.append(line)

        filtered = "\n".join(filtered_lines)

        if len(filtered) < len(text):
            self.stats["filters_applied"].append("remove_verbose_comments")

        return filtered

    def get_stats(self) -> Dict[str, Any]:
        """
        Get filtering statistics.

        Returns:
            Dictionary with filtering stats
        """
        return self.stats.copy()

    def to_markdown(self) -> str:
        """
        Generate markdown report of filtering decisions.

        Returns:
            Markdown-formatted filtering report
        """
        from datetime import datetime

        lines = [
            "# Filtering Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Original Size:** {self.stats['original_size']:,} characters",
            f"- **Filtered Size:** {self.stats['filtered_size']:,} characters",
            f"- **Tokens Removed:** {self.stats['tokens_removed']:,}",
            f"- **Reduction:** {self.stats['reduction_pct']:.1f}%",
            "",
        ]

        if self.stats["filters_applied"]:
            lines.extend([
                "## Filters Applied",
                "",
            ])
            for filter_name in self.stats["filters_applied"]:
                lines.append(f"- `{filter_name}`")
            lines.append("")

        # Check if reduction is in target range
        reduction = self.stats["reduction_pct"]
        if self.MIN_REDUCTION_PCT <= reduction <= self.MAX_REDUCTION_PCT:
            lines.extend([
                "## Status",
                "",
                f"✓ Filtering achieved target reduction ({self.MIN_REDUCTION_PCT}-{self.MAX_REDUCTION_PCT}%)",
                "",
            ])
        elif reduction < self.MIN_REDUCTION_PCT:
            lines.extend([
                "## Status",
                "",
                f"⚠ Filtering below target ({reduction:.1f}% < {self.MIN_REDUCTION_PCT}%)",
                "Consider more aggressive filtering or input is already concise.",
                "",
            ])
        else:
            lines.extend([
                "## Status",
                "",
                f"⚠ Filtering above target ({reduction:.1f}% > {self.MAX_REDUCTION_PCT}%)",
                "Risk of removing critical information. Review filtered output.",
                "",
            ])

        return "\n".join(lines)
