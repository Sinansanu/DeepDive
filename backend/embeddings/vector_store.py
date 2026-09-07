from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from uuid import uuid4

from .simple_embeddings import cosine_similarity, embed_text


@dataclass
class VectorRecord:
    id: str
    url: str
    title: str
    text: str
    vector: list[float]


class JsonVectorStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def all(self) -> list[VectorRecord]:
        return [VectorRecord(**item) for item in json.loads(self.path.read_text(encoding="utf-8"))]

    def add(self, url: str, title: str, text: str) -> VectorRecord:
        record = VectorRecord(
            id=str(uuid4()),
            url=url,
            title=title,
            text=text,
            vector=embed_text(f"{title}\n{text}"),
        )
        records = self.all()
        records.append(record)
        self.path.write_text(json.dumps([asdict(item) for item in records], indent=2), encoding="utf-8")
        return record

    def search(self, query: str, limit: int = 6) -> list[tuple[VectorRecord, float]]:
        query_vector = embed_text(query)
        ranked = [(record, cosine_similarity(query_vector, record.vector)) for record in self.all()]
        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked[:limit]
