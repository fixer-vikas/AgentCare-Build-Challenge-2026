from __future__ import annotations

from typing import Optional

from repositories.appointment_repository import AppointmentRepository


class EscalationTool:
    def __init__(self, db_path: Optional[str] = None):
        self.appointment_repo = AppointmentRepository(db_path)

    def escalate(self, patient_id: int, reason: str, details: str = "") -> None:
        self.appointment_repo.create_escalation(patient_id, reason, details)
