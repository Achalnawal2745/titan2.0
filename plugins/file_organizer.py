"""
plugins/file_organizer.py
-------------------------
Intelligent directory organizer and clutter cleaner for Desktop, Downloads, and custom folders.
Adapted from Awesome Claude Skills File Organizer.
"""
from __future__ import annotations

import shutil
from pathlib import Path

PLUGIN = {
    "name": "file_organizer",
    "description": (
        "Organizes messy directories (e.g. Desktop, Downloads) by automatically grouping files "
        "into categorized subfolders (Documents, Images, Archives, Code, Videos, Audio, Installers) "
        "or summarizing folder clutter without moving files. Use when user asks to organize, clean, "
        "or sort a folder."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "organize | scan | undo_info",
            },
            "target_dir": {
                "type": "STRING",
                "description": "Folder to organize: 'desktop' | 'downloads' | full path (default: 'downloads')",
            },
        },
        "required": ["action"],
    },
}

CATEGORIES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv", ".pptx", ".md", ".epub"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".cpp", ".c", ".rs", ".go"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".appx"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
    "Audio": [".mp3", ".wav", ".m4a", ".flac", ".ogg"],
}


def _resolve_dir(raw: str) -> Path:
    lower = (raw or "downloads").lower().strip()
    if lower == "desktop":
        return Path.home() / "Desktop"
    if lower == "downloads":
        return Path.home() / "Downloads"
    if lower == "documents":
        return Path.home() / "Documents"
    p = Path(raw)
    return p if p.exists() else Path.home() / "Downloads"


def run(parameters: dict, player=None, speak=None) -> str:
    action = (parameters.get("action") or "scan").lower().strip()
    target_p = _resolve_dir(parameters.get("target_dir") or "downloads")

    if not target_p.exists():
        return f"Directory not found: {target_p}"

    files = [f for f in target_p.iterdir() if f.is_file() and not f.name.startswith(".")]

    if action == "scan":
        counts = {}
        for f in files:
            ext = f.suffix.lower()
            cat = "Other"
            for c_name, exts in CATEGORIES.items():
                if ext in exts:
                    cat = c_name
                    break
            counts[cat] = counts.get(cat, 0) + 1
        summary = [f"- **{cat}**: {cnt} files" for cat, cnt in sorted(counts.items())]
        return f"📁 **Scan of {target_p.name}** ({len(files)} total files):\n" + "\n".join(summary)

    if action == "organize":
        moved_count = 0
        cat_counts = {}
        for f in files:
            ext = f.suffix.lower()
            target_cat = "Other"
            for c_name, exts in CATEGORIES.items():
                if ext in exts:
                    target_cat = c_name
                    break
            dest_dir = target_p / target_cat
            dest_dir.mkdir(exist_ok=True)
            dest_file = dest_dir / f.name
            if not dest_file.exists():
                shutil.move(str(f), str(dest_file))
                moved_count += 1
                cat_counts[target_cat] = cat_counts.get(target_cat, 0) + 1

        res = [f"- **{cat}**: {cnt} files moved" for cat, cnt in cat_counts.items()]
        return f"✨ Successfully organized {moved_count} files in `{target_p.name}`:\n" + "\n".join(res)

    return f"Unknown action: {action}. Try 'scan' or 'organize'."
