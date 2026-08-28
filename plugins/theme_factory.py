"""
plugins/theme_factory.py
------------------------
Curated typography, color palettes, and visual design systems for presentations and documents.
Adapted from Anthropic Agent Skills Theme Factory.
"""
from __future__ import annotations

THEMES = {
    "tech_innovation": {
        "name": "Tech Innovation",
        "primary": "#0066FF",
        "secondary": "#00FFFF",
        "dark": "#1E1E1E",
        "light": "#FFFFFF",
        "accent": "#0052CC",
        "fonts": {"header": "Segoe UI", "body": "Segoe UI"},
        "use_case": "Tech startups, software launches, AI/ML presentations, digital transformation",
    },
    "modern_minimalist": {
        "name": "Modern Minimalist",
        "primary": "#2C3E50",
        "secondary": "#7F8C8D",
        "dark": "#1A1A1A",
        "light": "#F8F9F9",
        "accent": "#BDC3C7",
        "fonts": {"header": "Arial", "body": "Calibri"},
        "use_case": "Executive briefings, architecture reviews, clean product showcases",
    },
    "midnight_galaxy": {
        "name": "Midnight Galaxy",
        "primary": "#6C5CE7",
        "secondary": "#A29BFE",
        "dark": "#0F0F1E",
        "light": "#DFE6E9",
        "accent": "#FD79A8",
        "fonts": {"header": "Century Gothic", "body": "Segoe UI"},
        "use_case": "Creative pitches, gaming, futuristic concepts, dark-mode decks",
    },
    "ocean_depths": {
        "name": "Ocean Depths",
        "primary": "#0984E3",
        "secondary": "#74B9FF",
        "dark": "#0A3D62",
        "light": "#F0F8FF",
        "accent": "#00CEC9",
        "fonts": {"header": "Trebuchet MS", "body": "Calibri"},
        "use_case": "Corporate annual reports, finance, healthcare, maritime logistics",
    },
    "golden_hour": {
        "name": "Golden Hour",
        "primary": "#E17055",
        "secondary": "#FDCB6E",
        "dark": "#2D3436",
        "light": "#FFFDF9",
        "accent": "#D63031",
        "fonts": {"header": "Georgia", "body": "Garamond"},
        "use_case": "Marketing, keynote talks, lifestyle brands, portfolio decks",
    },
    "forest_canopy": {
        "name": "Forest Canopy",
        "primary": "#00B894",
        "secondary": "#55EFC4",
        "dark": "#1B3B2B",
        "light": "#F4FDF8",
        "accent": "#006266",
        "fonts": {"header": "Verdana", "body": "Calibri"},
        "use_case": "Sustainability, agriculture, ESG reports, environmental tech",
    },
    "academic_formal": {
        "name": "Academic Formal",
        "primary": "#000000",
        "secondary": "#333333",
        "dark": "#000000",
        "light": "#FFFFFF",
        "accent": "#1F4E79",
        "fonts": {"header": "Times New Roman", "body": "Times New Roman"},
        "use_case": "College/IEEE papers, research theses, formal institutional reports",
    },
}

PLUGIN = {
    "name": "theme_factory",
    "description": (
        "Provides curated professional color palettes, typography rules, and design themes "
        "for presentations and documents. Use to select or inspect color themes (e.g. tech_innovation, "
        "midnight_galaxy, ocean_depths, golden_hour, academic_formal)."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "get_theme | list_themes | recommend",
            },
            "theme_name": {
                "type": "STRING",
                "description": "Name of theme: tech_innovation, modern_minimalist, midnight_galaxy, ocean_depths, golden_hour, forest_canopy, academic_formal",
            },
            "topic": {
                "type": "STRING",
                "description": "Topic or context to get an automated theme recommendation for.",
            },
        },
        "required": ["action"],
    },
}


def run(parameters: dict, player=None, speak=None) -> str:
    action = (parameters.get("action") or "list_themes").lower().strip()
    theme_name = (parameters.get("theme_name") or "").lower().replace("-", "_").strip()
    topic = (parameters.get("topic") or "").lower()

    if action == "list_themes":
        names = [f"• **{t['name']}** (`{k}`): {t['use_case']}" for k, t in THEMES.items()]
        return "Available Design Themes:\n" + "\n".join(names)

    if action == "recommend" or (action == "get_theme" and not theme_name and topic):
        rec = "tech_innovation"
        if any(w in topic for w in ("finance", "health", "water", "sea", "ocean", "corp")):
            rec = "ocean_depths"
        elif any(w in topic for w in ("green", "tree", "nature", "sustainability", "eco", "esg")):
            rec = "forest_canopy"
        elif any(w in topic for w in ("game", "future", "dark", "space", "crypto")):
            rec = "midnight_galaxy"
        elif any(w in topic for w in ("college", "thesis", "ieee", "paper", "academic", "university")):
            rec = "academic_formal"
        elif any(w in topic for w in ("warm", "food", "art", "fashion", "brand")):
            rec = "golden_hour"
        t = THEMES[rec]
        return f"Recommended theme for '{topic}': **{t['name']}** (`{rec}`)\nColors: Primary={t['primary']}, Secondary={t['secondary']}, Dark={t['dark']}\nFonts: {t['fonts']['header']} / {t['fonts']['body']}"

    if theme_name in THEMES:
        t = THEMES[theme_name]
        return (
            f"🎨 **Theme: {t['name']}**\n"
            f"- Primary: `{t['primary']}`\n"
            f"- Secondary: `{t['secondary']}`\n"
            f"- Accent: `{t['accent']}`\n"
            f"- Dark Base: `{t['dark']}` | Light Base: `{t['light']}`\n"
            f"- Fonts: Headers={t['fonts']['header']}, Body={t['fonts']['body']}\n"
            f"- Best for: {t['use_case']}"
        )

    return f"Theme '{theme_name}' not found. Available: {', '.join(THEMES.keys())}"
