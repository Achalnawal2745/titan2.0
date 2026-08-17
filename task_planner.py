"""
task_planner.py — TITAN 2.0 Autonomous Task Planner & Reasoning Pipeline
------------------------------------------------------------------------
Handles complex multi-step reasoning tasks and document / presentation generation.

Actions:
  - generate_document       → Executive Word report (.docx) with tables, callout blocks, custom themes
  - generate_presentation   → 16:9 Widescreen PowerPoint (.pptx) with cards, KPI metrics, hero title
  - generate_interactive_deck → Modern HTML slide deck (.html) with keyboard animations
  - answer_questions_in_doc → Extracts & answers questions from any .docx, .pdf, or .txt
  - summarize_document      → Generates structured executive summaries
  - rewrite_document        → Translates or restructures documents
"""

import json
import re
from pathlib import Path
from colorama import Fore, Style, init
from google import genai
from google.genai import types

init(autoreset=True)


def _log(tag: str, msg: str, color=Fore.MAGENTA):
    print(f"{color}[{tag}]{Style.RESET_ALL} {msg}")


def truncate_text(text: str, limit: int = 50000) -> str:
    """Ensure text doesn't exceed the AI's context window."""
    if len(text) > limit:
        return text[:limit] + "\n\n...[TRUNCATED FOR LENGTH]..."
    return text


def _clean_json_response(raw: str) -> str:
    """Strip markdown code blocks from LLM JSON response."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
    return raw.strip()


# ──────────────────────────────────────────────────────────────────────────────
# 1. EXECUTIVE WORD DOCUMENT GENERATION
# ──────────────────────────────────────────────────────────────────────────────

def _detect_font_size(instruction: str, default: str = "normal") -> str | float:
    inst = instruction.lower()
    if m := re.search(r"(\d+(?:\.\d+)?)\s*(?:pt|point|size)", inst):
        return float(m.group(1))
    if any(w in inst for w in ("smaller", "small font", "compact", "tiny", "reduce font", "decrease font", "less size", "resume")):
        return "compact"
    if any(w in inst for w in ("larger", "large font", "big font", "increase font")):
        return "large"
    return default


def generate_document(
    output_path: str,
    topic: str,
    structure: str = "",
    theme: str = "navy",
    image_path: str = "",
    font_size: str = "normal",
    api_key: str = "",
    open_after: bool = True
) -> str:
    """
    Generates a professional executive Word report with structured headings,
    data tables, callout quotes (> blockquotes), bullet lists, and summary takeaways.
    If image_path is provided, automatically embeds the image into the report.
    """
    from doc_engine import create_word_document

    _log("TASK", f"Generating Executive Document on: '{topic}'")
    client = genai.Client(api_key=api_key)

    prompt = f"""You are TITAN's Master Executive Document Writer.
Write a comprehensive, publication-grade professional report about:

TOPIC: {topic}

STRUCTURE & FORMATTING GUIDELINES:
{structure if structure else '''
1. Document Title (# Title) and Subtitle
2. Executive Summary with a key takeaway callout box (use > for callouts)
3. 3-4 Detailed Sections with ## and ### Headings
4. At least ONE formatted data table comparing metrics or features (| Col 1 | Col 2 | Col 3 |)
5. Clear bullet points (- ) and numbered steps (1. )
6. Bold key metrics and terms with **term**
7. Conclusion / Future Outlook
'''}

Write directly in clean Markdown format with high quality, in-depth content. Do not include meta commentary."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.4)
    )

    doc_text = response.text.strip()
    
    # If image_path is provided, embed it into the markdown after the first section
    if image_path:
        img_md = f"\n\n![Visual Context]({image_path})\n\n"
        if "\n## " in doc_text:
            parts = doc_text.split("\n## ", 1)
            doc_text = parts[0] + img_md + "\n## " + parts[1]
        else:
            doc_text = img_md + doc_text

    # Extract Title and Subtitle if present
    lines = doc_text.split("\n")
    title = topic
    subtitle = "Comprehensive Strategic Intelligence Report"
    for l in lines[:5]:
        if l.startswith("# "):
            title = l[2:].strip()
            break

    f_size = _detect_font_size(structure or topic, default=font_size)

    return create_word_document(
        path=output_path,
        markdown_content=doc_text,
        title=title,
        subtitle=subtitle,
        author="",
        theme=theme,
        font_size=f_size,
        open_after=open_after
    )


