from __future__ import annotations

import re
from urllib.parse import urlparse


DEFAULT_USER_AGENT = (
    "DeepDiveResearchBot/0.1 "
    "(educational local research assistant; respects robots and timeouts)"
)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def is_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def hostname(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def truncate(text: str, limit: int) -> str:
    text = normalize_whitespace(text)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "..."
