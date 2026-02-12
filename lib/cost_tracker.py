"""
Cost Tracker for Loom-RLM
Tracks token usage and costs across subagent calls with optimization recommendations.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SubagentCall:
    """Record of a single subagent invocation."""
    role: str
    task_id: str
    input_tokens: int
    output_tokens: int
    timestamp: str
    iteration: int


@dataclass
class CostTracker:
    """
    Tracks token usage and costs for Loom-RLM execution.

    Pricing (Claude Sonnet 4.5):
    - Input: $3.00 per 1M tokens
    - Output: $15.00 per 1M tokens
    """

    # Pricing constants (per million tokens)
    INPUT_PRICE_PER_M = 3.00
    OUTPUT_PRICE_PER_M = 15.00

    # Token estimation multiplier (chars to tokens)
    CHAR_TO_TOKEN_MULTIPLIER = 1.3

    calls: List[SubagentCall] = field(default_factory=list)
    filtering_savings: Dict[str, int] = field(default_factory=dict)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate tokens from character count.
        Uses conservative 1.3 multiplier for safety.

        Args:
            text: Input text to estimate

        Returns:
            Estimated token count
        """
        return int(len(text) / CostTracker.CHAR_TO_TOKEN_MULTIPLIER)

    def track_subagent_call(
        self,
        role: str,
        task_id: str,
        input_text: str,
        output_text: str,
        iteration: int
    ) -> None:
        """
        Track a subagent invocation.

        Args:
            role: Subagent role (researcher, coder, etc.)
            task_id: Task identifier
            input_text: Input prompt text
            output_text: Generated output text
            iteration: Iteration number
        """
        input_tokens = self.estimate_tokens(input_text)
        output_tokens = self.estimate_tokens(output_text)

        call = SubagentCall(
            role=role,
            task_id=task_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            timestamp=datetime.now().isoformat(),
            iteration=iteration
        )

        self.calls.append(call)

    def track_filtering_savings(self, version: int, tokens_removed: int) -> None:
        """
        Track tokens saved through filtering.

        Args:
            version: Compilation version
            tokens_removed: Number of tokens filtered out
        """
        self.filtering_savings[f"v{version}"] = tokens_removed

    def get_total_tokens(self) -> Tuple[int, int]:
        """
        Get total input and output tokens across all calls.

        Returns:
            Tuple of (total_input_tokens, total_output_tokens)
        """
        total_input = sum(call.input_tokens for call in self.calls)
        total_output = sum(call.output_tokens for call in self.calls)
        return total_input, total_output

    def get_total_cost(self) -> float:
        """
        Calculate total cost in USD.

        Returns:
            Total cost in dollars
        """
        total_input, total_output = self.get_total_tokens()

        input_cost = (total_input / 1_000_000) * self.INPUT_PRICE_PER_M
        output_cost = (total_output / 1_000_000) * self.OUTPUT_PRICE_PER_M

        return input_cost + output_cost

    def get_cost_by_role(self) -> Dict[str, float]:
        """
        Break down costs by subagent role.

        Returns:
            Dictionary mapping role to cost in USD
        """
        role_costs = {}

        for call in self.calls:
            input_cost = (call.input_tokens / 1_000_000) * self.INPUT_PRICE_PER_M
            output_cost = (call.output_tokens / 1_000_000) * self.OUTPUT_PRICE_PER_M
            total_cost = input_cost + output_cost

            if call.role not in role_costs:
                role_costs[call.role] = 0.0
            role_costs[call.role] += total_cost

        return role_costs

    def get_cost_by_iteration(self) -> Dict[int, float]:
        """
        Break down costs by iteration.

        Returns:
            Dictionary mapping iteration number to cost in USD
        """
        iteration_costs = {}

        for call in self.calls:
            input_cost = (call.input_tokens / 1_000_000) * self.INPUT_PRICE_PER_M
            output_cost = (call.output_tokens / 1_000_000) * self.OUTPUT_PRICE_PER_M
            total_cost = input_cost + output_cost

            if call.iteration not in iteration_costs:
                iteration_costs[call.iteration] = 0.0
            iteration_costs[call.iteration] += total_cost

        return iteration_costs

    def get_filtering_impact(self) -> Tuple[int, float]:
        """
        Calculate total impact of filtering.

        Returns:
            Tuple of (total_tokens_saved, estimated_cost_savings_usd)
        """
        total_saved = sum(self.filtering_savings.values())

        # Assume filtered tokens would have been input tokens
        cost_saved = (total_saved / 1_000_000) * self.INPUT_PRICE_PER_M

        return total_saved, cost_saved

    def get_optimization_recommendations(self) -> List[str]:
        """
        Generate optimization recommendations based on usage patterns.

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Analyze role distribution
        role_costs = self.get_cost_by_role()
        if role_costs:
            max_role = max(role_costs.items(), key=lambda x: x[1])
            max_role_name, max_role_cost = max_role
            total_cost = self.get_total_cost()

            if max_role_cost > total_cost * 0.5:
                recommendations.append(
                    f"The '{max_role_name}' role accounts for "
                    f"{(max_role_cost/total_cost*100):.1f}% of costs. "
                    f"Consider optimizing {max_role_name} prompts or reducing calls."
                )

        # Analyze filtering effectiveness
        tokens_saved, cost_saved = self.get_filtering_impact()
        if tokens_saved > 0:
            total_input, _ = self.get_total_tokens()
            reduction_pct = (tokens_saved / (total_input + tokens_saved)) * 100
            recommendations.append(
                f"Filtering removed {tokens_saved:,} tokens ({reduction_pct:.1f}%), "
                f"saving approximately ${cost_saved:.4f}."
            )

            if reduction_pct < 15:
                recommendations.append(
                    "Filtering impact is low (<15%). Consider more aggressive filtering "
                    "or using chunking for large inputs."
                )
        else:
            recommendations.append(
                "No filtering applied. For verbose inputs, filtering can reduce costs by 20-40%."
            )

        # Analyze iteration costs
        iteration_costs = self.get_cost_by_iteration()
        if len(iteration_costs) > 1:
            cost_trend = []
            for i in sorted(iteration_costs.keys()):
                cost_trend.append(iteration_costs[i])

            if len(cost_trend) >= 2 and cost_trend[-1] > cost_trend[0] * 1.5:
                recommendations.append(
                    "Later iterations are significantly more expensive. "
                    "Consider better initial compilation or earlier convergence criteria."
                )

        # Token usage alerts
        total_input, total_output = self.get_total_tokens()
        if total_input > 500_000:
            recommendations.append(
                f"High input token usage ({total_input:,}). "
                "Consider enabling chunking for inputs >50K tokens."
            )

        if total_output > 100_000:
            recommendations.append(
                f"High output token usage ({total_output:,}). "
                "Review if subagents are being too verbose in their outputs."
            )

        return recommendations if recommendations else ["No specific optimizations recommended."]

    def to_markdown(self) -> str:
        """
        Generate a markdown report of costs and recommendations.

        Returns:
            Markdown-formatted cost report
        """
        total_input, total_output = self.get_total_tokens()
        total_cost = self.get_total_cost()
        role_costs = self.get_cost_by_role()
        iteration_costs = self.get_cost_by_iteration()
        tokens_saved, cost_saved = self.get_filtering_impact()

        lines = [
            "# Loom-RLM Cost Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Total Input Tokens:** {total_input:,}",
            f"- **Total Output Tokens:** {total_output:,}",
            f"- **Total Tokens:** {total_input + total_output:,}",
            f"- **Total Cost:** ${total_cost:.4f}",
            "",
        ]

        if tokens_saved > 0:
            lines.extend([
                "## Filtering Impact",
                "",
                f"- **Tokens Removed:** {tokens_saved:,}",
                f"- **Cost Saved:** ${cost_saved:.4f}",
                f"- **Reduction:** {(tokens_saved/(total_input+tokens_saved)*100):.1f}%",
                "",
            ])

        if role_costs:
            lines.extend([
                "## Cost by Role",
                "",
            ])
            for role, cost in sorted(role_costs.items(), key=lambda x: x[1], reverse=True):
                pct = (cost / total_cost * 100) if total_cost > 0 else 0
                lines.append(f"- **{role}:** ${cost:.4f} ({pct:.1f}%)")
            lines.append("")

        if iteration_costs:
            lines.extend([
                "## Cost by Iteration",
                "",
            ])
            for iteration in sorted(iteration_costs.keys()):
                cost = iteration_costs[iteration]
                pct = (cost / total_cost * 100) if total_cost > 0 else 0
                lines.append(f"- **Iteration {iteration}:** ${cost:.4f} ({pct:.1f}%)")
            lines.append("")

        recommendations = self.get_optimization_recommendations()
        if recommendations:
            lines.extend([
                "## Optimization Recommendations",
                "",
            ])
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        return "\n".join(lines)
