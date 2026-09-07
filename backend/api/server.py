from __future__ import annotations

import json
import sys
from dataclasses import asdict
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.agents.research_agent import ResearchAgent
from backend.database.db import ResearchDatabase
from backend.embeddings.vector_store import JsonVectorStore
from backend.reports.generator import generate_report
from backend.scraping.extractor import ExtractedDocument
from backend.scraping.scraper import WebScraper

DATA_DIR = ROOT / "vector_store"
FRONTEND_DIR = ROOT / "frontend"
agent = ResearchAgent(JsonVectorStore(DATA_DIR / "vectors.json"))
database = ResearchDatabase(ROOT / "backend" / "database" / "deepdive.sqlite3")


class ApiHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self.write_json({"ok": True, "service": "DeepDive"})
            return
        if parsed.path == "/api/reports":
            self.write_json({"reports": database.list_reports()})
            return
        if parsed.path == "/api/memory":
            query = parse_qs(parsed.query).get("q", [""])[0]
            self.write_json({"results": agent.search_memory(query)})
            return
        if parsed.path == "/":
            self.path = "/pages/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/research":
            payload = self.read_json()
            query = (payload.get("query") or "").strip()
            urls = [url.strip() for url in payload.get("urls", []) if url.strip()]
            if not query:
                self.write_json({"error": "Provide a research topic."}, HTTPStatus.BAD_REQUEST)
                return
            result = agent.research(query, urls)
            result["id"] = database.save_report(query, result["report"])
            self.write_json(result)
            return
        if parsed.path == "/api/report/from-text":
            payload = self.read_json()
            query = (payload.get("query") or "Pasted research").strip()
            sources = payload.get("sources", [])
            documents = [
                ExtractedDocument(
                    url=item.get("url", "local://note"),
                    title=item.get("title", "Pasted source"),
                    description=item.get("description", ""),
                    text=item.get("text", ""),
                )
                for item in sources
                if item.get("text")
            ]
            report = asdict(generate_report(query, documents))
            self.write_json({"report": report, "id": database.save_report(query, report)})
            return
        self.write_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def read_json(self) -> dict:
        length = int(self.headers.get("content-length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def write_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ApiHandler)
    print(f"DeepDive running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
