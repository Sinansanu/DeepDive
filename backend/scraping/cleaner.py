from __future__ import annotations

import re
from html import unescape

from .utils import normalize_whitespace


SCRIPT_STYLE_RE = re.compile(
    r"<(script|style|noscript|svg|canvas|template)\b[^>]*>.*?</\1>",
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")
ENTITY_RE = re.compile(r"&[a-zA-Z0-9#]+;")


def strip_html_noise(html: str) -> str:
    return SCRIPT_STYLE_RE.sub(" ", html or "")


def clean_text(text: str) -> str:
    text = unescape(text or "")
    text = ENTITY_RE.sub(" ", text)
    text = normalize_whitespace(text)
    text = re.sub(r"(\b[a-zA-Z]\b\s*){8,}", " ", text)
    return normalize_whitespace(text)


def html_to_plain_text(html: str) -> str:
    html = strip_html_noise(html)
    html = re.sub(r"</(p|div|section|article|li|h[1-6]|br)>", "\n", html, flags=re.I)
    return clean_text(TAG_RE.sub(" ", html))
