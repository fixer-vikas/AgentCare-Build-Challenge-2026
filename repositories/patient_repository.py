import os
import sqlite3
import json
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class PatientRepository:
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
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TEXT NOT NULL
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            specialty TEXT,
            availability TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY(department_id) REFERENCES departments(id)
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS appointment_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            slot_date TEXT NOT NULL,
            slot_time TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id),
            FOREIGN KEY(department_id) REFERENCES departments(id)
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
        conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            appointment_id INTEGER,
            reminder_type TEXT NOT NULL,
            message TEXT NOT NULL,
            due_at TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            details TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
        """)
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

    def get_patient_dashboard(self, user_id: int, required_documents_for_department: Optional[Any] = None) -> Dict[str, Any]:
        conn = self._get_conn()
        user = conn.execute("SELECT id, role, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
        patient = conn.execute("SELECT id, age, phone FROM patients WHERE user_id = ?", (user_id,)).fetchone()
        patient_id = patient["id"] if patient else None
        appointments = conn.execute(
            "SELECT a.id, a.appointment_date, a.appointment_time, a.status, d.name as doctor_name, dep.name as department_name FROM appointments a JOIN doctors d ON a.doctor_id = d.id JOIN departments dep ON a.department_id = dep.id WHERE a.patient_id = ? ORDER BY a.created_at DESC",
            (patient_id,),
        ).fetchall() if patient_id is not None else []
        documents = conn.execute("SELECT document_name, document_type, status, uploaded_at FROM patient_documents WHERE patient_id = ? ORDER BY uploaded_at DESC", (patient_id,)).fetchall() if patient_id is not None else []
        reminders = conn.execute("SELECT reminder_type, message, due_at, status FROM reminders WHERE patient_id = ? ORDER BY due_at ASC", (patient_id,)).fetchall() if patient_id is not None else []
        workflows = conn.execute("SELECT id, request, status, department, summary, created_at FROM workflow_runs WHERE patient_id = ? ORDER BY created_at DESC LIMIT 5", (patient_id,)).fetchall() if patient_id is not None else []
        doctors = conn.execute(
            "SELECT d.id, d.department_id, d.name, d.specialty, d.availability, d.active, dep.name as department_name FROM doctors d JOIN departments dep ON d.department_id = dep.id WHERE d.active = 1 ORDER BY d.name"
        ).fetchall()
        available_slots = conn.execute(
            "SELECT s.id, d.name as doctor_name, dep.name as department_name, s.slot_date, s.slot_time, s.status FROM appointment_slots s JOIN doctors d ON s.doctor_id = d.id JOIN departments dep ON d.department_id = dep.id WHERE s.status = 'available' ORDER BY s.slot_date, s.slot_time LIMIT 12"
        ).fetchall()
        departments = conn.execute("SELECT id, name, description FROM departments ORDER BY name").fetchall()
        conn.close()

        current_department = appointments[0]["department_name"] if appointments else "General Medicine"
        required_docs = required_documents_for_department(current_department) if required_documents_for_department is not None else []
        existing_docs = {row["document_type"]: row for row in documents}
        required_documents = []
        for doc_type in required_docs:
            doc_info = existing_docs.get(doc_type)
            required_documents.append({
                "document_type": doc_type,
                "status": doc_info["status"] if doc_info is not None else "missing",
                "uploaded_at": doc_info["uploaded_at"] if doc_info is not None else None,
                "document_name": doc_info["document_name"] if doc_info is not None else None,
            })
        return {
            "user": {"id": user["id"], "role": user["role"], "name": user["name"], "email": user["email"]} if user is not None else None,
            "patient": {"id": patient["id"], "age": patient["age"], "phone": patient["phone"]} if patient else None,
            "appointments": [dict(row) for row in appointments],
            "documents": [dict(row) for row in documents],
            "reminders": [dict(row) for row in reminders],
            "workflows": [dict(row) for row in workflows],
            "available_doctors": [dict(row) for row in doctors],
            "available_slots": [dict(row) for row in available_slots],
            "required_documents": required_documents,
            "departments": [dict(row) for row in departments],
        }

    def get_patient_by_id(self, patient_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        patient = conn.execute("SELECT id, user_id, age, phone FROM patients WHERE id = ?", (patient_id,)).fetchone()
        conn.close()
        if patient is None:
            return None
        return dict(patient)

    def get_patient_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        patient = conn.execute("SELECT id, user_id, age, phone FROM patients WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        if patient is None:
            return None
        return dict(patient)

    def get_all_patients(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT p.id, u.name as patient_name, u.email, p.age, p.phone FROM patients p JOIN users u ON p.user_id = u.id ORDER BY p.id DESC"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_requests(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT id, patient_id, patient_name, request, status, department, created_at FROM workflow_runs ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_documents(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT pd.id, u.name as patient_name, pd.document_name, pd.document_type, pd.status, pd.uploaded_at FROM patient_documents pd JOIN patients p ON pd.patient_id = p.id JOIN users u ON p.user_id = u.id ORDER BY pd.uploaded_at DESC"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_patient_document(self, patient_id: int, file, document_name: Optional[str] = None, classify_document: Optional[Any] = None, log_audit: Optional[Any] = None) -> Dict[str, Any]:
        conn = self._get_conn()
        file_name = document_name or getattr(file, 'filename', 'uploaded_document')
        document_type = classify_document(file_name) if classify_document is not None else "misc_document"
        existing = conn.execute("SELECT document_type FROM patient_documents WHERE patient_id = ? AND document_type = ?", (patient_id, document_type)).fetchone()
        if existing is not None:
            conn.close()
            return {"status": "duplicate", "document_type": document_type}
        safe_name = f"{uuid.uuid4()}_{Path(file_name).name}"
        file_path = os.path.join(self.upload_dir, safe_name)
        with open(file_path, 'wb') as handle:
            handle.write(file.read())
        conn.execute(
            "INSERT INTO patient_documents (patient_id, document_name, document_type, status, file_path, uploaded_at) VALUES (?, ?, ?, ?, ?, ?)",
            (patient_id, file_name, document_type, "uploaded", file_path, self._now()),
        )
        conn.commit()
        conn.close()
        if log_audit is not None:
            log_audit("patient_document", patient_id, "uploaded", f"Uploaded {document_type}")
        return {"status": "uploaded", "document_type": document_type}

    def get_doctors(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT d.id, d.department_id, d.name, d.specialty, d.availability, d.active, dep.name as department_name FROM doctors d JOIN departments dep ON d.department_id = dep.id ORDER BY d.name"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_departments(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute("SELECT id, name, description FROM departments ORDER BY name").fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        conn = self._get_conn()
        workflow = conn.execute(
            "SELECT id, patient_id, patient_name, request, status, department, steps, summary, created_at FROM workflow_runs WHERE id = ?",
            (workflow_id,),
        ).fetchone()
        conn.close()
        if workflow is None:
            raise KeyError(workflow_id)
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
