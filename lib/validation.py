"""
Validation Module for Loom-RLM
Consolidates all security validation logic from Loom + Phase 3 extensions.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Any


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class LoomRLMValidator:
    """
    Comprehensive validation for Loom-RLM security boundaries.

    Validates:
    - File paths (Loom validation)
    - Output content (Loom validation)
    - Patch actions (Loom validation)
    - Chunk metadata (Phase 2 validation)
    - Recursive spawns (Phase 3 validation)
    - Unbounded outputs (Phase 3 validation)
    """

    # Dangerous patterns to detect in output files
    DANGEROUS_PATTERNS = [
        r'\bimport\s+',
        r'\bfrom\s+\w+\s+import\b',
        r'__import__\(',
        r'\bexec\(',
        r'\beval\(',
        r'os\.system\(',
        r'subprocess\.',
        r'\bopen\(',
    ]

    # Allowed patch actions
    ALLOWED_PATCH_ACTIONS = {
        'add_context',
        'update_task',
        'add_task',
        'remove_task',
        'update_intent'
    }

    # Valid subagent roles
    VALID_ROLES = {
        'researcher',
        'architect',
        'coder',
        'reviewer',
        'data_analyst',
        'documenter',
        'debugger'
    }

    def __init__(self, working_dir: str = "."):
        """
        Initialize validator.

        Args:
            working_dir: Working directory for path validation
        """
        self.working_dir = Path(working_dir).resolve()

    # ==================== LOOM CORE VALIDATIONS ====================

    def validate_file_path(self, file_path: str, path_type: str = "state") -> Tuple[bool, str]:
        """
        Validate file path according to Loom security constraints.

        Args:
            file_path: Path to validate
            path_type: Type of path ("state", "code", "output", "compiled")

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for ".." (directory traversal)
        if ".." in file_path:
            return False, "Path contains '..' (directory traversal attack)"

        # Check for absolute system paths
        dangerous_prefixes = ['/etc', '/usr', '/var', '~/', '/System', '/Library']
        for prefix in dangerous_prefixes:
            if file_path.startswith(prefix):
                return False, f"Path targets system directory: {prefix}"

        # Check for forbidden targets
        forbidden_patterns = [
            '.claude/',
            '.github/workflows/',
            '.gitlab-ci',
            'ci/cd',
            '.env',
            'credentials'
        ]
        for pattern in forbidden_patterns:
            if pattern in file_path.lower():
                return False, f"Path contains forbidden pattern: {pattern}"

        # Type-specific validation
        if path_type == "state":
            if not file_path.startswith("loom-rlm/"):
                return False, "State files must be within loom-rlm/"

        elif path_type == "output":
            # Output files must match pattern: loom-rlm/outputs/[a-z_]+_[0-9]+.py
            pattern = r'^loom-rlm/outputs/[a-z_]+_[0-9]+\.py$'
            if not re.match(pattern, file_path):
                return False, f"Output file doesn't match required pattern: {pattern}"

        elif path_type == "compiled":
            # Compiled files must match pattern: loom-rlm/compiled_v[0-9]+.py
            pattern = r'^loom-rlm/compiled_v[0-9]+\.py$'
            if not re.match(pattern, file_path):
                return False, f"Compiled file doesn't match required pattern: {pattern}"

        elif path_type == "code":
            # Code deliverables must be within project directory
            if file_path.startswith('/') or file_path.startswith('~'):
                return False, "Code files must use relative paths within project"

        # Check for symlinks (would need actual filesystem check in real usage)
        # In practice: test -L <path> via bash

        return True, ""

    def validate_output_content(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate subagent output content for dangerous patterns.

        Args:
            content: Output file content

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                issues.append(f"Dangerous pattern found: {pattern} (matches: {len(matches)})")

        # Check content looks like structured data (has assignments), not prose
        lines = content.split('\n')
        has_assignments = False
        for line in lines:
            stripped = line.strip()
            # Skip empty lines, comments, class defs, docstrings
            if not stripped or stripped.startswith('#') or stripped.startswith('class '):
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            # Look for key = value assignments (structured data indicator)
            if re.match(r'^[a-zA-Z_]\w*\s*=\s*', stripped):
                has_assignments = True
                break
        if not has_assignments:
            issues.append("Content does not appear to be structured data (no key = value assignments found)")

        # Check for required fields (supports both `field = ...` and `"field": ...` patterns)
        required_fields = ['task_id', 'iteration', 'completed', 'results']
        for field in required_fields:
            pattern = rf'(?:^|\s){field}\s*=|"{field}"\s*:'
            if not re.search(pattern, content, re.MULTILINE):
                issues.append(f"Missing required field: {field}")

        # Check completed is boolean (accepts True/False, true/false, or colon syntax)
        completed_match = re.search(r'completed\s*[=:]\s*(\w+)', content)
        if completed_match:
            value = completed_match.group(1)
            if value not in ('True', 'False', 'true', 'false'):
                issues.append(f"'completed' must be True/False (or true/false), got: {value}")

        return len(issues) == 0, issues

    def validate_patch(self, patch: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a prompt patch.

        Args:
            patch: Patch dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check action is allowed
        action = patch.get('action')
        if action not in self.ALLOWED_PATCH_ACTIONS:
            return False, f"Invalid patch action: {action} (allowed: {self.ALLOWED_PATCH_ACTIONS})"

        # Action-specific validation
        if action == 'add_context':
            key = patch.get('key', '')
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
                return False, f"Invalid context key: {key} (must be alphanumeric/underscore)"

            value = patch.get('value')
            if isinstance(value, str):
                # Check for shell commands or URLs in value
                if any(cmd in value.lower() for cmd in ['rm -rf', 'curl', 'wget', 'sudo']):
                    return False, "Context value contains shell command"
                if value.lower().startswith(('http://', 'https://', 'ftp://')):
                    return False, "Context value contains raw URL"

        elif action == 'update_task':
            task_id = patch.get('task_id')
            if not task_id:
                return False, "update_task requires task_id"

            field = patch.get('field')
            if field not in ('description', 'requires', 'depends_on'):
                return False, f"Invalid field for update_task: {field}"

        elif action == 'add_task':
            task = patch.get('task', {})
            if not task.get('id'):
                return False, "add_task requires task with 'id'"

            outputs_to = task.get('outputs_to', '')
            is_valid, error = self.validate_file_path(outputs_to, "output")
            if not is_valid:
                return False, f"Invalid outputs_to path: {error}"

        elif action == 'remove_task':
            task_id = patch.get('task_id')
            if not task_id:
                return False, "remove_task requires task_id"

        elif action == 'update_intent':
            # Intent updates are sensitive - orchestrator must review
            new_intent = patch.get('new_intent', {})
            if not isinstance(new_intent, dict):
                return False, "new_intent must be a dictionary"

        return True, ""

    # ==================== PHASE 2 VALIDATIONS ====================

    def validate_chunk_metadata(self, metadata_file: str) -> Tuple[bool, str]:
        """
        Validate chunk metadata file.

        Args:
            metadata_file: Path to chunks_metadata.py

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check path
        if not metadata_file.startswith("loom-rlm/"):
            return False, "Chunk metadata must be in loom-rlm/"

        if not metadata_file.endswith("chunks_metadata.py"):
            return False, "Chunk metadata must be named chunks_metadata.py"

        return True, ""

    # ==================== PHASE 3 VALIDATIONS ====================

    def validate_recursive_spawn(
        self,
        parent_task_id: str,
        child_task_id: str,
        current_depth: int,
        max_depth: int = 2
    ) -> Tuple[bool, str]:
        """
        Validate recursive spawn request.

        Args:
            parent_task_id: Parent task ID
            child_task_id: Child task ID
            current_depth: Current depth in spawn tree
            max_depth: Maximum allowed depth

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check depth limit
        if current_depth >= max_depth:
            return False, f"Spawn depth limit reached (max: {max_depth}, current: {current_depth})"

        # Check task IDs are valid
        if not parent_task_id or not child_task_id:
            return False, "Parent and child task IDs are required"

        # Check for self-reference
        if parent_task_id == child_task_id:
            return False, "Task cannot spawn itself"

        # Check task ID format (should be safe identifiers)
        for task_id in [parent_task_id, child_task_id]:
            if not re.match(r'^[a-z0-9_]+$', task_id):
                return False, f"Invalid task ID format: {task_id}"

        return True, ""

    def validate_unbounded_output_path(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate unbounded output file path.

        Args:
            file_path: Path to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Must be in unbounded_outputs directory
        if not file_path.startswith("loom-rlm/unbounded_outputs/"):
            return False, "Unbounded outputs must be in loom-rlm/unbounded_outputs/"

        # Check for path traversal
        if ".." in file_path:
            return False, "Path contains '..'"

        # Must be .py file
        if not file_path.endswith(".py"):
            return False, "Unbounded output files must be .py"

        # Check filename pattern (should be task_id_part_N.py or task_id_index.py)
        filename = Path(file_path).name
        if not (re.match(r'^[a-z0-9_]+_part_\d+\.py$', filename) or
                re.match(r'^[a-z0-9_]+_index\.py$', filename)):
            return False, f"Invalid unbounded output filename: {filename}"

        return True, ""

    def validate_spawn_role(self, role: str) -> Tuple[bool, str]:
        """
        Validate subagent role.

        Args:
            role: Role name

        Returns:
            Tuple of (is_valid, error_message)
        """
        if role not in self.VALID_ROLES:
            return False, f"Invalid role: {role} (allowed: {self.VALID_ROLES})"

        return True, ""

    # ==================== BATCH VALIDATIONS ====================

    def validate_all_patches(self, patches: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate a list of patches.

        Args:
            patches: List of patch dictionaries

        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []

        for i, patch in enumerate(patches):
            is_valid, error = self.validate_patch(patch)
            if not is_valid:
                errors.append(f"Patch {i}: {error}")

        return len(errors) == 0, errors

    def validate_files_changed(self, files: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate list of changed files.

        Args:
            files: List of file paths

        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []

        for file_path in files:
            # Determine path type
            if file_path.startswith("loom-rlm/"):
                path_type = "state"
            else:
                path_type = "code"

            is_valid, error = self.validate_file_path(file_path, path_type)
            if not is_valid:
                errors.append(f"{file_path}: {error}")

        return len(errors) == 0, errors

    # ==================== HELPER METHODS ====================

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all validation rules.

        Returns:
            Dictionary with validation rules summary
        """
        return {
            "path_validation": {
                "no_directory_traversal": "'..' not allowed",
                "no_system_paths": "No /etc, /usr, /var, ~/, etc.",
                "no_forbidden_targets": "No .claude/, .github/workflows/, etc.",
                "state_files": "Must be in loom-rlm/",
                "output_pattern": "loom-rlm/outputs/[role]_[n].py",
                "compiled_pattern": "loom-rlm/compiled_v[n].py"
            },
            "output_validation": {
                "no_imports": "No import statements",
                "no_exec_eval": "No exec() or eval()",
                "no_os_system": "No os.system() or subprocess",
                "no_file_handles": "No open()",
                "structured_data": "Must be structured data with key-value assignments",
                "required_fields": ["task_id", "iteration", "completed", "results"]
            },
            "patch_validation": {
                "allowed_actions": list(self.ALLOWED_PATCH_ACTIONS),
                "key_format": "Alphanumeric/underscore only",
                "no_shell_commands": "Values must not contain shell commands",
                "no_raw_urls": "Values must not contain raw URLs"
            },
            "phase_3_validation": {
                "recursive_spawn": {
                    "max_depth": 2,
                    "no_self_reference": "Task cannot spawn itself",
                    "task_id_format": "lowercase alphanumeric + underscore"
                },
                "unbounded_output": {
                    "directory": "loom-rlm/unbounded_outputs/",
                    "filename_pattern": "[task]_part_[n].py or [task]_index.py",
                    "extension": ".py only"
                }
            }
        }
