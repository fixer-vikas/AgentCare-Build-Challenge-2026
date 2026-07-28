import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class AuditRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "agentcare.sqlite3")

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        conn.commit()
        return conn

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def log_audit(self, entity_type: str, entity_id: int, action: str, details: str) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO audit_events (entity_type, entity_id, action, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (entity_type, entity_id, action, details, self._now()),
        )
        conn.commit()
        conn.close()

    def get_audit_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT id, entity_type, entity_id, action, details, created_at FROM audit_events ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
