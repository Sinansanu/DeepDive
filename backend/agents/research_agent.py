from __future__ import annotations

from dataclasses import asdict

from backend.embeddings.vector_store import JsonVectorStore
from backend.reports.generator import generate_report
from backend.scraping.extractor import ExtractedDocument
from backend.scraping.scraper import WebScraper
from backend.scraping.searcher import DuckDuckGoSearch


class ResearchAgent:
    def __init__(
        self,
        vector_store: JsonVectorStore,
        scraper: WebScraper | None = None,
        searcher: DuckDuckGoSearch | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.scraper = scraper or WebScraper()
        self.searcher = searcher or DuckDuckGoSearch()

    def research(self, query: str, urls: list[str], search_limit: int = 5) -> dict:
        discovered = []
        if not urls:
            discovered = self.searcher.search(query, limit=search_limit)
            urls = [result.url for result in discovered]
        scrape_results = self.scraper.scrape_many(urls)
        documents: list[ExtractedDocument] = []
        errors: list[dict[str, str]] = []
        for result in scrape_results:
            if result.ok and result.document:
                documents.append(result.document)
                self.vector_store.add(result.document.url, result.document.title, result.document.text[:6000])
            else:
                errors.append({"url": result.url, "error": result.error or "Unknown scrape error"})

        report = generate_report(query, documents)
        return {
            "report": asdict(report),
            "scraped": len(documents),
            "discovered": [asdict(result) for result in discovered],
            "errors": errors,
        }

    def search_memory(self, query: str) -> list[dict]:
        return [
            {
                "id": record.id,
                "title": record.title,
                "url": record.url,
                "score": round(score, 4),
                "snippet": record.text[:260],
            }
            for record, score in self.vector_store.search(query)
        ]