# ──────────────────────────────────────────────────────────────────────────────
# 2. POWERPOINT PRESENTATION DECK GENERATION (.pptx)
# ──────────────────────────────────────────────────────────────────────────────

def generate_presentation(
    output_path: str,
    topic: str,
    num_slides: int = 5,
    theme: str = "midnight",
    image_path: str = "",
    api_key: str = "",
    open_after: bool = True
) -> str:
    """
    Generates a 16:9 Widescreen PowerPoint Presentation from structured slide data.
    Uses AI to generate a curated slide structure with title, multi-column cards,
    KPI metrics, and detailed bullet slides.
    """
    from doc_engine import create_presentation_deck

    _log("TASK", f"Generating PowerPoint Presentation on: '{topic}' ({num_slides} slides)")
    client = genai.Client(api_key=api_key)

    prompt = f"""You are TITAN's Master Presentation Architect.
Create a compelling, professional {num_slides}-slide presentation deck about:

TOPIC: {topic}

Return a strictly valid JSON array of slide objects matching this exact format:

[
  {{
    "type": "title",
    "category": "STRATEGIC BRIEFING",
    "title": "Main Presentation Title",
    "subtitle": "Clear and impactful subtitle",
    "author": "TITAN Intelligence"
  }},
  {{
    "type": "cards",
    "category": "CORE PILLARS",
    "title": "Key Strategic Drivers",
    "items": [
      {{
        "header": "Pillar 1: Innovation",
        "bullets": ["Autonomous agent workflows", "Zero-latency real-time response", "Edge computing"]
      }},
      {{
        "header": "Pillar 2: Scalability",
        "bullets": ["Cloud & local hybrid compute", "Deterministic pipelines", "High throughput"]
      }},
      {{
        "header": "Pillar 3: Security",
        "bullets": ["Biometric voice & face gate", "Sandboxed execution", "Zero data leak"]
      }}
    ]
  }},
  {{
    "type": "metrics",
    "category": "PERFORMANCE IMPACT",
    "title": "Key Performance Indicators",
    "metrics": [
      {{"value": "10x", "label": "Execution Speed", "subtext": "vs manual workflows"}},
      {{"value": "99.4%", "label": "Accuracy Rate", "subtext": "verified in sandbox"}},
      {{"value": "<50ms", "label": "Interruption Latency", "subtext": "real-time barge-in"}},
      {{"value": "$1.2M", "label": "Projected ROI", "subtext": "annual efficiency gain"}}
    ]
  }},
  {{
    "type": "bullets",
    "category": "STRATEGIC ROADMAP",
    "title": "Phased Execution Plan",
    "bullets": [
      "Phase 1: Deploy core neural bridges and autonomous browser copilots",
      "Phase 2: Integrate continuous learning and long-term vector graph memory",
      "Phase 3: Scale multi-agent swarm orchestration across enterprise endpoints"
    ]
  }}
]

Supported slide types:
- 'title' (Hero title card)
- 'split_image' (Split-screen image on left, bullets on right)
- 'cards' (2 or 3 structured comparison cards)
- 'metrics' (2 to 4 massive KPI stats)
- 'bullets' (Deep-dive content with bullet points)

Generate {num_slides} high-impact slides tailored to '{topic}'.
Return ONLY the raw JSON array, with NO markdown backticks or commentary."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3)
    )

    clean_json = _clean_json_response(response.text)

    try:
        slides_data = json.loads(clean_json)
    except Exception as e:
        _log("JSON ERROR", f"Failed to parse slide JSON: {e}\nRaw:\n{clean_json[:300]}", Fore.RED)
        slides_data = [
            {"type": "title", "title": topic, "subtitle": "Executive Briefing", "category": "EXECUTIVE DECK"},
            {"type": "bullets", "title": "Overview", "bullets": [f"Key insights regarding {topic}", "High-level strategic analysis", "Next execution milestones"]}
        ]

    # If user provided a specific image_path, inject a split_image slide using that image!
    if image_path:
        img_slide = {
            "type": "split_image",
            "category": "VISUAL ANALYSIS",
            "title": "Visual Context & Analysis",
            "image": image_path,
            "bullets": [
                f"Integrated reference image: {Path(image_path).name}",
                f"Core visual alignment with {topic}",
                "Detailed architectural representation"
            ]
        }
        # Insert after title slide
        if len(slides_data) > 1:
            slides_data.insert(1, img_slide)
        else:
            slides_data.append(img_slide)

    return create_presentation_deck(
        path=output_path,
        slides_data=slides_data,
        deck_title=topic,
        theme=theme,
        open_after=open_after
    )


# ──────────────────────────────────────────────────────────────────────────────
# 3. INTERACTIVE BROWSER PRESENTATION (.html)
# ──────────────────────────────────────────────────────────────────────────────

def generate_interactive_deck(
    output_path: str,
    topic: str,
    num_slides: int = 5,
    api_key: str = "",
    open_after: bool = True
) -> str:
    """
    Generates a standalone, interactive HTML5 presentation deck with glassmorphic UI,
    animated transitions, and keyboard navigation.
    """
    from doc_engine import create_interactive_deck

    _log("TASK", f"Generating Interactive HTML Deck on: '{topic}'")
    client = genai.Client(api_key=api_key)

    prompt = f"""Generate a {num_slides}-slide interactive deck structure for: '{topic}'.
