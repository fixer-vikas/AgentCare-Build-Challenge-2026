from __future__ import annotations

from typing import Optional

from repositories.appointment_repository import AppointmentRepository


class ReminderTool:
    def __init__(self, db_path: Optional[str] = None):
        self.appointment_repo = AppointmentRepository(db_path)

    def create_reminder(self, patient_id: int, appointment_id: int, message: str, due_at: Optional[str] = None) -> None:
        due = due_at or "2099-01-01"
        self.appointment_repo.create_reminder(patient_id, appointment_id, "follow_up", message, due)
