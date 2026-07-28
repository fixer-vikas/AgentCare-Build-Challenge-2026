import os
import sqlite3
from typing import Any, Dict, Optional


class UserRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "agentcare.sqlite3")

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
        conn.commit()
        return conn

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        user = conn.execute("SELECT id, role, name, email, password_hash FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user is None:
            return None
        return dict(user)

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        user = conn.execute("SELECT id, role, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        if user is None:
            return None
        return dict(user)

    def get_patient_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        patient = conn.execute("SELECT id, age, phone FROM patients WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        if patient is None:
            return None
        return dict(patient)

    def register_user(self, role: str, name: str, email: str, password: str, age: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        from werkzeug.security import generate_password_hash

        conn = self._get_conn()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing is not None:
            conn.close()
            raise ValueError("User already exists")
        user_id = conn.execute(
            "INSERT INTO users (role, name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            (role, name, email, generate_password_hash(password), self._now()),
        ).lastrowid
        patient_id = None
        if role == "patient":
            patient_id = conn.execute(
                "INSERT INTO patients (user_id, age, phone, created_at) VALUES (?, ?, ?, ?)",
                (user_id, age, phone, self._now()),
            ).lastrowid
        else:
            patient_id = None
        conn.commit()
        conn.close()
        return {"id": user_id, "role": role, "name": name, "email": email, "patient_id": patient_id}

    def patient_exists(self, email: str) -> bool:
        conn = self._get_conn()
        row = conn.execute("SELECT id FROM users WHERE email = ? AND role = 'patient'", (email,)).fetchone()
        conn.close()
        return row is not None

    def _now(self) -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
