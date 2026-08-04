#!/usr/bin/env python3
"""OPTIONAL PreToolUse hook that enforces Contributor Scout's discovery-only rule.

This hook is NOT installed automatically. Nothing in this project registers it.
To use it, follow hooks/README.md and add it to your own settings file
deliberately.

What it does
------------
Reads a Claude Code PreToolUse hook payload on stdin and denies:

  * Write / Edit / NotebookEdit to any path outside `contribution-discovery/`
  * Bash commands that mutate Git state (commit, push, reset --hard, clean -fd,
    checkout, branch creation, tag creation, rebase, merge, stash)
  * Bash commands that write to GitHub (`gh issue create`, `gh pr create`,
    `gh * comment`, `gh api` with a mutating method, `gh release create`, ...)
  * Obviously destructive shell commands (`rm -rf`, `mkfs`, `dd of=`, ...)

Everything else is allowed to fall through to normal permission handling.

Exit behaviour
--------------
Emits the JSON `permissionDecision` form on stdout and exits 0. A malformed
payload is allowed through (exit 0, no decision) rather than blocking the
session - this hook is a safety net, not the only control.

Limitations
-----------
This is a defence-in-depth measure using textual command inspection. A
sufficiently creative command string can evade it. It complements the skill's
instructions and Claude Code's permission rules; it does not replace them.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Directory writes are confined to this, relative to the project directory.
ALLOWED_WRITE_ROOT = "contribution-discovery"

# (regex, reason) - matched case-insensitively against the Bash command string.
DENIED_COMMANDS: List[Tuple[str, str]] = [
    # Git state mutation
    (r"\bgit\s+(-[^\s]+\s+)*commit\b", "git commit is not permitted during discovery"),
    (r"\bgit\s+(-[^\s]+\s+)*push\b", "git push is not permitted during discovery"),
    (r"\bgit\s+(-[^\s]+\s+)*reset\s+--hard\b", "git reset --hard is destructive"),
    (r"\bgit\s+(-[^\s]+\s+)*clean\s+-[a-z]*[fd]", "git clean is destructive"),
    (r"\bgit\s+(-[^\s]+\s+)*checkout\b", "git checkout can discard working-tree changes"),
    (r"\bgit\s+(-[^\s]+\s+)*switch\b", "git switch changes the working tree"),
    (r"\bgit\s+(-[^\s]+\s+)*(rebase|merge|cherry-pick|revert)\b",
     "history-rewriting and merge commands are not permitted during discovery"),
    (r"\bgit\s+(-[^\s]+\s+)*stash\b", "git stash mutates the working tree"),
    (r"\bgit\s+(-[^\s]+\s+)*branch\s+(?!(-a|-r|-v|--list|--contains|--show-current))",
     "branch creation is not permitted during discovery"),
    (r"\bgit\s+(-[^\s]+\s+)*tag\s+(?!(-l|--list|--contains))",
     "tag creation is not permitted during discovery"),
    (r"\bgit\s+(-[^\s]+\s+)*(add|rm|mv)\b", "staging or moving files is not permitted"),
    (r"\bgit\s+(-[^\s]+\s+)*apply\b", "applying patches modifies source"),
    (r"\bgit\s+(-[^\s]+\s+)*(remote\s+(add|remove|set-url))\b",
     "remote configuration changes are not permitted"),
    # GitHub write operations
    (r"\bgh\s+issue\s+(create|comment|close|reopen|edit|delete|pin|lock|transfer)\b",
     "creating or modifying issues is not permitted during discovery"),
    (r"\bgh\s+pr\s+(create|comment|close|reopen|edit|merge|review|ready|"
     r"checkout|revert|lock)\b",
     "creating or modifying pull requests is not permitted during discovery"),
    (r"\bgh\s+release\s+(create|edit|delete|upload)\b", "release commands are denied"),
    (r"\bgh\s+repo\s+(create|delete|fork|edit|rename|archive)\b",
     "repository mutation is denied"),
    (r"\bgh\s+(gist|secret|variable|ssh-key|gpg-key)\s+", "credential and gist commands are denied"),
    (r"\bgh\s+workflow\s+(run|enable|disable)\b", "triggering workflows is denied"),
    (r"\bgh\s+api\b[^|;&]*(-X|--method)\s*(POST|PUT|PATCH|DELETE)",
     "only read-only (GET) gh api requests are permitted"),
    (r"\bgh\s+api\b[^|;&]*(-f|--field|--input)\s",
     "gh api with a request body implies a write - use GET only"),
    # Destructive shell
    (r"\brm\s+(-[a-z]*[rf][a-z]*\s+)+", "recursive or forced deletion is denied"),
    (r"\bmkfs(\.|\s)", "filesystem creation is denied"),
    (r"\bdd\s+[^|;&]*\bof=", "dd with an output file is denied"),
    (r">\s*/dev/(sd|nvme|disk)", "writing to a block device is denied"),
    (r"\bchmod\s+(-R\s+)?777\b", "world-writable permissions are denied"),
    (r"\b(shutdown|reboot|halt)\b", "system control commands are denied"),
    # Download-and-execute
    (r"\bcurl\b[^|;&]*\|\s*(ba)?sh", "download-and-execute is denied"),
    (r"\bwget\b[^|;&]*\|\s*(ba)?sh", "download-and-execute is denied"),
]

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# Bash redirections that write to a file, e.g. `foo > bar` or `foo >> bar`.
REDIRECT_RE = re.compile(r"(?<![0-9<>])>>?\s*([^\s;|&]+)")


def decision(action: str, reason: str) -> Dict[str, Any]:
    """Build a PreToolUse hook response."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": action,
            "permissionDecisionReason": reason,
        }
    }


