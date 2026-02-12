"""
Chunking Strategy for Loom-RLM
Handles large inputs (50K+ tokens) through uniform chunking with sequential merging.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re


@dataclass
class Chunk:
    """Represents a single chunk of the input."""
    chunk_id: int
    content: str
    start_char: int
    end_char: int
    overlap_with_next: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkingConfig:
    """Configuration for chunking strategy."""
    chunk_size_tokens: int = 50_000
    overlap_tokens: int = 5_000
    strategy: str = "uniform"  # uniform, semantic, or adaptive
    merge_strategy: str = "sequential"  # sequential or parallel


class ChunkingStrategy:
    """
    Handles large input processing through intelligent chunking.

    Strategy:
    - Uniform division: Split at regular intervals
    - Overlap: 5K tokens between chunks for context continuity
    - Sequential merge: Chunk N sees results from chunk N-1
    """

    # Threshold for when to activate chunking
    CHUNKING_THRESHOLD_TOKENS = 50_000

    def __init__(self, config: Optional[ChunkingConfig] = None):
        self.config = config or ChunkingConfig()
        self.chunks: List[Chunk] = []
        self.metadata: Dict[str, Any] = {}

    def should_chunk(self, prompt: str) -> bool:
        """
        Determine if input should be chunked.

        Args:
            prompt: Input prompt text

        Returns:
            True if chunking is needed
        """
        try:
            from .cost_tracker import CostTracker
        except ImportError:
            from cost_tracker import CostTracker

        estimated_tokens = CostTracker.estimate_tokens(prompt)
        return estimated_tokens > self.CHUNKING_THRESHOLD_TOKENS

    def create_chunks(self, prompt: str) -> List[Chunk]:
        """
        Split prompt into chunks with overlap.

        Args:
            prompt: Full input prompt

        Returns:
            List of Chunk objects
        """
        try:
            from .cost_tracker import CostTracker
        except ImportError:
            from cost_tracker import CostTracker

        total_tokens = CostTracker.estimate_tokens(prompt)
        total_chars = len(prompt)

        # Calculate chunk parameters
        chars_per_token = total_chars / total_tokens if total_tokens > 0 else 1.3
        chunk_size_chars = int(self.config.chunk_size_tokens * chars_per_token)
        overlap_chars = int(self.config.overlap_tokens * chars_per_token)

        # Create chunks
        chunks = []
        chunk_id = 0
        start_char = 0

        while start_char < total_chars:
            end_char = min(start_char + chunk_size_chars, total_chars)

            # Try to break at natural boundaries (paragraph, sentence)
            if end_char < total_chars:
                end_char = self._find_break_point(prompt, end_char, chunk_size_chars)

            # Extract chunk content
            chunk_content = prompt[start_char:end_char]

            # Calculate overlap with next chunk
            overlap_with_next = overlap_chars if end_char < total_chars else 0

            chunk = Chunk(
                chunk_id=chunk_id,
                content=chunk_content,
                start_char=start_char,
                end_char=end_char,
                overlap_with_next=overlap_with_next,
                metadata={
                    "estimated_tokens": CostTracker.estimate_tokens(chunk_content),
                    "char_count": len(chunk_content),
                    "is_first": chunk_id == 0,
                    "is_last": end_char >= total_chars
                }
            )

            chunks.append(chunk)
            chunk_id += 1

            # Move to next chunk with overlap
            start_char = end_char - overlap_with_next

        self.chunks = chunks

        # Store metadata
        self.metadata = {
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "total_chars": total_chars,
            "chunk_size_tokens": self.config.chunk_size_tokens,
            "overlap_tokens": self.config.overlap_tokens,
            "strategy": self.config.strategy,
            "merge_strategy": self.config.merge_strategy
        }

        return chunks

    def _find_break_point(self, text: str, target_pos: int, max_search: int) -> int:
        """
        Find a natural break point near target position.

        Priority:
        1. Double newline (paragraph break)
        2. Single newline (line break)
        3. Period + space (sentence break)
        4. Comma + space (clause break)
        5. Space (word break)
        6. Target position (if no break found)

        Args:
            text: Full text
            target_pos: Desired break position
            max_search: Maximum chars to search backward

        Returns:
            Optimal break position
        """
        search_start = max(0, target_pos - max_search // 2)
        search_end = min(len(text), target_pos + max_search // 2)
        search_region = text[search_start:search_end]

        # Calculate position relative to search region
        relative_target = target_pos - search_start

        # Try to find best break point
        break_patterns = [
            (r'\n\n', 2),      # Paragraph break
            (r'\n', 1),        # Line break
            (r'\. ', 2),       # Sentence break
            (r', ', 2),        # Clause break
            (r' ', 1)          # Word break
        ]

        best_pos = None
        best_distance = float('inf')

        for pattern, offset in break_patterns:
            for match in re.finditer(pattern, search_region):
                match_pos = match.start() + offset
                distance = abs(match_pos - relative_target)

                if distance < best_distance:
                    best_distance = distance
                    best_pos = match_pos

            # If we found a good break, use it
            if best_pos is not None and best_distance < max_search // 4:
                return search_start + best_pos

        # No good break found, use target position
        return target_pos

    def merge_chunk_results(
        self,
        chunk_results: List[Dict[str, Any]],
        original_prompt: str
    ) -> Dict[str, Any]:
        """
        Merge results from multiple chunks.

        Sequential strategy:
        - Chunk 1 processes with base context
        - Chunk 2 sees Chunk 1's results as context
        - Chunk 3 sees Chunk 1+2's results, etc.

        Args:
            chunk_results: List of results from each chunk
            original_prompt: Original user prompt

        Returns:
            Merged CompiledPrompt dict
        """
        if not chunk_results:
            return {}

        # Start with first chunk's results
        merged = {
            "version": 1,
            "original": original_prompt,
            "intent": chunk_results[0].get("intent", {}),
            "tasks": [],
            "context": {
                "chunked": True,
                "total_chunks": len(chunk_results),
                "merge_strategy": self.config.merge_strategy
            },
            "deliverables": []
        }

        # Merge tasks from all chunks (sequential context)
        task_id_offset = 0
        for chunk_idx, chunk_result in enumerate(chunk_results):
            chunk_tasks = chunk_result.get("tasks", [])

            # Update task IDs to be globally unique
            for task in chunk_tasks:
                # Prefix task_id with chunk number
                original_id = task["id"]
                task["id"] = f"chunk{chunk_idx}_{original_id}"

                # Update dependency references
                if "depends_on" in task:
                    updated_deps = []
                    for dep in task["depends_on"]:
                        # If dependency is from same chunk, prefix it
                        if not dep.startswith("chunk"):
                            updated_deps.append(f"chunk{chunk_idx}_{dep}")
                        else:
                            updated_deps.append(dep)
                    task["depends_on"] = updated_deps

                # Add chunk metadata
                task["chunk_id"] = chunk_idx
                task["chunk_context"] = f"Processes chunk {chunk_idx + 1}/{len(chunk_results)}"

                merged["tasks"].append(task)

            # Merge context (sequential: later chunks build on earlier)
            chunk_context = chunk_result.get("context", {})
            for key, value in chunk_context.items():
                if key not in merged["context"]:
                    merged["context"][key] = value
                elif isinstance(value, list):
                    # Append to list
                    if key not in merged["context"]:
                        merged["context"][key] = []
                    merged["context"][key].extend(value)
                elif isinstance(value, dict):
                    # Merge dicts
                    if key not in merged["context"]:
                        merged["context"][key] = {}
                    merged["context"][key].update(value)

            # Merge deliverables
            chunk_deliverables = chunk_result.get("deliverables", [])
            merged["deliverables"].extend(chunk_deliverables)

        # Deduplicate deliverables
        merged["deliverables"] = list(set(merged["deliverables"]))

        # Add chunking metadata
        merged["chunking_metadata"] = {
            "total_chunks": len(chunk_results),
            "merge_strategy": self.config.merge_strategy,
            "chunk_boundaries": [
                {
                    "chunk_id": chunk.chunk_id,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "tokens": chunk.metadata.get("estimated_tokens", 0)
                }
                for chunk in self.chunks
            ]
        }

        return merged

    def get_chunk_metadata_python(self) -> str:
        """
        Generate pseudo-Python structured data for chunks_metadata.py.

        Returns:
            Pseudo-Python structured data as string
        """
        lines = [
            f'# ChunkingMetadata — pseudo-Python structured data (not executable)',
            f'# Auto-generated by ChunkingStrategy — {self.metadata.get("total_chunks", 0)} chunks',
            "",
        ]

        # Add configuration
        lines.append("config = {")
        for key, value in self.metadata.items():
            if isinstance(value, str):
                lines.append(f'    "{key}": "{value}",')
            else:
                lines.append(f'    "{key}": {value},')
        lines.append("}")
        lines.append("")

        # Add chunk details
        lines.append("chunks = [")
        for chunk in self.chunks:
            lines.append("    {")
            lines.append(f'        "chunk_id": {chunk.chunk_id},')
            lines.append(f'        "start_char": {chunk.start_char},')
            lines.append(f'        "end_char": {chunk.end_char},')
            lines.append(f'        "overlap_with_next": {chunk.overlap_with_next},')
            lines.append(f'        "estimated_tokens": {chunk.metadata.get("estimated_tokens", 0)},')
            lines.append(f'        "is_first": {chunk.metadata.get("is_first", False)},')
            lines.append(f'        "is_last": {chunk.metadata.get("is_last", False)},')
            lines.append("    },")
        lines.append("]")

        return "\n".join(lines)

    def to_markdown(self) -> str:
        """
        Generate markdown report of chunking decisions.

        Returns:
            Markdown-formatted chunking report
        """
        from datetime import datetime

        lines = [
            "# Chunking Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Total Chunks:** {self.metadata.get('total_chunks', 0)}",
            f"- **Total Tokens:** {self.metadata.get('total_tokens', 0):,}",
            f"- **Total Characters:** {self.metadata.get('total_chars', 0):,}",
            f"- **Chunk Size:** {self.metadata.get('chunk_size_tokens', 0):,} tokens",
            f"- **Overlap:** {self.metadata.get('overlap_tokens', 0):,} tokens",
            f"- **Strategy:** {self.metadata.get('strategy', 'unknown')}",
            f"- **Merge Strategy:** {self.metadata.get('merge_strategy', 'unknown')}",
            "",
        ]

        if self.chunks:
            lines.extend([
                "## Chunk Details",
                "",
                "| Chunk | Tokens | Characters | Start | End | Overlap |",
                "|-------|--------|------------|-------|-----|---------|",
            ])

            for chunk in self.chunks:
                tokens = chunk.metadata.get('estimated_tokens', 0)
                chars = chunk.metadata.get('char_count', 0)
                lines.append(
                    f"| {chunk.chunk_id} | {tokens:,} | {chars:,} | "
                    f"{chunk.start_char:,} | {chunk.end_char:,} | "
                    f"{chunk.overlap_with_next:,} |"
                )
            lines.append("")

        lines.extend([
            "## Processing Strategy",
            "",
            f"**Sequential Merge:** Chunk N+1 sees results from chunk N as context.",
            "",
            "This ensures:",
            "- Context continuity across chunks",
            "- Later chunks can reference earlier results",
            "- Dependencies are preserved",
            "",
            "## Next Steps",
            "",
            "1. Each chunk will be compiled separately",
            "2. Results merged sequentially (chunk 2 sees chunk 1 output)",
            "3. Final compilation combines all chunk results",
            "",
        ])

        return "\n".join(lines)
