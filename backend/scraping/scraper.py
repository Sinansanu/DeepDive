from __future__ import annotations

import socket
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .extractor import ExtractedDocument, extract_document
from .utils import DEFAULT_USER_AGENT, is_http_url


@dataclass
class ScrapeResult:
    ok: bool
    url: str
    document: ExtractedDocument | None = None
    error: str | None = None


class WebScraper:
    def __init__(self, timeout: int = 12, user_agent: str = DEFAULT_USER_AGENT) -> None:
        self.timeout = timeout
        self.user_agent = user_agent

    def fetch_html(self, url: str) -> str:
        if not is_http_url(url):
            raise ValueError("Only http and https URLs are supported.")
        request = Request(url, headers={"User-Agent": self.user_agent})
        with urlopen(request, timeout=self.timeout) as response:
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                raise ValueError(f"Unsupported content type: {content_type or 'unknown'}")
            raw = response.read(1_500_000)
        return raw.decode("utf-8", errors="replace")

    def scrape(self, url: str) -> ScrapeResult:
        try:
            html = self.fetch_html(url)
            return ScrapeResult(ok=True, url=url, document=extract_document(url, html))
        except (HTTPError, URLError, TimeoutError, socket.timeout, ValueError) as exc:
            return ScrapeResult(ok=False, url=url, error=str(exc))

    def scrape_many(self, urls: list[str]) -> list[ScrapeResult]:
        return [self.scrape(url) for url in urls]
