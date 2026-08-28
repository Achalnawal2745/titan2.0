"""
core/prompt_builder.py — Dynamic System Prompt Assembler.
Ported from DeepSeek Harness (`packages/core/system-prompt`).

Assembles system prompt layers dynamically:
1. Core Identity & Rules (`core/prompt.txt`).
2. Current Clock & Session Time.
3. Active WorkPad / Plan status.
4. OS & Environment Context (Desktop, Downloads, local user path).
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class PromptBuilder:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent

    def build_system_prompt(self, workpad_context: str = "", extra_sections: Optional[List[str]] = None) -> str:
        sections: List[str] = []

        # 1. Base Core Protocol
        prompt_file = self.base_dir / "core" / "prompt.txt"
        if prompt_file.exists():
            sections.append(prompt_file.read_text(encoding="utf-8"))

        # 2. Real System Context
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")
        desktop_dir = str(Path.home() / "Desktop")
        env_section = (
            f"\n[SYSTEM ENVIRONMENT CONTEXT]\n"
            f"• Current Date/Time: {now_str}\n"
            f"• User Desktop Path: {desktop_dir}\n"
            f"• User Workspace: {str(self.base_dir)}\n"
        )
        sections.append(env_section)

        # 3. Dynamic WorkPad Context
        if workpad_context and workpad_context.strip():
            sections.append(f"\n[ACTIVE WORKPAD PLAN]\n{workpad_context.strip()}\n")

        # 4. Extra Layer Sections
        if extra_sections:
            for s in extra_sections:
                if s and s.strip():
                    sections.append(f"\n{s.strip()}\n")

        return "\n".join(sections)


prompt_builder = PromptBuilder()