def project_dir(payload: Dict[str, Any]) -> Path:
    raw = (payload.get("cwd")
           or os.environ.get("CLAUDE_PROJECT_DIR")
           or os.getcwd())
    return Path(raw).resolve()


def is_inside_allowed_root(target: str, root: Path) -> bool:
    """True when `target` resolves inside <root>/contribution-discovery/."""
    try:
        resolved = Path(target).expanduser()
        if not resolved.is_absolute():
            resolved = root / resolved
        resolved = resolved.resolve()
        relative = resolved.relative_to(root)
    except (ValueError, OSError):
        return False
    return bool(relative.parts) and relative.parts[0] == ALLOWED_WRITE_ROOT


def check_write(payload: Dict[str, Any], root: Path) -> Optional[Dict[str, Any]]:
    target = (payload.get("tool_input") or {}).get("file_path")
    if not target:
        return None
    if is_inside_allowed_root(target, root):
        return None
    return decision(
        "deny",
        "Contributor Scout is discovery-only: writes are confined to "
        "{0}/. Refused write to '{1}'. If this is intentional non-discovery "
        "work, disable the discovery-guard hook first.".format(ALLOWED_WRITE_ROOT, target),
    )


def check_bash(payload: Dict[str, Any], root: Path) -> Optional[Dict[str, Any]]:
    command = (payload.get("tool_input") or {}).get("command") or ""
    if not command:
        return None

    for pattern, reason in DENIED_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return decision(
                "deny",
                "Contributor Scout is discovery-only: {0}. Blocked command: "
                "{1}".format(reason, command.strip()[:200]),
            )

    for match in REDIRECT_RE.finditer(command):
        target = match.group(1).strip("'\"")
        if target.startswith("/dev/"):
            continue
        if not is_inside_allowed_root(target, root):
            return decision(
                "deny",
                "Contributor Scout is discovery-only: shell redirection would "
                "write to '{0}', outside {1}/.".format(target, ALLOWED_WRITE_ROOT),
            )
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        # Fail open: a malformed payload must not wedge the session.
        return 0

    if not isinstance(payload, dict):
        return 0

    tool = payload.get("tool_name")
    root = project_dir(payload)

    result: Optional[Dict[str, Any]] = None
    if tool in WRITE_TOOLS:
        result = check_write(payload, root)
    elif tool == "Bash":
        result = check_bash(payload, root)

    if result is not None:
        json.dump(result, sys.stdout)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
