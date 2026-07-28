import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class AppointmentRepository:
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
        conn.commit()
        return conn

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def get_all_appointments(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT a.id, u.name as patient_name, dep.name as department, d.name as doctor_name, a.appointment_date, a.appointment_time, a.status FROM appointments a JOIN patients p ON a.patient_id = p.id JOIN users u ON p.user_id = u.id JOIN doctors d ON a.doctor_id = d.id JOIN departments dep ON a.department_id = dep.id ORDER BY a.appointment_date, a.appointment_time"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_doctor_schedule(self, doctor_id: int) -> Dict[str, Any]:
        conn = self._get_conn()
        doctor = conn.execute(
            "SELECT d.id, d.name, d.specialty, d.availability, d.active, dep.name as department_name FROM doctors d JOIN departments dep ON d.department_id = dep.id WHERE d.id = ?",
            (doctor_id,),
        ).fetchone()
        if doctor is None:
            conn.close()
            raise KeyError(doctor_id)
        slots = conn.execute(
            "SELECT id, slot_date, slot_time, status FROM appointment_slots WHERE doctor_id = ? ORDER BY slot_date, slot_time",
            (doctor_id,),
        ).fetchall()
        appointments = conn.execute(
            "SELECT a.id, u.name as patient_name, a.appointment_date, a.appointment_time, a.status, dep.name as department_name FROM appointments a JOIN patients p ON a.patient_id = p.id JOIN users u ON p.user_id = u.id JOIN departments dep ON a.department_id = dep.id WHERE a.doctor_id = ? ORDER BY a.appointment_date, a.appointment_time",
            (doctor_id,),
        ).fetchall()
        conn.close()
        return {
            "doctor": dict(doctor),
            "slots": [dict(row) for row in slots],
            "appointments": [dict(row) for row in appointments],
        }

    def get_department_schedule(self, department_id: int) -> Dict[str, Any]:
        conn = self._get_conn()
        department = conn.execute("SELECT id, name, description FROM departments WHERE id = ?", (department_id,)).fetchone()
        if department is None:
            conn.close()
            raise KeyError(department_id)
        doctors = conn.execute(
            "SELECT id, name, specialty, availability, active FROM doctors WHERE department_id = ? ORDER BY name",
            (department_id,),
        ).fetchall()
        appointments = conn.execute(
            "SELECT a.id, u.name as patient_name, d.name as doctor_name, a.appointment_date, a.appointment_time, a.status FROM appointments a JOIN doctors d ON a.doctor_id = d.id JOIN patients p ON a.patient_id = p.id JOIN users u ON p.user_id = u.id WHERE a.department_id = ? ORDER BY a.appointment_date, a.appointment_time",
            (department_id,),
        ).fetchall()
        conn.close()
        return {
            "department": dict(department),
            "doctors": [dict(row) for row in doctors],
            "appointments": [dict(row) for row in appointments],
        }

    def add_doctor(self, department_id: int, name: str, specialty: str, availability: str, active: int = 1) -> Dict[str, Any]:
        conn = self._get_conn()
        department = conn.execute("SELECT id FROM departments WHERE id = ?", (department_id,)).fetchone()
        if department is None:
            conn.close()
            raise ValueError("Department not found")
        doctor_id = conn.execute(
            "INSERT INTO doctors (department_id, name, specialty, availability, active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (department_id, name, specialty, availability, active, self._now()),
        ).lastrowid
        conn.commit()
        doctor = conn.execute(
            "SELECT d.id, d.name, d.specialty, d.availability, d.active, dep.name as department_name FROM doctors d JOIN departments dep ON d.department_id = dep.id WHERE d.id = ?",
            (doctor_id,),
        ).fetchone()
        conn.close()
        return dict(doctor)

    def update_doctor(self, doctor_id: int, department_id: int, name: str, specialty: str, availability: str, active: int) -> Dict[str, Any]:
        conn = self._get_conn()
        doctor = conn.execute("SELECT id FROM doctors WHERE id = ?", (doctor_id,)).fetchone()
        if doctor is None:
            conn.close()
            raise KeyError(doctor_id)
        conn.execute(
            "UPDATE doctors SET department_id = ?, name = ?, specialty = ?, availability = ?, active = ? WHERE id = ?",
            (department_id, name, specialty, availability, active, doctor_id),
        )
        conn.commit()
        updated = conn.execute(
            "SELECT d.id, d.name, d.specialty, d.availability, d.active, dep.name as department_name FROM doctors d JOIN departments dep ON d.department_id = dep.id WHERE d.id = ?",
            (doctor_id,),
        ).fetchone()
        conn.close()
        return dict(updated)

    def create_appointment(self, patient_id: int, doctor_id: int, department_id: int, appointment_date: str, appointment_time: str, status: str = "booked") -> int:
        conn = self._get_conn()
        appointment_id = conn.execute(
            "INSERT INTO appointments (patient_id, doctor_id, department_id, appointment_date, appointment_time, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (patient_id, doctor_id, department_id, appointment_date, appointment_time, status, self._now()),
        ).lastrowid
        conn.commit()
        conn.close()
        return appointment_id

    def update_appointment_status(self, appointment_id: int, status: str) -> None:
        conn = self._get_conn()
        conn.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
        conn.commit()
        conn.close()

    def create_slot(self, doctor_id: int, slot_date: str, slot_time: str, status: str = "available") -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO appointment_slots (doctor_id, slot_date, slot_time, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (doctor_id, slot_date, slot_time, status, self._now()),
        )
        conn.commit()
        conn.close()

    def slot_exists(self, doctor_id: int, slot_date: str, slot_time: str) -> bool:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT id FROM appointment_slots WHERE doctor_id = ? AND slot_date = ? AND slot_time = ?",
            (doctor_id, slot_date, slot_time),
        ).fetchone()
        conn.close()
        return row is not None

    def mark_slot_booked(self, doctor_id: int, slot_date: str, slot_time: str) -> None:
        conn = self._get_conn()
        conn.execute("UPDATE appointment_slots SET status = 'booked' WHERE doctor_id = ? AND slot_date = ? AND slot_time = ?", (doctor_id, slot_date, slot_time))
        conn.commit()
        conn.close()

    def get_last_patient_appointment(self, patient_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        row = conn.execute("SELECT id FROM appointments WHERE patient_id = ? AND status != 'cancelled' ORDER BY created_at DESC LIMIT 1", (patient_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return dict(row)

    def create_reminder(self, patient_id: int, appointment_id: Optional[int], reminder_type: str, message: str, due_at: str, status: str = "pending") -> int:
        conn = self._get_conn()
        reminder_id = conn.execute(
            "INSERT INTO reminders (patient_id, appointment_id, reminder_type, message, due_at, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (patient_id, appointment_id, reminder_type, message, due_at, status, self._now()),
        ).lastrowid
        conn.commit()
        conn.close()
        return reminder_id

    def create_escalation(self, patient_id: int, reason: str, details: str = "", status: str = "open") -> int:
        conn = self._get_conn()
        escal_id = conn.execute(
            "INSERT INTO escalations (patient_id, reason, details, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (patient_id, reason, details, status, self._now()),
        ).lastrowid
        conn.commit()
        conn.close()
        return escal_id

    def get_department_id(self, department_name: str) -> Optional[int]:
        conn = self._get_conn()
        row = conn.execute("SELECT id FROM departments WHERE name = ?", (department_name,)).fetchone()
        conn.close()
        if row is None:
            return None
        return row["id"]

    def get_doctor_for_department(self, department_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        row = conn.execute("SELECT id, name FROM doctors WHERE department_id = ? AND active = 1 LIMIT 1", (department_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return dict(row)