Return a raw JSON array of slides (same format with types: 'title', 'cards', 'metrics', 'bullets').
Return ONLY raw JSON, no backticks."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3)
    )

    clean_json = _clean_json_response(response.text)
    try:
        slides_data = json.loads(clean_json)
    except Exception:
        slides_data = [
            {"type": "title", "title": topic, "subtitle": "Interactive Presentation", "category": "TITAN LIVE"},
            {"type": "bullets", "title": "Overview", "bullets": [f"Interactive slide presentation on {topic}", "Keyboard navigation with Arrow Keys / Space", "Press F for Fullscreen"]}
        ]

    return create_interactive_deck(
        path=output_path,
        slides_data=slides_data,
        deck_title=topic,
        open_after=open_after
    )


# ──────────────────────────────────────────────────────────────────────────────
# 4. DOCUMENT REASONING (Q&A, Summarize, Rewrite)
# ──────────────────────────────────────────────────────────────────────────────

def answer_questions_in_doc(
    source_path: str,
    output_path: str,
    structure: str = "qa",
    api_key: str = "",
    context: str = ""
) -> str:
    from doc_engine import read_document, create_word_document

    _log("TASK", f"Reading source: {source_path}")
    doc_text = read_document(source_path)
    doc_text = truncate_text(doc_text)

    if doc_text.startswith("❌"):
        return doc_text

    _log("AI", "Extracting and answering questions...")
    client = genai.Client(api_key=api_key)

    extraction_prompt = f"""Extract ALL questions from the document below and provide thorough, accurate answers for each.

DOCUMENT:
{doc_text}

EXTRA CONTEXT: {context}

Return in Markdown format with:
# Answered Questions Report
Source: {Path(source_path).name}

## Q1: [Question 1]
> **Answer:** [Detailed Answer]

## Q2: [Question 2]
> **Answer:** [Detailed Answer]
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=extraction_prompt,
        config=types.GenerateContentConfig(temperature=0.2)
    )

    return create_word_document(
        path=output_path,
        markdown_content=response.text,
        title="Answered Questions Report",
        subtitle=f"Source Document: {Path(source_path).name}",
        open_after=True
    )


def summarize_document(
    source_path: str,
    output_path: str,
    style: str = "executive",
    api_key: str = ""
) -> str:
    from doc_engine import read_document, create_word_document

    _log("TASK", f"Summarizing: {source_path}")
    doc_text = read_document(source_path)
    doc_text = truncate_text(doc_text)
    if doc_text.startswith("❌"):
        return doc_text

    client = genai.Client(api_key=api_key)

    prompt = f"""Summarize this document with high executive quality.

DOCUMENT:
{doc_text}

FORMAT IN MARKDOWN:
# Executive Summary Report
> **Key Takeaway:** [One-sentence overarching insight]

## Overview
[Paragraph summary]

