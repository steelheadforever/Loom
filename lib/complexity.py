"""
Complexity Calculator for Loom-RLM
Determines optimal iteration depth (3-10) based on task complexity.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ComplexityScore:
    """Result of complexity calculation."""
    overall_score: float  # 0.0-1.0
    max_iterations: int   # 3-10
    factors: Dict[str, float]
    reasoning: List[str]


class ComplexityCalculator:
    """
    Calculates task complexity and maps to optimal iteration depth.

    Factors:
    - Task count (30%): More tasks = higher complexity
    - Dependency depth (30%): Deeper dependencies = higher complexity
    - Input size (20%): Larger inputs = higher complexity
    - Task diversity (20%): More subagent types = higher complexity

    Mapping:
    - 0.0-0.3 → 3 iterations (simple)
    - 0.3-0.6 → 5 iterations (moderate)
    - 0.6-0.8 → 7 iterations (complex)
    - 0.8-1.0 → 10 iterations (very complex)
    """

    # Weights for each factor
    WEIGHT_TASK_COUNT = 0.30
    WEIGHT_DEPENDENCY_DEPTH = 0.30
    WEIGHT_INPUT_SIZE = 0.20
    WEIGHT_TASK_DIVERSITY = 0.20

    # Iteration mapping thresholds
    ITERATION_MAP = [
        (0.0, 0.3, 3),   # Simple: 3 iterations
        (0.3, 0.6, 5),   # Moderate: 5 iterations
        (0.6, 0.8, 7),   # Complex: 7 iterations
        (0.8, 1.0, 10),  # Very complex: 10 iterations
    ]

    def calculate(self, compiled_prompt: Dict[str, Any]) -> ComplexityScore:
        """
        Calculate complexity score and optimal iteration depth.

        Args:
            compiled_prompt: Compiled prompt dictionary with tasks, context, etc.

        Returns:
            ComplexityScore with overall score and max iterations
        """
        factors = {}
        reasoning = []

        # Factor 1: Task count (30%)
        task_count_score, task_count_reason = self._calculate_task_count_score(
            compiled_prompt
        )
        factors["task_count"] = task_count_score
        reasoning.append(task_count_reason)

        # Factor 2: Dependency depth (30%)
        dep_depth_score, dep_depth_reason = self._calculate_dependency_depth_score(
            compiled_prompt
        )
        factors["dependency_depth"] = dep_depth_score
        reasoning.append(dep_depth_reason)

        # Factor 3: Input size (20%)
        input_size_score, input_size_reason = self._calculate_input_size_score(
            compiled_prompt
        )
        factors["input_size"] = input_size_score
        reasoning.append(input_size_reason)

        # Factor 4: Task diversity (20%)
        diversity_score, diversity_reason = self._calculate_task_diversity_score(
            compiled_prompt
        )
        factors["task_diversity"] = diversity_score
        reasoning.append(diversity_reason)

        # Calculate weighted overall score
        overall_score = (
            task_count_score * self.WEIGHT_TASK_COUNT +
            dep_depth_score * self.WEIGHT_DEPENDENCY_DEPTH +
            input_size_score * self.WEIGHT_INPUT_SIZE +
            diversity_score * self.WEIGHT_TASK_DIVERSITY
        )

        # Map to iteration count
        max_iterations = self._map_score_to_iterations(overall_score)

        return ComplexityScore(
            overall_score=overall_score,
            max_iterations=max_iterations,
            factors=factors,
            reasoning=reasoning
        )

    def _calculate_task_count_score(
        self,
        compiled_prompt: Dict[str, Any]
    ) -> tuple[float, str]:
        """
        Calculate score based on number of tasks.

        Scale:
        - 1-2 tasks: 0.0 (simple)
        - 3-5 tasks: 0.5 (moderate)
        - 6-10 tasks: 0.8 (complex)
        - 10+ tasks: 1.0 (very complex)
        """
        tasks = compiled_prompt.get("tasks", [])
        task_count = len(tasks)

        if task_count <= 2:
            score = 0.0
            level = "simple"
        elif task_count <= 5:
            score = 0.5
            level = "moderate"
        elif task_count <= 10:
            score = 0.8
            level = "complex"
        else:
            score = 1.0
            level = "very complex"

        reason = f"Task count: {task_count} tasks ({level})"
        return score, reason

    def _calculate_dependency_depth_score(
        self,
        compiled_prompt: Dict[str, Any]
    ) -> tuple[float, str]:
        """
        Calculate score based on dependency graph depth.

        Uses topological levels:
        - 1 level: 0.0 (no dependencies)
        - 2 levels: 0.3 (simple chain)
        - 3 levels: 0.6 (moderate chain)
        - 4 levels: 0.8 (complex chain)
        - 5+ levels: 1.0 (very complex chain)
        """
        tasks = compiled_prompt.get("tasks", [])

        if not tasks:
            return 0.0, "No tasks to analyze"

        # Build dependency graph
        task_deps = {}
        for task in tasks:
            task_id = task.get("id")
            depends_on = task.get("depends_on", [])
            task_deps[task_id] = depends_on

        # Calculate depth using topological sort
        depth = self._calculate_graph_depth(task_deps)

        if depth <= 1:
            score = 0.0
            level = "no dependencies"
        elif depth == 2:
            score = 0.3
            level = "simple chain"
        elif depth == 3:
            score = 0.6
            level = "moderate chain"
        elif depth == 4:
            score = 0.8
            level = "complex chain"
        else:
            score = 1.0
            level = "very complex chain"

        reason = f"Dependency depth: {depth} levels ({level})"
        return score, reason

    def _calculate_graph_depth(self, task_deps: Dict[str, List[str]]) -> int:
        """
        Calculate maximum depth of dependency graph.

        Args:
            task_deps: Dict mapping task_id to list of dependencies

        Returns:
            Maximum depth (1 = no dependencies)
        """
        if not task_deps:
            return 0

        # Calculate level for each task
        task_levels = {}

        def get_level(task_id: str) -> int:
            if task_id in task_levels:
                return task_levels[task_id]

            deps = task_deps.get(task_id, [])
            if not deps:
                task_levels[task_id] = 1
                return 1

            # Level is 1 + max level of dependencies
            max_dep_level = max(
                get_level(dep) for dep in deps if dep in task_deps
            )
            task_levels[task_id] = max_dep_level + 1
            return task_levels[task_id]

        # Calculate levels for all tasks
        for task_id in task_deps:
            get_level(task_id)

        return max(task_levels.values()) if task_levels else 1

    def _calculate_input_size_score(
        self,
        compiled_prompt: Dict[str, Any]
    ) -> tuple[float, str]:
        """
        Calculate score based on input size.

        Scale:
        - <10K chars: 0.0 (small)
        - 10K-50K chars: 0.3 (medium)
        - 50K-100K chars: 0.6 (large)
        - 100K-200K chars: 0.8 (very large)
        - 200K+ chars: 1.0 (massive)
        """
        try:
            from .cost_tracker import CostTracker
        except ImportError:
            from cost_tracker import CostTracker

        # Estimate input size from original prompt
        original = compiled_prompt.get("original", "")
        char_count = len(original)
        token_count = CostTracker.estimate_tokens(original)

        if char_count < 10_000:
            score = 0.0
            level = "small"
        elif char_count < 50_000:
            score = 0.3
            level = "medium"
        elif char_count < 100_000:
            score = 0.6
            level = "large"
        elif char_count < 200_000:
            score = 0.8
            level = "very large"
        else:
            score = 1.0
            level = "massive"

        reason = f"Input size: {token_count:,} tokens ({level})"
        return score, reason

    def _calculate_task_diversity_score(
        self,
        compiled_prompt: Dict[str, Any]
    ) -> tuple[float, str]:
        """
        Calculate score based on variety of task types/requirements.

        Measures:
        - Number of unique capabilities required
        - Number of unique subagent roles needed

        Scale:
        - 1 role: 0.0 (single focus)
        - 2 roles: 0.3 (dual focus)
        - 3 roles: 0.6 (diverse)
        - 4 roles: 0.8 (very diverse)
        - 5+ roles: 1.0 (highly diverse)
        """
        tasks = compiled_prompt.get("tasks", [])

        if not tasks:
            return 0.0, "No tasks to analyze"

        # Collect unique capabilities
        capabilities = set()
        for task in tasks:
            task_requires = task.get("requires", [])
            capabilities.update(task_requires)

        unique_count = len(capabilities)

        if unique_count <= 1:
            score = 0.0
            level = "single focus"
        elif unique_count == 2:
            score = 0.3
            level = "dual focus"
        elif unique_count == 3:
            score = 0.6
            level = "diverse"
        elif unique_count == 4:
            score = 0.8
            level = "very diverse"
        else:
            score = 1.0
            level = "highly diverse"

        reason = f"Task diversity: {unique_count} unique capabilities ({level})"
        return score, reason

    def _map_score_to_iterations(self, score: float) -> int:
        """
        Map complexity score to iteration count.

        Args:
            score: Complexity score (0.0-1.0)

        Returns:
            Recommended iteration count (3-10)
        """
        for min_score, max_score, iterations in self.ITERATION_MAP:
            if min_score <= score < max_score:
                return iterations

        # Edge case: score exactly 1.0
        return self.ITERATION_MAP[-1][2]

    def to_markdown(self, complexity_score: ComplexityScore) -> str:
        """
        Generate markdown report of complexity analysis.

        Args:
            complexity_score: Result from calculate()

        Returns:
            Markdown-formatted complexity report
        """
        from datetime import datetime

        lines = [
            "# Complexity Analysis",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Overall Complexity:** {complexity_score.overall_score:.2f} / 1.0",
            f"- **Recommended Iterations:** {complexity_score.max_iterations}",
            "",
        ]

        # Add complexity level description
        if complexity_score.overall_score < 0.3:
            level = "Simple"
            description = "Straightforward task with few dependencies"
        elif complexity_score.overall_score < 0.6:
            level = "Moderate"
            description = "Multi-step task with some dependencies"
        elif complexity_score.overall_score < 0.8:
            level = "Complex"
            description = "Intricate task with many dependencies"
        else:
            level = "Very Complex"
            description = "Highly sophisticated task requiring extensive iteration"

        lines.extend([
            f"**Complexity Level:** {level}",
            f"**Description:** {description}",
            "",
        ])

        # Add factor breakdown
        lines.extend([
            "## Factor Breakdown",
            "",
            "| Factor | Score | Weight | Contribution |",
            "|--------|-------|--------|--------------|",
        ])

        factors = complexity_score.factors
        weights = {
            "task_count": self.WEIGHT_TASK_COUNT,
            "dependency_depth": self.WEIGHT_DEPENDENCY_DEPTH,
            "input_size": self.WEIGHT_INPUT_SIZE,
            "task_diversity": self.WEIGHT_TASK_DIVERSITY
        }

        for factor_name, factor_score in factors.items():
            weight = weights.get(factor_name, 0)
            contribution = factor_score * weight
            lines.append(
                f"| {factor_name.replace('_', ' ').title()} | "
                f"{factor_score:.2f} | {weight:.0%} | {contribution:.2f} |"
            )

        lines.append("")

        # Add reasoning
        if complexity_score.reasoning:
            lines.extend([
                "## Analysis Details",
                "",
            ])
            for reason in complexity_score.reasoning:
                lines.append(f"- {reason}")
            lines.append("")

        # Add iteration strategy
        lines.extend([
            "## Iteration Strategy",
            "",
            f"Based on complexity score of {complexity_score.overall_score:.2f}, "
            f"the system will run up to **{complexity_score.max_iterations} iterations**.",
            "",
            "This allows:",
            "- Initial exploration and compilation",
            "- Multiple refinement cycles",
            "- Adequate time for complex dependencies to resolve",
            "- Quality validation and optimization",
            "",
        ])

        return "\n".join(lines)
