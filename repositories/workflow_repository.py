import os
import sqlite3
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class WorkflowRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "agentcare.sqlite3")

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS workflow_runs (
            id TEXT PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            request TEXT NOT NULL,
            status TEXT NOT NULL,
            department TEXT NOT NULL,
            steps TEXT NOT NULL,
            summary TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
        """)
        conn.commit()
        return conn

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        workflow = conn.execute(
            "SELECT id, patient_id, patient_name, request, status, department, steps, summary, created_at FROM workflow_runs WHERE id = ?",
            (workflow_id,),
        ).fetchone()
        conn.close()
        if workflow is None:
            return None
        raw_steps = json.loads(workflow["steps"]) if workflow["steps"] else []
        return {
            "id": workflow["id"],
            "patient_id": workflow["patient_id"],
            "patient_name": workflow["patient_name"],
            "request": workflow["request"],
            "status": workflow["status"],
            "department": workflow["department"],
            "steps": raw_steps,
            "summary": workflow["summary"],
            "created_at": workflow["created_at"],
        }

    def persist_workflow(self, workflow_id: str, patient_id: int, patient_name: str, request: str, department: str, steps: List[Dict[str, Any]], summary: Optional[str] = None) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO workflow_runs (id, patient_id, patient_name, request, status, department, steps, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (workflow_id, patient_id, patient_name, request, "completed", department, json.dumps(steps), summary, self._now()),
        )
        conn.commit()
        conn.close()

    def update_workflow_status(self, workflow_id: str, status: str) -> None:
        conn = self._get_conn()
        conn.execute("UPDATE workflow_runs SET status = ? WHERE id = ?", (status, workflow_id))
        conn.commit()
        conn.close()

    def get_workflow_for_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute("SELECT id, request, status, department, summary, created_at FROM workflow_runs WHERE patient_id = ? ORDER BY created_at DESC LIMIT 5", (patient_id,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]
