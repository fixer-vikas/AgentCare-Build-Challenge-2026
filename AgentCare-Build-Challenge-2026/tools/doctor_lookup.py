from __future__ import annotations

from typing import Optional

from repositories.appointment_repository import AppointmentRepository


class DoctorLookupTool:
    def __init__(self, db_path: Optional[str] = None):
        self.appointment_repo = AppointmentRepository(db_path)

    def get_doctor_for_department(self, department_name: str) -> Optional[dict]:
        department_id = self.appointment_repo.get_department_id(department_name)
        if department_id is None:
            return None
        return self.appointment_repo.get_doctor_for_department(department_id)
