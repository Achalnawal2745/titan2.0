"""
core/skill_registry.py — Discovery + progressive-disclosure loading for
SKILL.md knowledge packages (Mark-L/skills/, bro/*/skills/, bro/*-skills/).

This is DIFFERENT from plugin_loader.py's PluginRegistry:
  - PluginRegistry:  plugins/*.py, each with a fixed run(parameters) function,
                     hardcoded Python logic, one Gemini tool per plugin.
  - SkillRegistry:   SKILL.md folders, mostly markdown instructions + optional
                     scripts/*.py helpers, ONE Gemini tool total (load_skill)
                     that returns full instructions on demand.

Cost model: at startup we only read the YAML frontmatter of every SKILL.md
(name + description, ~50-150 tokens each) into a permanent index. The full
SKILL.md body (which can be thousands of tokens with examples) is only
pulled into context when the model actually calls load_skill(name).

Never raises during discovery — a malformed SKILL.md is skipped and logged,
same contract as plugin_loader.discover_plugins().
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_NAME_RE = re.compile(r'^name:\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)
_DESC_RE = re.compile(r'^description:\s*"(.+?)"\s*$', re.MULTILINE | re.DOTALL)


@dataclass
class SkillRecord:
    name: str
    description: str
    folder: Path
    skill_md: Path


class SkillRegistry:
    def __init__(
        self,
        skills: dict[str, SkillRecord],
        logger: Callable[[str], None] = print,
        collisions: dict[str, list[Path]] | None = None,
    ):
        self._skills = skills
        self._logger = logger
        # name -> list of folders that were SHADOWED (lost the name collision).
        # Populated by discover_skills(); empty for registries built by hand.
        self._collisions = collisions or {}

    def collisions_report(self) -> str:
        """Human-readable list of duplicate skill names and which folder
        won vs which ones got silently shadowed before this fix. Print this
        at startup / put a button for it in the UI — these are bugs waiting
        to bite (wrong skill loads for a name you thought was unique)."""
        if not self._collisions:
            return "No duplicate skill names found."
        lines = [f"{len(self._collisions)} duplicate skill name(s) found:"]
        for name, shadowed in sorted(self._collisions.items()):
            winner = self._skills[name].folder if name in self._skills else "?"
            lines.append(f"- '{name}': using {winner}")
            for p in shadowed:
                lines.append(f"    (shadowed, NOT loadable: {p})")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self._skills)

    def names(self) -> list[str]:
        return sorted(self._skills.keys())

    def index_for_prompt(self) -> str:
        """Lightweight, always-in-context skills guide formatted as canonical DeepSeek Harness XML."""
        if not self._skills:
            return ""

        primary_skills = [
            "pptx", "docx", "xlsx", "pdf", "canvas-design", "theme-factory",
            "tailored-resume-generator", "artifacts-builder", "mcp-builder",
            "webapp-testing", "changelog-generator", "meeting-insights-analyzer",
            "content-research-writer", "deep-research", "algorithmic-art",
            "playwright-pro", "brand-guidelines", "code-tour", "git-worktree-manager"
        ]

        lines = [
            "<system-reminder>",
            "A skill is a reusable set of task-specific instructions. The following skills are available in this session:",
            "",
            "<available_skills>",
        ]
        for name in primary_skills:
            if name in self._skills:
                rec = self._skills[name]
                desc = rec.description.replace("\n", " ").strip()
                lines.append(f"- `{rec.name}`: {desc}")
        lines.extend([
            "</available_skills>",
            "",
            f"There are {len(self._skills)} total skills available. For other tasks, call search_skills(query) first.",
            "If the task clearly matches a skill, call the `load_skill` tool with the exact skill name before taking task actions. Follow the loaded <skill_instructions>.",
            "</system-reminder>",
        ])
        return "\n".join(lines)

    def search(self, query: str, top_k: int = 5) -> list[SkillRecord]:
        """Simple keyword scorer over name + description across ALL skills."""
        if not query or not query.strip():
            return []
        q_tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
        if not q_tokens:
            return []

        scored: list[tuple[float, SkillRecord]] = []
        for rec in self._skills.values():
            name_tokens = set(re.findall(r"[a-z0-9]+", rec.name.lower()))
            desc_tokens = set(re.findall(r"[a-z0-9]+", rec.description.lower()))
            # name matches weighted higher than description matches
            score = 3.0 * len(q_tokens & name_tokens) + 1.0 * len(q_tokens & desc_tokens)
            # substring bonus catches e.g. query "zoho" matching "zoho_books-automation"
            if any(qt in rec.name.lower() for qt in q_tokens):
                score += 1.5
            if score > 0:
                scored.append((score, rec))

        scored.sort(key=lambda t: (-t[0], t[1].name))
        return [rec for _, rec in scored[:top_k]]

    def get_tool_declaration(self) -> dict:
        return {
            "name": "load_skill",
            "description": (
                "Load the full instructions for an available skill. Call this with the exact skill name from the available skills list before acting on a task that matches that skill."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "skill_name": {
                        "type": "STRING",
                        "description": "The exact skill name from the available skills list (e.g. 'pptx', 'docx', 'xlsx', 'pdf').",
                    },
                },
                "required": ["skill_name"],
            },
        }

    def get_search_tool_declaration(self) -> dict:
        return {
            "name": "search_skills",
            "description": (
                "Search ALL available skills by keyword and get back the closest-matching skill names."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "Task description or keywords to search for.",
                    },
                },
                "required": ["query"],
            },
        }

    def search_for_tool(self, query: str) -> str:
        matches = self.search(query, top_k=5)
        if not matches:
            return f"No skills matched query '{query}'."
        lines = [f"Found {len(matches)} matching skill(s):"]
        for rec in matches:
            desc = rec.description.replace("\n", " ").strip()
            lines.append(f"- `{rec.name}`: {desc}")
        lines.append("Call load_skill(skill_name) with the exact name above.")
        return "\n".join(lines)

    def load(self, skill_name: str) -> str:
        rec = self._skills.get(skill_name)
        if rec is None:
            available = ", ".join(self.names()) or "(none indexed)"
            return f"No skill named '{skill_name}'. Available: {available}"
        try:
            body = rec.skill_md.read_text(encoding="utf-8")
        except Exception as e:
            return f"Failed to read {rec.skill_md}: {e}"

        scripts_dir = rec.folder / "scripts"
        script_lines = []
        if scripts_dir.exists():
            runnable_exts = ("*.py", "*.js", "*.sh", "*.ts")
            found = []
            for pattern in runnable_exts:
                found.extend(scripts_dir.rglob(pattern))
            if found:
                for p in sorted(found):
                    runner = "python" if p.suffix == ".py" else \
                             "node" if p.suffix in (".js", ".ts") else "bash"
                    script_lines.append(f'  {runner} "{p.resolve()}"')

        resource_hint = [
            f"Base folder: {rec.folder.resolve()}",
        ]
        if script_lines:
            resource_hint.append("Available helper scripts (run via run_command):")
            resource_hint.extend(script_lines)
        else:
            resource_hint.append("No pre-packaged scripts. Write generator code via write_file / code_helper.")

        return "\n".join([
            f'<skill_content name="{skill_name}">',
            '<skill_resources>',
            "\n".join(resource_hint),
            '</skill_resources>',
            '',
            '<skill_instructions>',
            body,
            '</skill_instructions>',
            '</skill_content>',
        ])

    def list_for_ui(self) -> list[dict]:
        return [
            {"name": r.name, "description": r.description, "folder": str(r.folder)}
            for r in sorted(self._skills.values(), key=lambda r: r.name)
        ]


def discover_skills(skill_dirs: list[Path | str], logger: Callable[[str], None] = print) -> SkillRegistry:
    found: dict[str, SkillRecord] = {}
    collisions: dict[str, list[Path]] = {}  # name -> shadowed folders (lost the collision)

    for base in skill_dirs:
        base = Path(base)
        if not base.exists():
            logger(f"Skill dir not found, skipping: {base}")
            continue
        all_skills = list(base.rglob("SKILL.md"))
        # Prioritize top-level core skills over deep _playbooks / _sandbox copies
        all_skills.sort(key=lambda p: (
            1 if any(part.startswith("_") for part in p.parts) else 0,
            len(p.parts),
            str(p)
        ))
        for skill_md in all_skills:
            try:
                text = skill_md.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            fm_match = _FRONTMATTER_RE.match(text)
            if not fm_match:
                continue

            fm = fm_match.group(1)
            name_match = _NAME_RE.search(fm)
            desc_match = _DESC_RE.search(fm)
            if not name_match or not desc_match:
                continue

            name = name_match.group(1).strip()
            if not name:
                continue
            if name in found:
                # Same name, different folder -> this one gets shadowed.
                # Previously this was silent; now we record it so it's
                # visible via registry.collisions_report() at startup.
                collisions.setdefault(name, []).append(skill_md.parent)
                continue

            found[name] = SkillRecord(
                name=name,
                description=desc_match.group(1).strip(),
                folder=skill_md.parent,
                skill_md=skill_md,
            )

    try:
        logger(f"[Skills] {len(found)} Production Skills Indexed & Ready (load_skill)")
        if collisions:
            logger(
                f"[Skills] WARNING: {len(collisions)} duplicate skill name(s) — "
                f"{sum(len(v) for v in collisions.values())} folder(s) shadowed and NOT loadable. "
                "Call registry.collisions_report() for the full list."
            )
    except Exception:
        pass
    return SkillRegistry(found, logger=logger, collisions=collisions)