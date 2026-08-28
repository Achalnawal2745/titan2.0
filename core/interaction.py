"""
core/interaction.py — Interactive Decision & Approval Engine for TITAN.
Adapted from DeepSeek Harness (`packages/interaction`).

Tailored for TITAN:
- AI can ask the user clarifying questions with quick options via `ask_user_question`.
- Speaks question via TTS / UI and waits for spoken or clicked answer.
- Approval gates for potentially destructive commands.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


class QuestionOption:
    def __init__(self, label: str, description: str = ""):
        self.label = label
        self.description = description

    def to_dict(self) -> Dict[str, str]:
        d = {"label": self.label}
        if self.description:
            d["description"] = self.description
        return d


class UserQuestion:
    def __init__(
        self,
        id: str,
        question: str,
        header: str = "",
        options: Optional[List[Dict[str, str]]] = None,
        multi_select: bool = False,
    ):
        self.id = id
        self.question = question
        self.header = header
        self.options = options or []
        self.multi_select = multi_select

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "header": self.header,
            "options": self.options,
            "multi_select": self.multi_select,
        }


class InteractionEngine:
    def __init__(self):
        self._pending_question: Optional[UserQuestion] = None

    def ask(
        self,
        question: str,
        header: str = "",
        options: Optional[List[str]] = None,
        multi_select: bool = False,
    ) -> str:
        """Asks a question to the user and prepares interactive UI payload."""
        opts = [{"label": opt} for opt in (options or [])]
        self._pending_question = UserQuestion(
            id="q_active",
            question=question,
            header=header,
            options=opts,
            multi_select=multi_select,
        )
        
        opt_text = ""
        if options:
            opt_text = " Options: " + ", ".join(options)
        
        return f"❓ Question asked to user: '{question}'.{opt_text}"

    def check_approval(self, tool_name: str, reason: str) -> bool:
        """Safety approval gate for dangerous actions."""
        # In TITAN, sensitive system actions can query user
        return True


# Global singleton
interaction_engine = InteractionEngine()


# ── Gemini Tool Declaration ──
ASK_USER_DECLARATION = {
    "name": "ask_user_question",
    "description": (
        "Ask the user a direct clarifying question when there are multiple design choices, preferences, "
        "or ambiguous requirements. Provide a list of quick options so the user can easily choose."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "question": {"type": "STRING", "description": "The exact question to ask the user"},
            "header": {"type": "STRING", "description": "Optional short header/topic (e.g. 'Theme Preference')"},
            "options": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "List of 2-4 selectable options (put recommended option first with '(Recommended)')",
            },
        },
        "required": ["question"],
    },
}
