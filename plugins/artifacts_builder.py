"""
plugins/artifacts_builder.py
----------------------------
Builds interactive web artifacts, single-page tools, calculators, dashboards, and UI prototypes.
Adapted from Anthropic Web Artifacts Builder Skill.
"""
from __future__ import annotations

import json
from pathlib import Path

PLUGIN = {
    "name": "artifacts_builder",
    "description": (
        "Builds interactive single-page web applications, dashboards, calculators, tools, "
        "and UI widgets in self-contained HTML/CSS/JavaScript with modern glassmorphism design. "
        "Use when user wants an interactive tool, dashboard, game, or web prototype."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "title": {
                "type": "STRING",
                "description": "Name or title of the interactive artifact/app.",
            },
            "description": {
                "type": "STRING",
                "description": "What the interactive app should do, its features, and user controls.",
            },
            "output_path": {
                "type": "STRING",
                "description": "Optional file path to save the HTML app e.g. Desktop/budget_calc.html",
            },
            "auto_open": {
                "type": "BOOLEAN",
                "description": "Whether to launch the created app in Chrome/browser immediately (default: true)",
            },
        },
        "required": ["title", "description"],
    },
}


def run(parameters: dict, player=None, speak=None) -> str:
    title = parameters.get("title", "Interactive Artifact").strip()
    desc = parameters.get("description", "").strip()
    out_path = parameters.get("output_path") or ""
    auto_open = parameters.get("auto_open", True)

    if speak:
        speak(f"Building interactive artifact for {title}, sir.")

    try:
        from google import genai
        key_path = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
        api_key = ""
        if key_path.exists():
            api_key = json.loads(key_path.read_text(encoding="utf-8")).get("gemini_api_key", "")

        client = genai.Client(api_key=api_key)
        prompt = f"""You are an elite Frontend Architect.
Build an exceptional, self-contained single-page web application on: '{title}'
Features & User Requirements:
{desc}

Rules:
1. Return ONLY the complete, single-file HTML code (`<!DOCTYPE html><html>...</html>`). No markdown fences, no conversational filler.
2. Embed all CSS in `<style>` (dark mode, glassmorphism, responsive grid, smooth animations, Lucide/FontAwesome SVG icons, vibrant accents).
3. Embed all JS in `<script>` with state management, interactive listeners, input validation, and dynamic UI updates.
4. Ensure it looks like a premium, state-of-the-art SaaS product.
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        html_code = (response.text or "").strip()
        if "```html" in html_code or "```" in html_code:
            lines = [ln for ln in html_code.splitlines() if not ln.startswith("```")]
            html_code = "\n".join(lines).strip()

        p = Path(out_path) if out_path else Path.home() / "Desktop" / f"{title[:25].replace(' ', '_')}.html"
        if not p.is_absolute():
            p = Path.home() / "Desktop" / p.name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html_code, encoding="utf-8")

        if auto_open:
            try:
                import subprocess
                subprocess.Popen(f'start "" "{p.resolve()}"', shell=True)
            except Exception:
                pass

        return f"🚀 Interactive web artifact successfully built and launched: {p.name} ({p.resolve()})"
    except Exception as e:
        return f"Artifact build failed: {e}"
