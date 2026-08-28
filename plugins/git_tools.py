"""
plugins/git_tools.py
--------------------
Git intelligence tools: analyze diffs, generate changelogs, inspect repo health.
Adapted from Claude Skills Engineering workflows.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

PLUGIN = {
    "name": "git_tools",
    "description": (
        "Inspects git repositories, analyzes working tree diffs, generates Markdown changelogs "
        "from recent commits, and reports branch health. Use when asked about git commits, diffs, "
        "or repo status."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "diff_summary | changelog | branch_status | log",
            },
            "repo_path": {
                "type": "STRING",
                "description": "Path to the repository folder (defaults to current project).",
            },
            "max_commits": {
                "type": "INTEGER",
                "description": "Number of recent commits to include in changelog/log (default: 10).",
            },
        },
        "required": ["action"],
    },
}


def _run_git(cmd: list[str], cwd: Path) -> str:
    try:
        res = subprocess.run(
            ["git"] + cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return res.stdout.strip() if res.returncode == 0 else res.stderr.strip()
    except Exception as e:
        return f"Git error: {e}"


def run(parameters: dict, player=None, speak=None) -> str:
    action = (parameters.get("action") or "branch_status").lower().strip()
    repo_raw = parameters.get("repo_path") or "."
    repo_dir = Path(repo_raw).resolve()
    if not (repo_dir / ".git").exists():
        # Fallback to current project root
        repo_dir = Path(__file__).resolve().parent.parent

    max_c = int(parameters.get("max_commits") or 10)

    if action == "branch_status":
        branch = _run_git(["branch", "--show-current"], repo_dir)
        status = _run_git(["status", "--short"], repo_dir)
        last_commit = _run_git(["log", "-1", "--oneline"], repo_dir)
        return (
            f"🌿 **Repository**: `{repo_dir.name}`\n"
            f"- **Active Branch**: `{branch or 'HEAD'}`\n"
            f"- **Latest Commit**: `{last_commit}`\n"
            f"- **Working Directory**:\n```\n{status or 'Clean working tree'}\n```"
        )

    if action == "diff_summary":
        stat = _run_git(["diff", "--stat"], repo_dir)
        unstaged = _run_git(["diff"], repo_dir)
        if not stat and not unstaged:
            return "No uncommitted changes in the repository."
        preview = unstaged[:2500] if len(unstaged) > 2500 else unstaged
        return f"📊 **Git Diff Summary**:\n```\n{stat}\n```\n**Preview**:\n```diff\n{preview}\n```"

    if action in ("changelog", "log"):
        raw_log = _run_git(["log", f"-n{max_c}", "--pretty=format:%h - %s (%cr) <%an>"], repo_dir)
        if not raw_log:
            return "No commit history found."
        lines = [f"- {ln}" for ln in raw_log.splitlines() if ln.strip()]
        return f"📝 **Recent Changelog ({repo_dir.name})**:\n" + "\n".join(lines)

    return f"Unknown git action: {action}. Try: branch_status, diff_summary, changelog"
