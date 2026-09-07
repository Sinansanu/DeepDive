from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.request import Request, urlopen

from .utils import DEFAULT_USER_AGENT, is_http_url


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class DuckDuckGoSearch:
    def __init__(self, timeout: int = 12) -> None:
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
        request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        with urlopen(request, timeout=self.timeout) as response:
            html = response.read(800_000).decode("utf-8", errors="replace")
        return self._parse_results(html, limit)

    def _parse_results(self, html: str, limit: int) -> list[SearchResult]:
        results: list[SearchResult] = []
        blocks = re.findall(r'<div class="result__body">(.*?)</div>\s*</div>', html, flags=re.S)
        for block in blocks:
            link_match = re.search(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, flags=re.S)
            if not link_match:
                continue
            resolved_url = self._resolve_url(unescape(link_match.group(1)))
            if not is_http_url(resolved_url):
                continue
            title = self._strip_tags(link_match.group(2))
            snippet_match = re.search(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', block, flags=re.S)
            snippet = self._strip_tags(snippet_match.group(1)) if snippet_match else ""
            results.append(SearchResult(title=title, url=resolved_url, snippet=snippet))
            if len(results) >= limit:
                break
        return results

    def _resolve_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.path == "/l/":
            target = parse_qs(parsed.query).get("uddg", [""])[0]
            return unquote(target)
        return url

    def _strip_tags(self, html: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(html or ""))).strip()
