from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4


class ResearchDatabase:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save_report(self, query: str, payload: dict) -> str:
        report_id = str(uuid4())
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO reports (id, query, payload) VALUES (?, ?, ?)",
                (report_id, query, json.dumps(payload)),
            )
        return report_id

    def list_reports(self) -> list[dict]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT id, query, payload, created_at FROM reports ORDER BY created_at DESC"
            ).fetchall()
        return [
            {
                "id": row["id"],
                "query": row["query"],
                "created_at": row["created_at"],
                "payload": json.loads(row["payload"]),
            }
            for row in rows
        ]
