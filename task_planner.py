"""
task_planner.py — TITAN 2.0 Autonomous Task Planner & Reasoning Pipeline
------------------------------------------------------------------------
Handles COMPLEX multi-step tasks that require AI reasoning in the middle.

Examples:
  - "Read questions.docx, answer them, save as answers.docx"
  - "Summarize all files in this folder into a report.docx"
  - "Look at my code file and find bugs, write a report"
  - "Translate this document to Hindi and save it"
"""

import json
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


def answer_questions_in_doc(
    source_path: str,
    output_path: str,
    structure: str = "qa",
    api_key: str = "",
    context: str = ""
) -> str:
    from doc_engine import read_document, create_word_doc

    _log("TASK", f"Reading source: {source_path}")
    doc_text = read_document(source_path)
    doc_text = truncate_text(doc_text)

    if doc_text.startswith("❌"):
        return doc_text

    _log("AI", "Extracting and answering questions...")

    client = genai.Client(api_key=api_key)

    extraction_prompt = f"""You are given a document. Extract ALL questions from it and answer each one comprehensively.

DOCUMENT CONTENT:
{doc_text}

EXTRA CONTEXT / INSTRUCTIONS:
{context if context else "Answer clearly and professionally."}

Return a JSON array where each element is:
{{
  "question": "The exact question from the document",
  "answer": "Your comprehensive answer"
}}

Return ONLY the raw JSON array, no markdown, no explanation."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=extraction_prompt,
        config=types.GenerateContentConfig(temperature=0.2)
    )

    raw = response.text.strip()
    import re
    raw = re.sub(r"```(?:json)?\n?", "", raw).strip().rstrip("```").strip()

    try:
        qa_pairs = json.loads(raw)
    except json.JSONDecodeError:
        _log("PARSE ERROR", raw[:200], Fore.RED)
        return f"❌ AI returned invalid JSON. Raw: {raw[:300]}"

    if not qa_pairs:
        return "❌ No questions found in the document."

    _log("TASK", f"Found {len(qa_pairs)} question(s). Building Word document...")

    content = [
        {"type": "title", "text": "Answered Questions"},
        {"type": "paragraph", "text": f"Source: {Path(source_path).name}"},
        {"type": "divider"},
    ]

    for i, qa in enumerate(qa_pairs, 1):
        question = qa.get("question", "")
        answer = qa.get("answer", "")

        if structure == "qa":
            content.append({"type": "qa", "question": question, "answer": answer})
            content.append({"type": "divider"})

        elif structure == "heading":
            content.append({"type": "heading2", "text": f"Q{i}: {question}"})
            content.append({"type": "paragraph", "text": answer})
            content.append({"type": "divider"})

        elif structure == "numbered":
            content.append({"type": "bold", "text": f"{i}. {question}"})
            content.append({"type": "paragraph", "text": answer})

    return create_word_doc(output_path, content, open_after=True)


def summarize_document(
    source_path: str,
    output_path: str,
    style: str = "bullet",
    api_key: str = ""
) -> str:
    from doc_engine import read_document, create_word_from_markdown

    _log("TASK", f"Summarizing: {source_path}")
    doc_text = read_document(source_path)
    doc_text = truncate_text(doc_text)
    if doc_text.startswith("❌"):
        return doc_text

    client = genai.Client(api_key=api_key)

    style_instructions = {
        "bullet": "Write the summary as clear bullet points grouped by theme.",
        "paragraph": "Write 3-5 well-structured paragraphs.",
        "executive": "Write a short executive summary (max 200 words) followed by key takeaways as bullet points.",
    }.get(style, "Write as bullet points.")

    prompt = f"""Summarize the following document.

{style_instructions}

DOCUMENT:
{doc_text}

Return your response in clean markdown format (use # for headings, - for bullets)."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3)
    )

    return create_word_from_markdown(output_path, response.text, open_after=True)


def rewrite_document(
    source_path: str,
    output_path: str,
    instruction: str,
    api_key: str = ""
) -> str:
    from doc_engine import read_document, create_word_from_markdown

    _log("TASK", f"Rewriting: {source_path} | Instruction: {instruction}")
    doc_text = read_document(source_path)
    if doc_text.startswith("❌"):
        return doc_text

    client = genai.Client(api_key=api_key)

    prompt = f"""Transform the following document according to this instruction:

INSTRUCTION: {instruction}

ORIGINAL DOCUMENT:
{doc_text}

Return the transformed document in clean markdown format."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.4)
    )

    return create_word_from_markdown(output_path, response.text, open_after=True)


def generate_document(
    output_path: str,
    topic: str,
    structure: str = "",
    api_key: str = ""
) -> str:
    from doc_engine import create_word_from_markdown

    _log("TASK", f"Generating document about: {topic}")

    client = genai.Client(api_key=api_key)

    prompt = f"""Write a comprehensive, well-structured document about:

TOPIC: {topic}

FORMATTING: {structure if structure else "Use clear headings (# ##), bullet points where appropriate, and professional language."}

Return in clean markdown format."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.5)
    )

    return create_word_from_markdown(output_path, response.text, open_after=True)


SMART_TASK_MAP = {
    "answer_questions_in_doc": answer_questions_in_doc,
    "summarize_document":      summarize_document,
    "rewrite_document":        rewrite_document,
    "generate_document":       generate_document,
}


def run_smart_task(task: dict, api_key: str) -> str:
    task_type = task.get("action")
    fn = SMART_TASK_MAP.get(task_type)
    if not fn:
        return f"❌ Unknown smart task: '{task_type}'"

    kwargs = {k: v for k, v in task.items() if k != "action"}
    kwargs["api_key"] = api_key

    try:
        return fn(**kwargs)
    except Exception as e:
        return f"❌ Smart task '{task_type}' failed: {e}"