## Key Findings & Core Themes
- Point 1
- Point 2

## Action Items & Next Steps
1. Step 1
2. Step 2
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3)
    )

    return create_word_document(
        path=output_path,
        markdown_content=response.text,
        title="Executive Summary",
        subtitle=f"Analysis of {Path(source_path).name}",
        open_after=True
    )


def rewrite_document(
    source_path: str,
    output_path: str,
    instruction: str,
    api_key: str = ""
) -> str:
    from doc_engine import read_document, create_word_document

    _log("TASK", f"Rewriting: {source_path} | Instruction: {instruction}")
    doc_text = read_document(source_path)
    if doc_text.startswith("❌"):
        return doc_text

    client = genai.Client(api_key=api_key)

    prompt = f"""Transform the following document according to this instruction:
INSTRUCTION: {instruction}

ORIGINAL DOCUMENT:
{doc_text}

Return the transformed content in rich, structured Markdown."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.4)
    )

    f_size = _detect_font_size(instruction)

    return create_word_document(
        path=output_path,
        markdown_content=response.text,
        title="",
        subtitle="",
        author="",
        font_size=f_size,
        open_after=True
    )


def fill_template(
    source_path: str,
    output_path: str = "",
    instruction: str = "",
    replacements: dict = None,
    api_key: str = "",
    open_after: bool = True
) -> str:
    """
    Fills an existing Word template document with new data and instructions.
    Uses AI to analyze what fields to replace, keeping all fonts, tables, and logos.
    """
    from doc_engine import fill_docx_template, read_docx

    if not replacements and instruction:
        doc_text = read_docx(source_path)
        client = genai.Client(api_key=api_key)
        prompt = f"""You are a document template filler.
Analyze the template text and user instruction, and determine what placeholders/keys to replace.

TEMPLATE TEXT:
{doc_text[:15000]}

USER INSTRUCTION:
{instruction}

Return a strictly valid JSON dictionary mapping the exact placeholder string to the new replacement value:
{{
  "[CLIENT_NAME]": "Acme Corp",
  "[DATE]": "August 18, 2026",
  "[TOTAL]": "$15,000"
}}

Return ONLY the raw JSON dictionary, no backticks."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2)
        )
        clean_json = _clean_json_response(response.text)
        try:
            replacements = json.loads(clean_json)
        except Exception:
            replacements = {}

    if not output_path:
        desktop = Path.home() / "Desktop"
        output_path = str(desktop / f"Filled_{Path(source_path).name}")

    return fill_docx_template(
        template_path=source_path,
        output_path=output_path,
        replacements=replacements or {},
        open_after=open_after
    )


# ──────────────────────────────────────────────────────────────────────────────
# ROUTING DISPATCH MAP
# ──────────────────────────────────────────────────────────────────────────────

SMART_TASK_MAP = {
    "generate_document":         generate_document,
    "generate_presentation":     generate_presentation,
    "generate_interactive_deck": generate_interactive_deck,
    "answer_questions_in_doc":   answer_questions_in_doc,
    "summarize_document":        summarize_document,
    "rewrite_document":          rewrite_document,
    "fill_template":             fill_template,
}


def run_smart_task(task: dict, api_key: str) -> str:
    task_type = task.get("action")
    fn = SMART_TASK_MAP.get(task_type)
    if not fn:
        return f"❌ Unknown smart task: '{task_type}'. Supported actions: {list(SMART_TASK_MAP.keys())}"

    kwargs = {k: v for k, v in task.items() if k != "action"}
    kwargs["api_key"] = api_key

    # Auto-generate default output path if not specified
    if "output_path" not in kwargs or not kwargs["output_path"]:
        desktop = Path.home() / "Desktop"
        topic_slug = "".join(c if c.isalnum() else "_" for c in kwargs.get("topic", "output")).strip("_")[:30]
        ext = ".docx" if task_type in ("generate_document", "fill_template", "rewrite_document", "summarize_document", "answer_questions_in_doc") else (".pptx" if task_type == "generate_presentation" else ".html")
        kwargs["output_path"] = str(desktop / f"{topic_slug}{ext}")

    try:
        return fn(**kwargs)
    except Exception as e:
        return f"❌ Smart task '{task_type}' failed: {e}"
