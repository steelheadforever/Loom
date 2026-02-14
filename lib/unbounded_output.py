"""
Unbounded Output Handler for Loom-RLM
Manages large outputs (>10K lines) through splitting and indexing.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class OutputPart:
    """Represents a part of a split output."""
    part_number: int
    start_line: int
    end_line: int
    line_count: int
    file_path: str


class UnboundedOutputHandler:
    """
    Handles outputs that exceed normal size limits.

    Strategy:
    - Threshold: 10,000 lines
    - Split at: 10,000 lines per part
    - Create index file with navigation
    - Preserve line numbers across parts
    """

    # Threshold for unbounded output handling
    THRESHOLD_LINES = 10_000

    # Lines per part
    LINES_PER_PART = 10_000

    def __init__(self, base_path: str = "loom/unbounded_outputs"):
        """
        Initialize the unbounded output handler.

        Args:
            base_path: Base directory for unbounded outputs
        """
        self.base_path = base_path
        self.parts: List[OutputPart] = []

    def should_handle(self, content: str) -> bool:
        """
        Check if content should be handled as unbounded output.

        Args:
            content: Output content to check

        Returns:
            True if content exceeds threshold
        """
        line_count = content.count('\n') + 1
        return line_count > self.THRESHOLD_LINES

    def split_output(
        self,
        task_id: str,
        content: str,
        base_filename: str = None
    ) -> List[str]:
        """
        Split large output into manageable parts.

        Args:
            task_id: Task identifier
            content: Full output content
            base_filename: Base filename (default: task_id)

        Returns:
            List of file paths created
        """
        if base_filename is None:
            base_filename = task_id

        lines = content.split('\n')
        total_lines = len(lines)

        # Calculate number of parts needed
        num_parts = (total_lines + self.LINES_PER_PART - 1) // self.LINES_PER_PART

        created_files = []
        self.parts = []

        for part_num in range(num_parts):
            start_line = part_num * self.LINES_PER_PART
            end_line = min((part_num + 1) * self.LINES_PER_PART, total_lines)

            part_lines = lines[start_line:end_line]
            part_content = '\n'.join(part_lines)

            # Create filename for this part
            part_filename = f"{base_filename}_part_{part_num + 1}.py"
            part_path = f"{self.base_path}/{part_filename}"

            # Track part metadata
            part = OutputPart(
                part_number=part_num + 1,
                start_line=start_line + 1,  # 1-indexed
                end_line=end_line,  # 1-indexed
                line_count=len(part_lines),
                file_path=part_path
            )
            self.parts.append(part)

            # Add part header
            header = self._create_part_header(part, num_parts, task_id)
            full_content = header + part_content

            created_files.append((part_path, full_content))

        return created_files

    def _create_part_header(
        self,
        part: OutputPart,
        total_parts: int,
        task_id: str
    ) -> str:
        """
        Create header for a part file.

        Args:
            part: Part metadata
            total_parts: Total number of parts
            task_id: Task identifier

        Returns:
            Header string
        """
        return f"""# Part {part.part_number} of {total_parts}
# Task: {task_id}
# Lines: {part.start_line} - {part.end_line}
# See index file for navigation

"""

    def create_index_file(
        self,
        task_id: str,
        base_filename: str = None
    ) -> tuple[str, str]:
        """
        Create an index file for navigating parts.

        Args:
            task_id: Task identifier
            base_filename: Base filename (default: task_id)

        Returns:
            Tuple of (index_file_path, index_content)
        """
        if base_filename is None:
            base_filename = task_id

        index_filename = f"{base_filename}_index.py"
        index_path = f"{self.base_path}/{index_filename}"

        # Calculate total lines
        total_lines = sum(part.line_count for part in self.parts)

        # Create index content
        lines = [
            f'"""',
            f'Unbounded Output Index',
            f'Task: {task_id}',
            f'',
            f'This output was split into {len(self.parts)} parts due to size.',
            f'Total lines: {total_lines:,}',
            f'',
            f'Parts:',
        ]

        for part in self.parts:
            lines.append(
                f'  Part {part.part_number}: '
                f'Lines {part.start_line:,}-{part.end_line:,} '
                f'({part.line_count:,} lines) → {Path(part.file_path).name}'
            )

        lines.extend([
            f'',
            f'Navigation:',
            f'  - Use the part files above to view specific sections',
            f'  - Line numbers are preserved across parts',
            f'  - Each part has a header indicating its range',
            f'"""',
            f'',
            f'# UnboundedOutputIndex — pseudo-Python structured data (not executable)',
            f'',
            f'task_id = "{task_id}"',
            f'total_lines = {total_lines}',
            f'total_parts = {len(self.parts)}',
            f'',
            f'parts = [',
        ])

        for part in self.parts:
            lines.append(f'    {{')
            lines.append(f'        "part_number": {part.part_number},')
            lines.append(f'        "start_line": {part.start_line},')
            lines.append(f'        "end_line": {part.end_line},')
            lines.append(f'        "line_count": {part.line_count},')
            lines.append(f'        "file_path": "{part.file_path}"')
            lines.append(f'    }},')

        lines.extend([
            f']',
        ])

        index_content = '\n'.join(lines)

        return index_path, index_content

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the unbounded output.

        Returns:
            Dictionary with statistics
        """
        if not self.parts:
            return {
                "total_parts": 0,
                "total_lines": 0,
                "avg_lines_per_part": 0,
                "threshold": self.THRESHOLD_LINES
            }

        total_lines = sum(part.line_count for part in self.parts)
        avg_lines = total_lines / len(self.parts) if self.parts else 0

        return {
            "total_parts": len(self.parts),
            "total_lines": total_lines,
            "avg_lines_per_part": int(avg_lines),
            "threshold": self.THRESHOLD_LINES,
            "lines_per_part": self.LINES_PER_PART,
            "parts": [
                {
                    "part_number": part.part_number,
                    "lines": part.line_count,
                    "range": f"{part.start_line}-{part.end_line}"
                }
                for part in self.parts
            ]
        }

    def to_markdown(self) -> str:
        """
        Generate markdown report of unbounded output handling.

        Returns:
            Markdown-formatted report
        """
        from datetime import datetime

        stats = self.get_statistics()

        lines = [
            "# Unbounded Output Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Total Parts:** {stats['total_parts']}",
            f"- **Total Lines:** {stats['total_lines']:,}",
            f"- **Avg Lines/Part:** {stats['avg_lines_per_part']:,}",
            f"- **Threshold:** {stats['threshold']:,} lines",
            "",
        ]

        if stats['total_parts'] > 0:
            lines.extend([
                "## Part Breakdown",
                "",
                "| Part | Lines | Range |",
                "|------|-------|-------|",
            ])

            for part_info in stats['parts']:
                lines.append(
                    f"| {part_info['part_number']} | "
                    f"{part_info['lines']:,} | "
                    f"{part_info['range']} |"
                )

            lines.append("")

        lines.extend([
            "## Strategy",
            "",
            f"- **Splitting:** Outputs exceeding {self.THRESHOLD_LINES:,} lines are split",
            f"- **Part Size:** {self.LINES_PER_PART:,} lines per part",
            "- **Line Numbers:** Preserved across all parts",
            "- **Index File:** Created for easy navigation",
            "- **Headers:** Each part includes context header",
            "",
            "## Benefits",
            "",
            "- ✓ No size limits on subagent outputs",
            "- ✓ Easy navigation via index file",
            "- ✓ Line numbers preserved for referencing",
            "- ✓ Each part is independently readable",
            "",
        ])

        return "\n".join(lines)
