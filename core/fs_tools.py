"""
core/fs_tools.py — File Operations, Precision Code Editor & Workspace Search for TITAN.
Ported and adapted from DeepSeek Harness (`packages/fs`, `packages/fs/tool-fs-search`, `packages/fs/tool-str-replace-editor`).

Provides:
- read_file, write_file
- str_replace_editor (Surgical replacement of unique substrings without file corruption)
- grep_search (Fast content pattern search)
- glob_search (Fast file pattern matching)
"""
from __future__ import annotations

import fnmatch
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from core.spill import maybe_spill_output


def _resolve_user_path(path: str) -> Path:
    """Expands desktop/..., downloads/..., documents/... to the user's real home folder."""
    p_str = path.strip()
    home = Path.home()
    for folder in ("Desktop", "Downloads", "Documents", "Pictures", "Music", "Videos"):
        if p_str.lower().startswith(f"{folder.lower()}/") or p_str.lower().startswith(f"{folder.lower()}\\"):
            remainder = p_str[len(folder) + 1:]
            return (home / folder / remainder).resolve()
    return Path(path).resolve()


def read_file(path: str, offset_lines: int = 1, max_lines: int = 250) -> str:
    """Reads a file with line numbering and optional windowing."""
    p = _resolve_user_path(path)
    if not p.exists():
        return f"Error: File '{path}' does not exist."
    if p.is_dir():
        return f"Error: '{path}' is a directory, not a file."
    
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        total_lines = len(lines)
        
        start_idx = max(0, offset_lines - 1)
        end_idx = min(total_lines, start_idx + max_lines)
        
        numbered_lines = []
        for i in range(start_idx, end_idx):
            numbered_lines.append(f"{i + 1:4d} | {lines[i]}")
            
        header = f"[{p.name} — Lines {start_idx + 1} to {end_idx} of {total_lines}]\n"
        out_text = header + "\n".join(numbered_lines)
        clean_text, _, _ = maybe_spill_output("read_file", out_text)
        return clean_text
    except Exception as e:
        return f"Error reading file '{path}': {e}"


def write_file(path: str, content: str, overwrite: bool = True) -> str:
    """Writes content to a file, creating parent directories if needed."""
    p = _resolve_user_path(path)
    if p.exists() and not overwrite:
        return f"Error: File '{path}' already exists and overwrite is False."
    
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content.encode('utf-8'))} bytes to '{p}'."
    except Exception as e:
        return f"Error writing to file '{path}': {e}"


def str_replace_editor(path: str, old_str: str, new_str: str) -> str:
    """
    Surgically replaces exactly ONE unique occurrence of old_str with new_str.
    Guarantees zero unintended side effects and prevents rewriting entire files.
    """
    p = _resolve_user_path(path)
    if not p.exists():
        return f"Error: File '{path}' does not exist."
    
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
        count = content.count(old_str)
        if count == 0:
            return f"Error: target string not found in '{p.name}'. Please check the exact whitespace/lines."
        if count > 1:
            return f"Error: target string matched {count} times in '{p.name}'. Must be completely unique. Include more surrounding lines."
        
        new_content = content.replace(old_str, new_str, 1)
        p.write_text(new_content, encoding="utf-8")
        return f"Successfully replaced block in '{p.name}'."
    except Exception as e:
        return f"Error editing '{path}': {e}"


def grep_search(query: str, search_path: str = ".", is_regex: bool = False, max_results: int = 50) -> str:
    """Fast regex or literal content search across a directory."""
    root = Path(search_path).resolve()
    if not root.exists():
        return f"Error: Path '{search_path}' does not exist."
    
    results: List[str] = []
    pattern = None
    if is_regex:
        try:
            pattern = re.compile(query)
        except re.error as e:
            return f"Invalid regex pattern: {e}"
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden and noisy directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__", "build", "dist")]
        for f in filenames:
            if f.startswith("."):
                continue
            fpath = Path(dirpath) / f
            try:
                text = fpath.read_text(encoding="utf-8", errors="ignore")
                for line_no, line in enumerate(text.splitlines(), start=1):
                    match = pattern.search(line) if is_regex and pattern else (query.lower() in line.lower())
                    if match:
                        rel = os.path.relpath(fpath, root)
                        results.append(f"{rel}:{line_no}: {line.strip()}")
                        if len(results) >= max_results:
                            break
            except Exception:
                continue
            if len(results) >= max_results:
                break
        if len(results) >= max_results:
            break
            
    if not results:
        return f"No matches found for '{query}' under '{root}'."
    
    out = f"Matches ({len(results)}):\n" + "\n".join(results)
    clean_out, _, _ = maybe_spill_output("grep_search", out)
    return clean_out


def glob_search(pattern: str, search_path: str = ".", max_results: int = 50) -> str:
    """Fast filename pattern matching across directory tree."""
    root = Path(search_path).resolve()
    if not root.exists():
        return f"Error: Path '{search_path}' does not exist."
    
    matches: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__")]
        for f in filenames:
            if fnmatch.fnmatch(f, pattern):
                rel = os.path.relpath(Path(dirpath) / f, root)
                matches.append(rel)
                if len(matches) >= max_results:
                    break
        if len(matches) >= max_results:
            break
            
    if not matches:
        return f"No files matched pattern '{pattern}' under '{root}'."
    return f"Files found ({len(matches)}):\n" + "\n".join(matches)


# ── Gemini Tool Declarations ──
FS_TOOLS_DECLARATIONS = [
    {
        "name": "read_file",
        "description": "Read contents of a file with line numbers and optional line windowing.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Absolute or relative file path to read"},
                "offset_lines": {"type": "INTEGER", "description": "1-indexed starting line number (default 1)"},
                "max_lines": {"type": "INTEGER", "description": "Maximum number of lines to return (default 250)"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write or create a complete file on disk.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "File path to write to"},
                "content": {"type": "STRING", "description": "Full text content of the file"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "str_replace_editor",
        "description": "Surgically edit a file by replacing a unique occurrence of old_str with new_str without rewriting the entire file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "File path to edit"},
                "old_str": {"type": "STRING", "description": "Exact text to replace (must be unique in the file)"},
                "new_str": {"type": "STRING", "description": "New replacement text"},
            },
            "required": ["path", "old_str", "new_str"],
        },
    },
    {
        "name": "grep_search",
        "description": "Fast content search across files in the workspace using regex or literal text.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search query or regex pattern"},
                "search_path": {"type": "STRING", "description": "Directory to search (default '.')"},
                "is_regex": {"type": "BOOLEAN", "description": "Whether query is a regex pattern (default false)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "glob_search",
        "description": "Find files matching a glob pattern (e.g. '*.py', '*test*.js') in the workspace.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "pattern": {"type": "STRING", "description": "Glob pattern to find (e.g. '*.py')"},
                "search_path": {"type": "STRING", "description": "Directory root to search (default '.')"},
            },
            "required": ["pattern"],
        },
    },
]
