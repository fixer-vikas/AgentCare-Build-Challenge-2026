from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Optional

from repositories.appointment_repository import AppointmentRepository

from .audit_tool import AuditTool


class AppointmentTool:
    def __init__(self, db_path: Optional[str] = None, audit_tool: Optional[AuditTool] = None):
        self.appointment_repo = AppointmentRepository(db_path)
        self.audit_tool = audit_tool or AuditTool(db_path)

    def infer_appointment(self, request: str) -> tuple[Optional[str], Optional[str]]:
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

    def create_slot_if_missing(self, doctor_id: int, appointment_date: str, appointment_time: str) -> None:
        if not self.appointment_repo.slot_exists(doctor_id, appointment_date, appointment_time):
            self.appointment_repo.create_slot(doctor_id, appointment_date, appointment_time, "available")

    def handle_appointment(self, patient_id: int, department_name: str, request: str, action: str) -> Dict[str, Any]:
        department_id = self.appointment_repo.get_department_id(department_name)
        if department_id is None:
            return {"status": "not_requested", "reason": "Department missing"}
        doctor_row = self.appointment_repo.get_doctor_for_department(department_id)
        if doctor_row is None:
            return {"status": "not_requested", "reason": "No active doctor"}
        doctor_id = doctor_row["id"]
        appointment_date, appointment_time = self.infer_appointment(request)
        if appointment_date is None:
            appointment_date = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
        if appointment_time is None:
            appointment_time = "10:00"
        if action == "cancel":
            last_appointment = self.appointment_repo.get_last_patient_appointment(patient_id)
            if last_appointment is None:
                return {"status": "not_requested", "reason": "No appointment to cancel"}
            self.appointment_repo.update_appointment_status(last_appointment["id"], "cancelled")
            self.audit_tool.log_audit("appointment", last_appointment["id"], "cancelled", "Appointment cancelled")
            return {"status": "cancelled", "reason": "Appointment cancelled", "appointment_date": appointment_date, "appointment_time": appointment_time}
        if action == "reschedule":
            last_appointment = self.appointment_repo.get_last_patient_appointment(patient_id)
            if last_appointment is None:
                return {"status": "not_requested", "reason": "No appointment to reschedule"}
            self.appointment_repo.update_appointment_status(last_appointment["id"], "rescheduled")
            appointment_id = self.appointment_repo.create_appointment(patient_id, doctor_id, department_id, appointment_date, appointment_time, "booked")
            self.audit_tool.log_audit("appointment", appointment_id, "rescheduled", f"Rescheduled to {appointment_date} {appointment_time}")
            return {
                "status": "rescheduled",
                "appointment_id": appointment_id,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "doctor_name": doctor_row["name"],
                "summary": f"Rescheduled {department_name} appointment",
            }
        self.create_slot_if_missing(doctor_id, appointment_date, appointment_time)
        appointment_id = self.appointment_repo.create_appointment(patient_id, doctor_id, department_id, appointment_date, appointment_time, "booked")
        self.appointment_repo.mark_slot_booked(doctor_id, appointment_date, appointment_time)
        self.audit_tool.log_audit("appointment", appointment_id, "booked", f"Booked for {appointment_date} {appointment_time}")
        return {
            "status": "booked",
            "appointment_id": appointment_id,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "doctor_name": doctor_row["name"],
            "summary": f"Booked {department_name} appointment",
        }
