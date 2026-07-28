import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class DocumentRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "agentcare.sqlite3")
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "..", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            age TEXT,
            phone TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS patient_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            document_name TEXT NOT NULL,
            document_type TEXT NOT NULL,
            status TEXT NOT NULL,
            file_path TEXT,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
        """)
        conn.commit()
        return conn

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def get_patient_documents(self, patient_id: int) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute("SELECT document_type FROM patient_documents WHERE patient_id = ?", (patient_id,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_patient_document(self, patient_id: int, file_name: str, document_type: str, file_obj: Optional[Any] = None, log_audit: Optional[Any] = None) -> Dict[str, Any]:
        conn = self._get_conn()
        existing = conn.execute("SELECT document_type FROM patient_documents WHERE patient_id = ? AND document_type = ?", (patient_id, document_type)).fetchone()
        if existing is not None:
            conn.close()
            return {"status": "duplicate", "document_type": document_type}
        safe_name = f"{uuid.uuid4()}_{Path(file_name).name}"
        file_path = os.path.join(self.upload_dir, safe_name)
        if file_obj is not None:
            with open(file_path, 'wb') as handle:
                handle.write(file_obj.read())
        conn.execute(
            "INSERT INTO patient_documents (patient_id, document_name, document_type, status, file_path, uploaded_at) VALUES (?, ?, ?, ?, ?, ?)",
            (patient_id, file_name, document_type, "uploaded", file_path, self._now()),
        )
        conn.commit()
        conn.close()
        if log_audit is not None:
            log_audit("patient_document", patient_id, "uploaded", f"Uploaded {document_type}")
        return {"status": "uploaded", "document_type": document_type}

    def get_documents_for_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT id, document_name, document_type, status, file_path, uploaded_at FROM patient_documents WHERE patient_id = ? ORDER BY uploaded_at DESC",
            (patient_id,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_document_by_id(self, document_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT id, patient_id, document_name, document_type, status, file_path, uploaded_at FROM patient_documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return dict(row)

    def delete_document(self, document_id: int) -> None:
        conn = self._get_conn()
        conn.execute("DELETE FROM patient_documents WHERE id = ?", (document_id,))
        conn.commit()
        conn.close()

    def add_missing_document(self, patient_id: int, document_type: str) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO patient_documents (patient_id, document_name, document_type, status, file_path, uploaded_at) VALUES (?, ?, ?, ?, ?, ?)",
            (patient_id, document_type.replace("_", " "), document_type, "missing", None, self._now()),
        )
        conn.commit()
        conn.close()
