"""
doc_engine.py — TITAN 2.0 Document Intelligence Engine
------------------------------------------------------
Read from: .txt, .docx, .pdf, .pptx, .xlsx
Write to:  .docx (formatted Word), .txt, .md

This is what lets TITAN 2.0 do tasks like:
  "Read questions.docx, answer each question, save as answers.docx with H1/H2 structure"
"""

from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

def _log(msg: str, color=Fore.CYAN):
    print(f"{color}[DOC]{Style.RESET_ALL} {msg}")

def read_docx(path: str) -> str:
    """Extract all text from a .docx file using Unstructured for better layout awareness."""
    try:
        from unstructured.partition.docx import partition_docx
        elements = partition_docx(filename=path)
        return "\n\n".join([str(el) for el in elements])
    except Exception:
        try:
            from docx import Document
            doc = Document(path)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            return f"❌ Cannot read docx '{path}': {e}"


def read_pdf(path: str) -> str:
    """Extract structured Markdown from a PDF using Docling (Vision-based)."""
    try:
        from docling.document_converter import DocumentConverter
        _log("Using Docling (Vision) to parse PDF...")
        converter = DocumentConverter()
        result = converter.convert(path)
        return result.document.export_to_markdown()
    except Exception as e:
        _log(f"Docling failed, falling back to Unstructured: {e}", Fore.YELLOW)
        try:
            from unstructured.partition.pdf import partition_pdf
            elements = partition_pdf(filename=path)
            return "\n\n".join([str(el) for el in elements])
        except Exception as e2:
            return f"❌ All PDF readers failed: {e2}"


def read_document(path: str) -> str:
    """Auto-detect and read any document type using Unstructured / Docling."""
    _log(f"Analyzing Document: {path}")
    p = Path(path)
    ext = p.suffix.lower()

    if not p.exists():
        return f"❌ File not found: {path}"

    if ext == ".pdf":
        return read_pdf(path)
    
    try:
        from unstructured.partition.auto import partition
        _log(f"Using Unstructured for {ext} format...")
        elements = partition(filename=str(path))
        return "\n\n".join([str(el) for el in elements])
    except Exception as e:
        _log(f"Unstructured fallback failed: {e}. Trying raw read...", Fore.YELLOW)
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except Exception as e3:
            return f"❌ Unsupported file type '{ext}': {e3}"


def create_word_doc(path: str, content: list[dict], open_after: bool = True) -> str:
    """
    Create a formatted Word document from structured content.
    """
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        return "❌ python-docx not installed. Run: pip install python-docx"

    _log(f"Creating Word doc: {path}")
    doc = Document()

    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1.2)
    section.right_margin = Inches(1.2)

    def set_font(run, size_pt: int, bold: bool = False, color: tuple = None):
        run.font.name = "Calibri"
        run.font.size = Pt(size_pt)
        run.font.bold = bold
        if color:
            run.font.color.rgb = RGBColor(*color)

    for block in content:
        btype = block.get("type", "paragraph")
        text = block.get("text", "")

        if btype == "title":
            p = doc.add_heading(text, level=0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        elif btype == "heading1":
            doc.add_heading(text, level=1)

        elif btype == "heading2":
            doc.add_heading(text, level=2)

        elif btype == "heading3":
            doc.add_heading(text, level=3)

        elif btype == "paragraph":
            p = doc.add_paragraph(text)
            p.paragraph_format.space_after = Pt(6)

        elif btype == "bullet":
            doc.add_paragraph(text, style="List Bullet")

        elif btype == "numbered":
            doc.add_paragraph(text, style="List Number")

        elif btype == "bold":
            p = doc.add_paragraph()
            run = p.add_run(text)
            set_font(run, 11, bold=True)

        elif btype == "divider":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run("─" * 60)
            run.font.color.rgb = RGBColor(180, 180, 180)

        elif btype == "qa":
            question = block.get("question", "")
            answer = block.get("answer", "")

            p_q = doc.add_paragraph()
            r = p_q.add_run(f"Q: {question}")
            set_font(r, 11, bold=True, color=(31, 73, 125))

            p_a = doc.add_paragraph()
            r2 = p_a.add_run(f"A: {answer}")
            set_font(r2, 11, bold=False)
            p_a.paragraph_format.space_after = Pt(10)

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(p))
    _log(f"Saved: {path}", Fore.GREEN)

    if open_after:
        import subprocess
        subprocess.Popen(f'start "" "{p.resolve()}"', shell=True)

    return f"✅ Word document created: {path}"


def create_word_from_markdown(path: str, markdown_text: str, open_after: bool = True) -> str:
    """
    Parse simple markdown and convert to a Word doc.
    """
    _log(f"Parsing markdown → Word: {path}")
    import re

    content = []
    lines = markdown_text.strip().split("\n")
    numbered_re = re.compile(r"^\d+\.\s+(.+)")

    for line in lines:
        line = line.rstrip()
        if not line:
            continue

        if line.startswith("# "):
            content.append({"type": "heading1", "text": line[2:].strip()})
        elif line.startswith("## "):
            content.append({"type": "heading2", "text": line[3:].strip()})
        elif line.startswith("### "):
            content.append({"type": "heading3", "text": line[4:].strip()})
        elif line.startswith("- ") or line.startswith("* "):
            content.append({"type": "bullet", "text": line[2:].strip()})
        elif line.startswith("---"):
            content.append({"type": "divider"})
        elif m := numbered_re.match(line):
            content.append({"type": "numbered", "text": m.group(1).strip()})
        elif line.startswith("**") and line.endswith("**"):
            content.append({"type": "bold", "text": line.strip("*").strip()})
        else:
            clean = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            content.append({"type": "paragraph", "text": clean})

    return create_word_doc(path, content, open_after=open_after)
