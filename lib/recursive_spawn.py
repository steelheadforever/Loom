"""
Recursive Spawn Manager for Loom-RLM
Enables hierarchical task decomposition with controlled depth limits.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SpawnNode:
    """Represents a node in the spawn tree."""
    task_id: str
    parent_task_id: Optional[str]
    depth: int
    role: str
    spawned_at: str
    children: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed


class RecursiveSpawnManager:
    """
    Manages recursive subagent spawning with depth limits.

    Design decisions:
    - Max depth: 2 (configurable)
    - Auto-approval: Within depth limit (no user prompt)
    - Tree visualization: ASCII tree for logging
    - Spawn tracking: All spawns logged to spawn_tree.md
    """

    def __init__(self, max_depth: int = 2, auto_approve: bool = True):
        """
        Initialize the spawn manager.

        Args:
            max_depth: Maximum recursion depth (default: 2)
            auto_approve: Auto-approve spawns within depth limit (default: True)
        """
        self.max_depth = max_depth
        self.auto_approve = auto_approve
        self.spawn_tree: Dict[str, SpawnNode] = {}
        self.root_tasks: Set[str] = set()

    def register_root_task(self, task_id: str, role: str) -> None:
        """
        Register a root-level task (depth 0).

        Args:
            task_id: Task identifier
            role: Subagent role
        """
        if task_id not in self.spawn_tree:
            node = SpawnNode(
                task_id=task_id,
                parent_task_id=None,
                depth=0,
                role=role,
                spawned_at=datetime.now().isoformat()
            )
            self.spawn_tree[task_id] = node
            self.root_tasks.add(task_id)

    def can_spawn_child(self, parent_task_id: str) -> bool:
        """
        Check if a parent task can spawn a child.

        Args:
            parent_task_id: ID of the parent task

        Returns:
            True if spawning is allowed
        """
        if parent_task_id not in self.spawn_tree:
            # Parent doesn't exist, can't spawn
            return False

        parent_node = self.spawn_tree[parent_task_id]

        # Check depth limit
        if parent_node.depth >= self.max_depth:
            return False

        return True

    def register_spawn(
        self,
        parent_task_id: str,
        child_task_id: str,
        role: str
    ) -> bool:
        """
        Register a new spawn relationship.

        Args:
            parent_task_id: ID of the parent task
            child_task_id: ID of the child task
            role: Role of the child subagent

        Returns:
            True if spawn was registered successfully
        """
        # Validate parent exists
        if parent_task_id not in self.spawn_tree:
            return False

        # Check if spawning is allowed
        if not self.can_spawn_child(parent_task_id):
            return False

        # Get parent node
        parent_node = self.spawn_tree[parent_task_id]

        # Create child node
        child_node = SpawnNode(
            task_id=child_task_id,
            parent_task_id=parent_task_id,
            depth=parent_node.depth + 1,
            role=role,
            spawned_at=datetime.now().isoformat()
        )

        # Register child
        self.spawn_tree[child_task_id] = child_node

        # Add to parent's children
        parent_node.children.append(child_task_id)

        return True

    def update_status(self, task_id: str, status: str) -> None:
        """
        Update the status of a task.

        Args:
            task_id: Task identifier
            status: New status (pending, running, completed, failed)
        """
        if task_id in self.spawn_tree:
            self.spawn_tree[task_id].status = status

    def get_depth(self, task_id: str) -> int:
        """
        Get the depth of a task in the spawn tree.

        Args:
            task_id: Task identifier

        Returns:
            Depth (0 for root, -1 if not found)
        """
        if task_id not in self.spawn_tree:
            return -1
        return self.spawn_tree[task_id].depth

    def get_children(self, task_id: str) -> List[str]:
        """
        Get the children of a task.

        Args:
            task_id: Task identifier

        Returns:
            List of child task IDs
        """
        if task_id not in self.spawn_tree:
            return []
        return self.spawn_tree[task_id].children.copy()

    def get_spawn_path(self, task_id: str) -> List[str]:
        """
        Get the path from root to this task.

        Args:
            task_id: Task identifier

        Returns:
            List of task IDs from root to this task
        """
        if task_id not in self.spawn_tree:
            return []

        path = []
        current_id = task_id

        while current_id is not None:
            path.append(current_id)
            node = self.spawn_tree[current_id]
            current_id = node.parent_task_id

        return list(reversed(path))

    def get_spawn_tree_visualization(self) -> str:
        """
        Generate ASCII tree visualization of spawn hierarchy.

        Returns:
            ASCII art tree
        """
        lines = []

        def render_node(task_id: str, prefix: str, is_last: bool):
            node = self.spawn_tree[task_id]

            # Node line
            connector = "└── " if is_last else "├── "
            status_symbol = {
                "pending": "○",
                "running": "◐",
                "completed": "●",
                "failed": "✗"
            }.get(node.status, "?")

            lines.append(
                f"{prefix}{connector}{status_symbol} {node.role}:{node.task_id} "
                f"(depth {node.depth})"
            )

            # Children prefix
            if is_last:
                child_prefix = prefix + "    "
            else:
                child_prefix = prefix + "│   "

            # Render children
            for i, child_id in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                render_node(child_id, child_prefix, is_last_child)

        # Render all root tasks
        root_list = sorted(self.root_tasks)
        for i, root_id in enumerate(root_list):
            is_last = (i == len(root_list) - 1)
            render_node(root_id, "", is_last)

        return "\n".join(lines)

    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about the spawn tree.

        Returns:
            Dictionary with statistics
        """
        total_tasks = len(self.spawn_tree)
        depth_counts = {}
        role_counts = {}
        status_counts = {}

        for node in self.spawn_tree.values():
            # Depth distribution
            depth_counts[node.depth] = depth_counts.get(node.depth, 0) + 1

            # Role distribution
            role_counts[node.role] = role_counts.get(node.role, 0) + 1

            # Status distribution
            status_counts[node.status] = status_counts.get(node.status, 0) + 1

        # Calculate max depth reached
        max_depth_reached = max(depth_counts.keys()) if depth_counts else 0

        return {
            "total_tasks": total_tasks,
            "root_tasks": len(self.root_tasks),
            "max_depth_reached": max_depth_reached,
            "max_depth_allowed": self.max_depth,
            "depth_distribution": depth_counts,
            "role_distribution": role_counts,
            "status_distribution": status_counts,
            "auto_approve": self.auto_approve
        }

    def to_markdown(self) -> str:
        """
        Generate markdown report of spawn tree.

        Returns:
            Markdown-formatted spawn tree report
        """
        lines = [
            "# Recursive Spawn Tree",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
        ]

        # Statistics
        stats = self.get_statistics()
        lines.extend([
            "## Statistics",
            "",
            f"- **Total Tasks:** {stats['total_tasks']}",
            f"- **Root Tasks:** {stats['root_tasks']}",
            f"- **Max Depth Reached:** {stats['max_depth_reached']}",
            f"- **Max Depth Allowed:** {stats['max_depth_allowed']}",
            f"- **Auto-Approve:** {stats['auto_approve']}",
            "",
        ])

        # Status distribution
        if stats['status_distribution']:
            lines.extend([
                "## Status Distribution",
                "",
            ])
            for status, count in sorted(stats['status_distribution'].items()):
                lines.append(f"- **{status.title()}:** {count}")
            lines.append("")

        # Depth distribution
        if stats['depth_distribution']:
            lines.extend([
                "## Depth Distribution",
                "",
            ])
            for depth, count in sorted(stats['depth_distribution'].items()):
                lines.append(f"- **Depth {depth}:** {count} tasks")
            lines.append("")

        # Role distribution
        if stats['role_distribution']:
            lines.extend([
                "## Role Distribution",
                "",
            ])
            for role, count in sorted(stats['role_distribution'].items()):
                lines.append(f"- **{role}:** {count} spawns")
            lines.append("")

        # Tree visualization
        tree_viz = self.get_spawn_tree_visualization()
        if tree_viz:
            lines.extend([
                "## Spawn Tree Visualization",
                "",
                "```",
                tree_viz,
                "```",
                "",
                "**Legend:**",
                "- ○ Pending",
                "- ◐ Running",
                "- ● Completed",
                "- ✗ Failed",
                "",
            ])

        # Task details
        if self.spawn_tree:
            lines.extend([
                "## Task Details",
                "",
            ])

            for task_id in sorted(self.spawn_tree.keys()):
                node = self.spawn_tree[task_id]
                path = " → ".join(self.get_spawn_path(task_id))

                lines.extend([
                    f"### {task_id}",
                    "",
                    f"- **Role:** {node.role}",
                    f"- **Depth:** {node.depth}",
                    f"- **Status:** {node.status}",
                    f"- **Parent:** {node.parent_task_id or 'None (root)'}",
                    f"- **Children:** {len(node.children)}",
                    f"- **Spawned:** {node.spawned_at}",
                    f"- **Path:** {path}",
                    "",
                ])

        return "\n".join(lines)

    def validate_spawn_request(
        self,
        parent_task_id: str,
        child_task_id: str,
        role: str
    ) -> tuple[bool, str]:
        """
        Validate a spawn request before execution.

        Args:
            parent_task_id: ID of the parent task
            child_task_id: ID of the child task
            role: Role of the child subagent

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check parent exists
        if parent_task_id not in self.spawn_tree:
            return False, f"Parent task '{parent_task_id}' not found in spawn tree"

        # Check depth limit
        if not self.can_spawn_child(parent_task_id):
            parent_depth = self.spawn_tree[parent_task_id].depth
            return False, f"Cannot spawn at depth {parent_depth + 1} (max: {self.max_depth})"

        # Check for duplicate task ID
        if child_task_id in self.spawn_tree:
            return False, f"Task ID '{child_task_id}' already exists"

        # Check role is valid (basic check)
        valid_roles = [
            "researcher", "architect", "coder", "reviewer",
            "data_analyst", "documenter", "debugger"
        ]
        if role not in valid_roles:
            return False, f"Invalid role '{role}' (must be one of {valid_roles})"

        return True, ""
