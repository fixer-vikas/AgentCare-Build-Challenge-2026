from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from werkzeug.security import check_password_hash, generate_password_hash

from repositories.appointment_repository import AppointmentRepository
from repositories.audit_repository import AuditRepository
from repositories.document_repository import DocumentRepository
from repositories.patient_repository import PatientRepository
from repositories.user_repository import UserRepository
from repositories.workflow_repository import WorkflowRepository
from tools.appointment_tool import AppointmentTool
from tools.audit_tool import AuditTool
from tools.department_lookup import DepartmentLookupTool
from tools.document_tool import DocumentTool
from tools.doctor_lookup import DoctorLookupTool
from tools.escalation_tool import EscalationTool
from tools.patient_lookup import PatientLookupTool
from tools.reminder_tool import ReminderTool
from tools.workflow_tool import WorkflowTool

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - dependency may be missing in some environments
    OpenAI = None


class AgentCareService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "agentcare.sqlite3")
        self.upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
        self.user_repo = UserRepository(self.db_path)
        self.patient_repo = PatientRepository(self.db_path)
        self.appointment_repo = AppointmentRepository(self.db_path)
        self.document_repo = DocumentRepository(self.db_path)
        self.workflow_repo = WorkflowRepository(self.db_path)
        self.audit_repo = AuditRepository(self.db_path)
        self.audit_tool = AuditTool(self.db_path)
        self.patient_lookup_tool = PatientLookupTool(self.db_path, self.audit_tool)
        self.department_lookup_tool = DepartmentLookupTool()
        self.doctor_lookup_tool = DoctorLookupTool(self.db_path)
        self.appointment_tool = AppointmentTool(self.db_path, self.audit_tool)
        self.document_tool = DocumentTool(self.db_path, self.audit_tool)
        self.workflow_tool = WorkflowTool(self.db_path, self.audit_tool)
        self.reminder_tool = ReminderTool(self.db_path)
        self.escalation_tool = EscalationTool(self.db_path)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
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
        conn.commit()
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
        self._migrate_schema(conn)
        conn.close()
        self._seed_reference_data()

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        # Migrate old patients schema
        try:
            patient_columns = [row[1] for row in conn.execute("PRAGMA table_info(patients)").fetchall()]
        except sqlite3.OperationalError:
            patient_columns = []
        if patient_columns and "user_id" not in patient_columns:
            conn.execute("DROP TABLE IF EXISTS patients_old")
            conn.execute("ALTER TABLE patients RENAME TO patients_old")
            conn.execute("""
            CREATE TABLE patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                age TEXT,
                phone TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
            try:
                old_rows = conn.execute("SELECT id, name, created_at FROM patients_old").fetchall()
            except sqlite3.OperationalError:
                old_rows = []
            for row in old_rows:
                name = row[1] or f"imported_patient_{row[0]}"
                email = f"{name.lower().replace(' ', '')}@agentcare.local"
                password_hash = generate_password_hash("changeme")
                created_at = row[2] or self._now()
                user_id = conn.execute(
                    "INSERT INTO users (role, name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                    ("patient", name, email, password_hash, created_at),
                ).lastrowid
                conn.execute(
                    "INSERT INTO patients (user_id, age, phone, created_at) VALUES (?, ?, ?, ?)",
                    (user_id, None, None, created_at),
                )
            conn.commit()

        # Migrate old appointments schema if needed
        try:
            appointment_columns = [row[1] for row in conn.execute("PRAGMA table_info(appointments)").fetchall()]
        except sqlite3.OperationalError:
            appointment_columns = []
        if appointment_columns and ("doctor_id" not in appointment_columns or "department_id" not in appointment_columns):
            conn.execute("DROP TABLE IF EXISTS appointments_old")
            conn.execute("ALTER TABLE appointments RENAME TO appointments_old")
            conn.execute("""
            CREATE TABLE appointments (
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
            try:
                old_rows = conn.execute("SELECT id, patient_id, department, appointment_date, appointment_time, status, created_at FROM appointments_old").fetchall()
            except sqlite3.OperationalError:
                old_rows = []
            department_lookup = {
                row[1].lower(): row[0] for row in conn.execute("SELECT id, name FROM departments").fetchall()
            }
            for row in old_rows:
                department_name = (row[2] or "General Medicine").strip()
                department_id = department_lookup.get(department_name.lower(), department_lookup.get("general medicine"))
                doctor_row = conn.execute("SELECT id FROM doctors WHERE department_id = ? AND active = 1 LIMIT 1", (department_id,)).fetchone()
                doctor_id = doctor_row[0] if doctor_row is not None else 1
                conn.execute(
                    "INSERT INTO appointments (patient_id, doctor_id, department_id, appointment_date, appointment_time, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (row[1], doctor_id, department_id, row[3], row[4], row[5], row[6]),
                )
            conn.commit()

    def _seed_reference_data(self) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO users (role, name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            ("staff", "Staff User", "staff@example.com", generate_password_hash("staffpass"), self._now()),
        )
        default_departments = [
            ("Cardiology", "Heart and vascular follow-ups"),
            ("Orthopedics", "Bone, joint and mobility care"),
            ("Neurology", "Neurological follow-ups and referrals"),
            ("ENT", "Ear, nose and throat cases"),
            ("General Medicine", "General administrative coordination"),
        ]
        doctors_by_department = {
            "Cardiology": [
                ("Dr. Alice Heart", "Cardiology", "Mon-Fri, Wed off"),
                ("Dr. Ben Pulse", "Cardiology", "Mon-Fri"),
                ("Dr. Clara Vascular", "Cardiology", "Mon-Thu"),
                ("Dr. Daniel Rhythm", "Cardiology", "Tue-Fri"),
                ("Dr. Eva Artery", "Cardiology", "Mon-Fri, Fri off"),
            ],
            "Orthopedics": [
                ("Dr. Fiona Bones", "Orthopedics", "Mon-Fri"),
                ("Dr. Greg Joint", "Orthopedics", "Mon-Thu"),
                ("Dr. Hannah Spine", "Orthopedics", "Tue-Fri"),
                ("Dr. Ian Ligament", "Orthopedics", "Mon-Fri, Wed off"),
                ("Dr. Jenna Mobility", "Orthopedics", "Mon-Fri"),
            ],
            "Neurology": [
                ("Dr. Kyle Brain", "Neurology", "Mon-Fri"),
                ("Dr. Leah Nerve", "Neurology", "Tue-Thu"),
                ("Dr. Mike Synapse", "Neurology", "Mon-Fri, Fri off"),
                ("Dr. Nora Cortex", "Neurology", "Mon-Thu"),
                ("Dr. Oscar Reflex", "Neurology", "Mon-Fri"),
            ],
            "ENT": [
                ("Dr. Paige Ear", "ENT", "Mon-Fri"),
                ("Dr. Quinn Throat", "ENT", "Mon-Thu"),
                ("Dr. Ravi Nose", "ENT", "Tue-Fri"),
                ("Dr. Sara Voice", "ENT", "Mon-Fri, Wed off"),
                ("Dr. Terry Sinus", "ENT", "Mon-Fri"),
            ],
            "General Medicine": [
                ("Dr. Uma General", "General Medicine", "Mon-Fri"),
                ("Dr. Victor Care", "General Medicine", "Mon-Fri"),
                ("Dr. Wendy Wellness", "General Medicine", "Tue-Thu"),
                ("Dr. Xavier Health", "General Medicine", "Mon-Fri, Fri off"),
                ("Dr. Yara Clinic", "General Medicine", "Mon-Fri"),
            ],
        }
        for name, description in default_departments:
            conn.execute("INSERT OR IGNORE INTO departments (name, description, created_at) VALUES (?, ?, ?)", (name, description, self._now()))
            department_id = conn.execute("SELECT id FROM departments WHERE name = ?", (name,)).fetchone()[0]
            for doctor_name, specialty, availability in doctors_by_department.get(name, []):
                existing = conn.execute(
                    "SELECT id FROM doctors WHERE department_id = ? AND name = ?",
                    (department_id, doctor_name),
                ).fetchone()
                if existing is None:
                    conn.execute(
                        "INSERT INTO doctors (department_id, name, specialty, availability, active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (department_id, doctor_name, specialty, availability, 1, self._now()),
                    )
        self._seed_doctor_slots(conn)
        conn.commit()
        conn.close()

    def _seed_doctor_slots(self, conn: sqlite3.Connection) -> None:
        """Populate `appointment_slots` with a simple repeating schedule for active doctors.

        This is idempotent per-doctor: if a doctor already has any slots, we skip seeding for them.
        """
        # Check if any doctors exist
        doctors = conn.execute("SELECT id FROM doctors WHERE active = 1").fetchall()
        if not doctors:
            return

        # Simple working times for seeded slots
        times = ["09:00", "10:00", "11:00", "14:00", "15:00"]
        days_out = 14
        base = date.today()

        for drow in doctors:
            doc_id = drow[0]
            # If doctor already has slots, skip to avoid duplicates
            existing = conn.execute("SELECT COUNT(*) as c FROM appointment_slots WHERE doctor_id = ?", (doc_id,)).fetchone()["c"]
            if existing and existing > 0:
                continue

            for offset in range(days_out):
                day = base + timedelta(days=offset)
                # skip weekends
                if day.weekday() >= 5:
                    continue
                slot_date = day.isoformat()
                for t in times:
                    conn.execute(
                        "INSERT INTO appointment_slots (doctor_id, slot_date, slot_time, status, created_at) VALUES (?, ?, ?, ?, ?)",
                        (doc_id, slot_date, t, "available", self._now()),
                    )

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def register_user(self, role: str, name: str, email: str, password: str, age: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        result = self.user_repo.register_user(role, name, email, password, age, phone)
        self._log_audit("user", result["id"], "registered", f"{role} registered")
        return result

    def login_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.user_repo.get_user_by_email(email)
        if user is None:
            return None
        if not check_password_hash(user["password_hash"], password):
            return None
        return {"id": user["id"], "role": user["role"], "name": user["name"], "email": user["email"]}

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        user = self.user_repo.get_user(user_id)
        if user is None:
            return None
        return {"id": user["id"], "role": user["role"], "name": user["name"], "email": user["email"]}

    def get_patient_dashboard(self, user_id: int) -> Dict[str, Any]:
        return self.patient_repo.get_patient_dashboard(user_id, self._required_documents_for_department)

    def get_staff_dashboard(self) -> Dict[str, Any]:
        conn = self._get_conn()
        patient_count = conn.execute("SELECT COUNT(*) as c FROM patients").fetchone()["c"]
        pending_requests = conn.execute("SELECT COUNT(*) as c FROM workflow_runs WHERE status != 'completed'").fetchone()["c"]
        escalations = conn.execute("SELECT COUNT(*) as c FROM escalations WHERE status = 'open'").fetchone()["c"]
        upcoming = conn.execute("SELECT COUNT(*) as c FROM appointments WHERE status = 'booked'").fetchone()["c"]
        missing_docs = conn.execute("SELECT COUNT(*) as c FROM patient_documents WHERE status = 'missing'").fetchone()["c"]
        doctor_count = conn.execute("SELECT COUNT(*) as c FROM doctors").fetchone()["c"]
        department_count = conn.execute("SELECT COUNT(*) as c FROM departments").fetchone()["c"]
        workflows = conn.execute("SELECT id, patient_name, status, department, created_at FROM workflow_runs ORDER BY created_at DESC LIMIT 10").fetchall()
        escalations_rows = conn.execute("SELECT e.id, u.name as patient_name, e.reason, e.details, e.status, e.created_at FROM escalations e JOIN patients p ON e.patient_id = p.id JOIN users u ON p.user_id = u.id ORDER BY e.created_at DESC LIMIT 10").fetchall()
        open_requests = conn.execute("SELECT id, patient_name, request, status, department, created_at FROM workflow_runs WHERE status != 'completed' ORDER BY created_at DESC").fetchall()
        conn.close()
        return {
            "patient_count": patient_count,
            "pending_requests": pending_requests,
            "escalations": escalations,
            "upcoming_appointments": upcoming,
            "missing_documents": missing_docs,
            "doctor_count": doctor_count,
            "department_count": department_count,
            "workflows": [dict(row) for row in workflows],
            "escalations_rows": [dict(row) for row in escalations_rows],
            "open_requests": [dict(row) for row in open_requests],
        }

    def get_all_patients(self) -> List[Dict[str, Any]]:
        return self.patient_repo.get_all_patients()

    def get_all_requests(self) -> List[Dict[str, Any]]:
        return self.patient_repo.get_all_requests()

    def get_all_appointments(self) -> List[Dict[str, Any]]:
        return self.appointment_repo.get_all_appointments()

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return self.patient_repo.get_all_documents()

    def get_all_escalations(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT e.id, u.name as patient_name, e.reason, e.details, e.status, e.created_at FROM escalations e JOIN patients p ON e.patient_id = p.id JOIN users u ON p.user_id = u.id ORDER BY e.created_at DESC"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_audit_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.audit_repo.get_audit_events(limit)

    def add_patient_document(self, patient_id: int, file, document_name: Optional[str] = None) -> Dict[str, Any]:
        file_name = document_name or getattr(file, 'filename', 'uploaded_document')
        result = self.document_repo.add_patient_document(patient_id, file_name, self._classify_document(file_name), file_obj=file, log_audit=self._log_audit)
        return result

    def get_doctors(self) -> List[Dict[str, Any]]:
        return self.patient_repo.get_doctors()

    def get_departments(self) -> List[Dict[str, Any]]:
        return self.patient_repo.get_departments()

    def patient_exists(self, email: str) -> bool:
        return self.user_repo.patient_exists(email)

    def get_doctor_schedule(self, doctor_id: int) -> Dict[str, Any]:
        schedule = self.appointment_repo.get_doctor_schedule(doctor_id)
        schedule["holidays"] = self._generate_doctor_holidays(doctor_id)
        return schedule

    def get_department_schedule(self, department_id: int) -> Dict[str, Any]:
        return self.appointment_repo.get_department_schedule(department_id)

    def add_doctor(self, department_id: int, name: str, specialty: str, availability: str, active: int = 1) -> Dict[str, Any]:
        doctor = self.appointment_repo.add_doctor(department_id, name, specialty, availability, active)
        self._log_audit("doctor", doctor["id"], "added", f"Doctor {name} added to department {department_id}")
        return doctor

    def update_doctor(self, doctor_id: int, department_id: int, name: str, specialty: str, availability: str, active: int) -> Dict[str, Any]:
        updated = self.appointment_repo.update_doctor(doctor_id, department_id, name, specialty, availability, active)
        self._log_audit("doctor", doctor_id, "updated", f"Doctor {doctor_id} updated")
        return updated

    def verify_user_password(self, user_id: int, password: str) -> bool:
        conn = self._get_conn()
        row = conn.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        if row is None:
            return False
        return check_password_hash(row["password_hash"], password)

    def update_workflow_status(self, workflow_id: str, action: str, comment: Optional[str], staff_user_id: int) -> Dict[str, Any]:
        allowed_actions = {"open", "approved", "escalated", "rejected"}
        if action not in allowed_actions:
            raise ValueError("Invalid workflow action")
        conn = self._get_conn()
        workflow = conn.execute("SELECT id, patient_id FROM workflow_runs WHERE id = ?", (workflow_id,)).fetchone()
        if workflow is None:
            conn.close()
            raise KeyError(workflow_id)
        conn.execute("UPDATE workflow_runs SET status = ? WHERE id = ?", (action, workflow_id))
        if action == "escalated":
            conn.execute(
                "INSERT INTO escalations (patient_id, reason, details, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (workflow["patient_id"], comment or "Staff escalation", comment or "Escalated by staff", "open", self._now()),
            )
        conn.commit()
        conn.close()
        self._log_audit("workflow", workflow_id, action, comment or f"Request {action}")
        return {"workflow_id": workflow_id, "status": action, "comment": comment}

    def handle_staff_ai_request(self, request_text: str, patient_id: int, staff_user_id: int) -> Dict[str, Any]:
        conn = self._get_conn()
        patient = conn.execute(
            "SELECT p.id, u.name as patient_name, u.email FROM patients p JOIN users u ON p.user_id = u.id WHERE p.id = ?",
            (patient_id,),
        ).fetchone()
        if patient is None:
            conn.close()
            raise ValueError("Patient not found")

        if self._is_clinical_request(request_text):
            conn.close()
            self._log_audit("staff_ai", staff_user_id, "blocked", f"Blocked clinical request for patient {patient_id}: {request_text}")
            return {
                "workflow_id": None,
                "summary": "Blocked: this workflow only supports administrative routing and document coordination.",
                "steps": [{"agent": "safety", "action": "blocked", "details": "Clinical diagnosis or prescription requests are not supported."}],
            }

        lower = request_text.lower()
        steps: List[Dict[str, Any]] = []
        summary_parts: List[str] = []
        if "approve all requests made today" in lower:
            today = date.today().isoformat()
            result = conn.execute("UPDATE workflow_runs SET status = 'approved' WHERE created_at LIKE ? AND status != 'approved'", (today + "%",))
            approved_count = result.rowcount if result is not None else 0
            conn.commit()
            steps.append({"agent": "staff-ai", "action": "approved_today", "details": f"Approved {approved_count} requests created today"})
            summary_parts.append(f"Approved {approved_count} requests")
        if "insurance card" in lower or "collect the insurance card" in lower:
            steps.append({"agent": "staff-ai", "action": "requested_insurance", "details": "Requested insurance card collection"})
            summary_parts.append("Insurance card requested")
        if "follow-up reminder" in lower or "reminder" in lower:
            due_at = (date.today() + timedelta(days=7)).isoformat()
            message = f"Follow-up reminder: {request_text}"
            conn.execute(
                "INSERT INTO reminders (patient_id, appointment_id, reminder_type, message, due_at, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (patient_id, None, "follow_up", message, due_at, "pending", self._now()),
            )
            conn.commit()
            steps.append({"agent": "staff-ai", "action": "created_reminder", "details": message})
            summary_parts.append("Created follow-up reminder")
        if "pediatric" in lower:
            steps.append({"agent": "staff-ai", "action": "routed", "details": "Routed pediatric request to general medicine"})
            summary_parts.append("Routed pediatric request")
        if not steps:
            department_name = self._department_agent(request_text)
            steps.append({"agent": "staff-ai", "action": "requested", "details": f"Staff AI requested: {request_text}"})
            summary_parts.append(f"Routed to {department_name}")

        workflow_id = str(uuid.uuid4())
        conn.close()
        self.workflow_repo.persist_workflow(workflow_id, patient_id, patient["patient_name"], request_text, "General Medicine", steps, "; ".join(summary_parts) if summary_parts else None)
        self._log_audit("staff_ai", staff_user_id, "created", f"Staff AI request for patient {patient_id}: {request_text}")
        return {"workflow_id": workflow_id, "summary": "; ".join(summary_parts), "steps": steps}

    def get_escalation_queue(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT e.id, u.name as patient_name, e.reason, e.details, e.status, e.created_at FROM escalations e JOIN patients p ON e.patient_id = p.id JOIN users u ON p.user_id = u.id WHERE e.status = 'open' ORDER BY e.created_at DESC"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def reset_system(self, staff_user_id: int, password: str) -> Dict[str, Any]:
        if not self.verify_user_password(staff_user_id, password):
            raise ValueError("Invalid password")
        conn = self._get_conn()
        conn.execute("DELETE FROM workflow_runs")
        conn.execute("DELETE FROM appointments")
        conn.execute("DELETE FROM appointment_slots")
        conn.execute("DELETE FROM patient_documents")
        conn.execute("DELETE FROM reminders")
        conn.execute("DELETE FROM escalations")
        conn.execute("DELETE FROM audit_events")
        conn.execute("DELETE FROM patients")
        conn.execute("DELETE FROM users WHERE role = 'patient'")
        conn.commit()
        conn.close()
        self._log_audit("system", staff_user_id, "reset", f"System reset performed by staff {staff_user_id}")
        return {"status": "reset"}

    def _required_documents_for_department(self, department_name: str) -> List[str]:
        return self.department_lookup_tool.required_documents_for_department(department_name)

    def handle_request(self, request: str, patient_name: str, patient_email: Optional[str] = None, patient_age: Optional[str] = None, patient_phone: Optional[str] = None, uploaded_documents: Optional[List[Dict[str, Any]]] = None, patient_id: Optional[int] = None) -> Dict[str, Any]:
        if self._is_medical_safety_block(request):
            return {
                "status": "blocked",
                "workflow_id": None,
                "patient_name": patient_name,
                "department": "None",
                "appointment_status": "not_requested",
                "document_count": 0,
                "follow_up_created": False,
                "safety_reason": "Medical diagnosis, prescription, or dosage recommendations are not allowed in this administrative workflow.",
            }

        profile = self._ensure_patient_profile(patient_name, patient_email, patient_age, patient_phone, patient_id)
        patient_id = profile["patient_id"]
        plan = self._coordinator_agent(request)
        department_name = self._department_agent(request)
        appointment_result = self._appointment_agent(patient_id, department_name, request, plan["action"])
        document_result = self._document_agent(patient_id, request, uploaded_documents or [])
        reminder_result = self._follow_up_agent(patient_id, appointment_result.get("appointment_id"), request)
        escalation_result = self._safety_agent(request, department_name, appointment_result, document_result)

        workflow_id = str(uuid.uuid4())
        steps: List[Dict[str, Any]] = [
            {"agent": "coordinator", "action": "identified intent", "details": plan["action"]},
            {"agent": "department", "action": "routed", "details": department_name},
        ]
        if appointment_result["status"] == "booked":
            steps.append({"agent": "appointment", "action": "booked", "details": f"{appointment_result['appointment_date']} {appointment_result['appointment_time']}"})
        elif appointment_result["status"] == "cancelled":
            steps.append({"agent": "appointment", "action": "cancelled", "details": appointment_result["reason"]})
        elif appointment_result["status"] == "rescheduled":
            steps.append({"agent": "appointment", "action": "rescheduled", "details": f"{appointment_result['appointment_date']} {appointment_result['appointment_time']}"})
        steps.append({"agent": "documents", "action": "classified", "details": ", ".join(document_result["created_documents"]) or "none"})
        if document_result["missing_documents"]:
            steps.append({"agent": "documents", "action": "missing documents", "details": ", ".join(document_result["missing_documents"])})
        if document_result["duplicate_documents"]:
            steps.append({"agent": "documents", "action": "duplicate documents", "details": ", ".join(document_result["duplicate_documents"])})
        if reminder_result:
            steps.append({"agent": "follow_up", "action": "reminder created", "details": reminder_result["message"]})
        if escalation_result:
            steps.append({"agent": "safety", "action": "escalated", "details": escalation_result["reason"]})
        self.workflow_tool.persist_workflow(workflow_id, profile["patient_id"], patient_name, request, department_name, steps, summary=appointment_result.get("summary"))
        self._log_audit("workflow", workflow_id, "processed", json.dumps({"department": department_name, "action": plan["action"]}))
        return {
            "status": "escalated" if escalation_result else "completed",
            "workflow_id": workflow_id,
            "patient_name": patient_name,
            "department": department_name,
            "appointment_status": appointment_result["status"],
            "document_count": len(document_result["created_documents"]),
            "follow_up_created": bool(reminder_result),
            "missing_documents": document_result["missing_documents"],
            "duplicate_documents": document_result["duplicate_documents"],
            "escalation": escalation_result,
        }

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        workflow = self.workflow_repo.get_workflow(workflow_id)
        if workflow is None:
            raise KeyError(workflow_id)
        return workflow

    def _ensure_patient_profile(self, patient_name: str, patient_email: Optional[str], patient_age: Optional[str], patient_phone: Optional[str], patient_id: Optional[int]) -> Dict[str, Any]:
        try:
            result = self.patient_lookup_tool.ensure_patient_profile(patient_name, patient_email, patient_age, patient_phone, patient_id)
        except ValueError:
            raise
        normalized = {"patient_id": result["patient_id"]}
        if "id" in result:
            normalized["id"] = result["id"]
        else:
            normalized["id"] = result["patient_id"]
        return normalized

    def _coordinator_agent(self, request: str) -> Dict[str, Any]:
        lowered = request.lower()
        if any(word in lowered for word in ["reschedule", "rescheduled", "move"]):
            action = "reschedule"
        elif any(word in lowered for word in ["cancel", "cancellation"]):
            action = "cancel"
        elif any(word in lowered for word in ["follow-up", "follow up", "reminder"]):
            action = "follow-up"
        else:
            action = "book"
        return {"action": action, "needs_clarification": any(word in lowered for word in ["uncertain", "unsure", "maybe", "not sure"]) }

    def _department_agent(self, request: str) -> str:
        return self.department_lookup_tool.department_agent(request)

    def _appointment_agent(self, patient_id: int, department_name: str, request: str, action: str) -> Dict[str, Any]:
        return self.appointment_tool.handle_appointment(patient_id, department_name, request, action)

    def _create_slot_if_missing(self, doctor_id: int, appointment_date: str, appointment_time: str) -> None:
        conn = self._get_conn()
        existing = conn.execute("SELECT id FROM appointment_slots WHERE doctor_id = ? AND slot_date = ? AND slot_time = ?", (doctor_id, appointment_date, appointment_time)).fetchone()
        if existing is None:
            conn.execute(
                "INSERT INTO appointment_slots (doctor_id, slot_date, slot_time, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (doctor_id, appointment_date, appointment_time, "available", self._now()),
            )
            conn.commit()
        conn.close()

    def _document_agent(self, patient_id: int, request: str, uploaded_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        conn = self._get_conn()
        required_documents = self._infer_documents(request)
        existing_types = {row["document_type"] for row in conn.execute("SELECT document_type FROM patient_documents WHERE patient_id = ?", (patient_id,)).fetchall()}
        created_documents: List[str] = []
        missing_documents: List[str] = []
        duplicate_documents: List[str] = []
        for item in uploaded_documents:
            file_name = item.get("name") or item.get("document_name") or "uploaded_document"
            document_type = self._classify_document(file_name)
            if document_type in existing_types:
                duplicate_documents.append(document_type)
                continue
            file_path = None
            if item.get("file"):
                safe_name = f"{uuid.uuid4()}_{Path(file_name).name}"
                file_path = os.path.join(self.upload_dir, safe_name)
                with open(file_path, "wb") as handle:
                    handle.write(item["file"].read())
            conn.execute(
                "INSERT INTO patient_documents (patient_id, document_name, document_type, status, file_path, uploaded_at) VALUES (?, ?, ?, ?, ?, ?)",
                (patient_id, file_name, document_type, "uploaded", file_path, self._now()),
            )
            created_documents.append(document_type)
            existing_types.add(document_type)
        for doc_type in required_documents:
            if doc_type in existing_types:
                continue
            if doc_type not in created_documents:
                created_documents.append(doc_type)
            missing_documents.append(doc_type)
            conn.execute(
                "INSERT INTO patient_documents (patient_id, document_name, document_type, status, file_path, uploaded_at) VALUES (?, ?, ?, ?, ?, ?)",
                (patient_id, doc_type.replace("_", " "), doc_type, "missing", None, self._now()),
            )
            existing_types.add(doc_type)
        conn.commit()
        conn.close()
        return {"created_documents": created_documents, "missing_documents": missing_documents, "duplicate_documents": duplicate_documents}

    def _follow_up_agent(self, patient_id: int, appointment_id: Optional[int], request: str) -> Optional[Dict[str, Any]]:
        if "follow-up" not in request.lower() and "reminder" not in request.lower() and appointment_id is None:
            return None
        conn = self._get_conn()
        reminder_type = "follow_up" if "follow-up" in request.lower() or "follow up" in request.lower() else "appointment"
        due_at = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        conn.execute(
            "INSERT INTO reminders (patient_id, appointment_id, reminder_type, message, due_at, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (patient_id, appointment_id, reminder_type, "Reminder created for follow-up", due_at, "pending", self._now()),
        )
        conn.commit()
        conn.close()
        return {"message": "Reminder created for follow-up", "due_at": due_at}

    def _safety_agent(self, request: str, department_name: str, appointment_result: Dict[str, Any], document_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        lowered = request.lower()
        if any(word in lowered for word in ["emergency", "urgent", "immediately", "severe pain", "bleeding"]):
            conn = self._get_conn()
            patient_id = conn.execute("SELECT id FROM patients ORDER BY id DESC LIMIT 1").fetchone()
            if patient_id is not None:
                conn.execute(
                    "INSERT INTO escalations (patient_id, reason, details, status, created_at) VALUES (?, ?, ?, ?, ?)",
                    (patient_id["id"], "Emergency request", "Escalated to human staff for review", "open", self._now()),
                )
                conn.commit()
            conn.close()
            return {"reason": "Emergency request escalated to staff", "department": department_name}
        return None

    def _infer_appointment(self, request: str) -> tuple[Optional[str], Optional[str]]:
        if "2026-" in request:
            date_part = None
            for fragment in request.split():
                if len(fragment) == 10 and fragment.count("-") == 2:
                    date_part = fragment
                    break
            if date_part:
                try:
                    date.fromisoformat(date_part)
                except ValueError:
                    date_part = None
            if date_part:
                time_part = None
                for fragment in request.split():
                    if ":" in fragment and len(fragment) <= 5:
                        time_part = fragment
                        break
                return date_part, time_part or "09:00"
        if "next week" in request.lower():
            return (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"), "10:00"
        if "next monday" in request.lower():
            today = date.today()
            weekday = today.weekday()
            delta = 7 - weekday + 0
            return (today + timedelta(days=delta)).strftime("%Y-%m-%d"), "10:00"
        return None, None

    def _is_medical_safety_block(self, request: str) -> bool:
        return self._is_clinical_request(request)

    def _is_clinical_request(self, request: str) -> bool:
        lower = request.lower()
        disallowed_terms = [
            "diagnose",
            "diagnosis",
            "prescribe",
            "prescription",
            "medicine",
            "medication",
            "dosage",
            "treatment",
            "treat",
            "insulin",
            "diabetes",
            "cancer",
            "disease",
        ]
        return any(term in lower for term in disallowed_terms)

    def _infer_documents(self, request: str) -> List[str]:
        lower = request.lower()
        docs: List[str] = []
        if "insurance" in lower or "insurance card" in lower:
            docs.append("insurance_card")
        if "id" in lower or "identification" in lower or "passport" in lower:
            docs.append("id_proof")
        if "medical history" in lower or "history" in lower:
            docs.append("medical_history")
        if "report" in lower or "test result" in lower or "blood report" in lower:
            docs.append("blood_report")
        if "ecg" in lower:
            docs.append("ecg")
        if "document" in lower or "documents" in lower:
            docs.append("misc_document")
        return docs

    def _classify_document(self, file_name: str) -> str:
        lowered = file_name.lower()
        if "ecg" in lowered or "electrocardiogram" in lowered:
            return "ecg"
        if "blood" in lowered or "report" in lowered:
            return "blood_report"
        if "insurance" in lowered:
            return "insurance_card"
        if "id" in lowered or "passport" in lowered:
            return "id_proof"
        return "misc_document"

    def _persist_workflow(self, workflow_id: str, patient_id: int, patient_name: str, request: str, department: str, steps: List[Dict[str, Any]], summary: Optional[str] = None) -> None:
        self.workflow_repo.persist_workflow(workflow_id, patient_id, patient_name, request, department, steps, summary)

    def _generate_doctor_holidays(self, doctor_id: int) -> List[Dict[str, str]]:
        base = date.today()
        holidays: List[Dict[str, str]] = []
        if doctor_id % 2 == 0:
            holidays.append({"date": (base + timedelta(days=3)).isoformat(), "title": "Training day"})
        if doctor_id % 3 == 0:
            holidays.append({"date": (base + timedelta(days=6)).isoformat(), "title": "Hospital closed"})
        return holidays

    def _log_audit(self, entity_type: str, entity_id: int, action: str, details: str) -> None:
        self.audit_repo.log_audit(entity_type, entity_id, action, details)
