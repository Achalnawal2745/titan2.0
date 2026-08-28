"""
plugins/canvas_designer.py
--------------------------
Creates visual graphic designs, posters, SVG infographics, and artistic layout diagrams.
Adapted from Anthropic Canvas Design Skill.
"""
from __future__ import annotations

import json
from pathlib import Path

PLUGIN = {
    "name": "canvas_designer",
    "description": (
        "Generates visual designs, posters, infographics, SVG diagrams, and aesthetic visual assets. "
        "Use when user asks to design a poster, infographic, visual diagram, promotional banner, "
        "or artistic SVG graphic."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "topic": {
                "type": "STRING",
                "description": "Topic, concept, or event to design a visual piece for.",
            },
            "output_path": {
                "type": "STRING",
                "description": "Optional file path to save the SVG or HTML design (e.g. Desktop/poster.svg).",
            },
            "style": {
                "type": "STRING",
                "description": "Visual style: brutalist | minimalist | futuristic_cyber | swiss_clean | dark_galaxy | bauhaus",
            },
            "width": {
                "type": "INTEGER",
                "description": "Canvas width in pixels (default: 1200)",
            },
            "height": {
                "type": "INTEGER",
                "description": "Canvas height in pixels (default: 800)",
            },
        },
        "required": ["topic"],
    },
}


def run(parameters: dict, player=None, speak=None) -> str:
    topic = parameters.get("topic", "").strip()
    if not topic:
        return "Please specify a design topic."

    style = (parameters.get("style") or "minimalist").lower()
    width = int(parameters.get("width") or 1200)
    height = int(parameters.get("height") or 800)
    out_path = parameters.get("output_path") or ""

    if speak:
        speak(f"Designing {style} visual canvas for {topic}, sir.")

    try:
        from google import genai
        key_path = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
        api_key = ""
        if key_path.exists():
            api_key = json.loads(key_path.read_text(encoding="utf-8")).get("gemini_api_key", "")

        client = genai.Client(api_key=api_key)
        prompt = f"""You are a Master Graphic Designer & Visual Artist.
Create an exceptional, production-grade standalone SVG graphic design on the topic: '{topic}'.
Design Style: {style}
Dimensions: viewBox="0 0 {width} {height}" width="{width}" height="{height}"

Rules:
1. Return ONLY the valid raw <svg ...> ... </svg> code. No markdown fences, no explanatory text.
2. Use modern gradients, geometric accents, typography hierarchy, drop shadows, and rich color palettes.
3. 90% visual composition (shapes, grids, gradients, badges, layout architecture), 10% essential punchy text.
4. Ensure all fonts use clean web-safe system fonts (Inter, Segoe UI, Montserrat, Arial, Trebuchet MS).
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        svg_code = (response.text or "").strip()
        if "```xml" in svg_code or "```svg" in svg_code or "```" in svg_code:
            lines = [ln for ln in svg_code.splitlines() if not ln.startswith("```")]
            svg_code = "\n".join(lines).strip()

        # Target save path
        p = Path(out_path) if out_path else Path.home() / "Desktop" / f"design_{topic[:20].replace(' ', '_')}.svg"
        if not p.is_absolute():
            p = Path.home() / "Desktop" / p.name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(svg_code, encoding="utf-8")

        if player:
            try:
                player.show_content("CANVAS DESIGN", f"Designed SVG visual for {topic}:\nSaved: {p.name}")
            except Exception:
                pass

        return f"🎨 Canvas design successfully rendered and saved to Desktop: {p.name} ({p.resolve()})"
    except Exception as e:
        return f"Canvas design failed: {e}"
