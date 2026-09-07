from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser

from .cleaner import clean_text, html_to_plain_text, strip_html_noise
from .utils import truncate


@dataclass
class ExtractedDocument:
    url: str
    title: str
    description: str
    text: str


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "meta":
            name = attr_map.get("name", "").lower()
            prop = attr_map.get("property", "").lower()
            if name == "description" or prop == "og:description":
                self.description = attr_map.get("content", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def extract_metadata(html: str) -> tuple[str, str]:
    parser = MetadataParser()
    parser.feed(html or "")
    title = clean_text(" ".join(parser.title_parts))
    description = clean_text(parser.description)
    return title, description


def extract_main_text(html: str) -> str:
    html = strip_html_noise(html)
    article_match = re.search(r"<article\b[^>]*>(.*?)</article>", html, flags=re.I | re.S)
    if article_match:
        article_text = html_to_plain_text(article_match.group(1))
        if len(article_text) > 400:
            return article_text
    return html_to_plain_text(html)


def extract_document(url: str, html: str) -> ExtractedDocument:
    title, description = extract_metadata(html)
    text = extract_main_text(html)
    if not description and text:
        description = truncate(text, 220)
    return ExtractedDocument(url=url, title=title or url, description=description, text=text)
