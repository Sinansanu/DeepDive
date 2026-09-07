from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from backend.scraping.extractor import ExtractedDocument
from backend.scraping.utils import hostname, truncate


STOPWORDS = {
    "about", "after", "again", "also", "and", "are", "because", "been", "but", "can",
    "from", "has", "have", "into", "its", "more", "not", "our", "over", "that", "the",
    "their", "this", "through", "was", "were", "which", "with", "your",
}


@dataclass
class ResearchReport:
    title: str
    summary: str
    key_insights: list[str]
    sources: list[dict[str, str]]
    related_terms: list[str]


def split_sentences(text: str) -> list[str]:
    return [item.strip() for item in re.split(r"(?<=[.!?])\s+", text or "") if len(item.strip()) > 40]


def important_terms(text: str, limit: int = 10) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9-]{3,}", text.lower())
    counts = Counter(word for word in words if word not in STOPWORDS)
    return [word for word, _ in counts.most_common(limit)]


def sentence_score(sentence: str, terms: list[str]) -> int:
    lower = sentence.lower()
    return sum(1 for term in terms if term in lower)


def generate_report(query: str, documents: list[ExtractedDocument]) -> ResearchReport:
    combined = "\n".join(document.text for document in documents)
    terms = important_terms(f"{query}\n{combined}")
    sentences = split_sentences(combined)
    ranked = sorted(sentences, key=lambda sentence: sentence_score(sentence, terms), reverse=True)
    insights = [truncate(sentence, 240) for sentence in ranked[:5]]
    if not insights:
        insights = [document.description for document in documents if document.description][:5]
    summary_seed = " ".join(insights[:3]) or "No strong textual summary could be extracted from the provided sources."
    sources = [
        {
            "title": document.title,
            "url": document.url,
            "site": hostname(document.url),
            "description": truncate(document.description or document.text, 180),
        }
        for document in documents
    ]
    return ResearchReport(
        title=f"Research report: {query}",
        summary=truncate(summary_seed, 700),
        key_insights=insights,
        sources=sources,
        related_terms=terms,
    )
