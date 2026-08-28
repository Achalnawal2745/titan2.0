"""
core/web_tools.py — Web Fetch & HTML-to-Markdown Scraper for TITAN.
Ported and adapted from DeepSeek Harness (`packages/web/web-fetch-http`, `packages/web/tool-web`).

Fetches any URL, strips scripts/styles/ads, and extracts clean, readable Markdown content.
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
from typing import Optional
from core.spill import maybe_spill_output


def web_fetch(url: str, max_chars: int = 12000, timeout: int = 15) -> str:
    """
    Fetches a web page URL and converts its body to clean Markdown text.
    Handles redirects, encoding, HTML parsing, and auto-spill for long articles.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return f"Error: Invalid URL scheme '{parsed.scheme}'. Only http and https URLs are allowed."

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip()
            
            raw_bytes = response.read(2_000_000)  # Cap at 2MB download
            raw_html = raw_bytes.decode(charset, errors="replace")

        # Strip scripts, styles, SVGs, and hidden elements
        cleaned_html = re.sub(r"<(script|style|svg|noscript|iframe)[^>]*>.*?</\1>", "", raw_html, flags=re.DOTALL | re.IGNORECASE)
        
        # Try BeautifulSoup if available for high-quality article parsing
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(cleaned_html, "html.parser")
            
            # Remove comments and unwanted tags
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()
                
            # Convert headings and paragraphs
            for h in soup.find_all(["h1", "h2", "h3", "h4"]):
                level = int(h.name[1])
                h.replace_with(f"\n\n{'#' * level} {h.get_text().strip()}\n\n")
                
            for p in soup.find_all("p"):
                p.replace_with(f"\n\n{p.get_text().strip()}\n\n")
                
            for li in soup.find_all("li"):
                li.replace_with(f"\n- {li.get_text().strip()}")
                
            text = soup.get_text()
        except ImportError:
            # Fallback regex extraction
            text = re.sub(r"<[^>]+>", " ", cleaned_html)

        # Normalize whitespace and blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n\n".join(lines)
        
        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + f"\n\n... [Content truncated at {max_chars} characters]"
            
        spill_text, _, _ = maybe_spill_output("web_fetch", f"[Source: {url}]\n\n" + clean_text)
        return spill_text

    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.reason} while fetching '{url}'"
    except urllib.error.URLError as e:
        return f"Network Error: {e.reason} while fetching '{url}'"
    except Exception as e:
        return f"Failed to fetch webpage '{url}': {e}"


# ── Gemini Tool Declaration ──
WEB_FETCH_DECLARATION = {
    "name": "web_fetch",
    "description": (
        "Fetch content directly from a public web page URL and extract its clean text/markdown. "
        "Use when you have a specific URL to read, inspect documentation, or extract webpage contents."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "url": {"type": "STRING", "description": "The HTTP or HTTPS URL of the webpage to fetch"},
            "max_chars": {"type": "INTEGER", "description": "Maximum characters to return (default 12000)"},
        },
        "required": ["url"],
    },
}
