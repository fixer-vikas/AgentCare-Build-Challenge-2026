from typing import Any, Dict, List, Optional

from app.agentcare import AgentCareService


class AppointmentRepository:
    def __init__(self, service=None):
        self.service = service or AgentCareService()

    def get_all_appointments(self) -> List[Dict[str, Any]]:
        return self.service.get_all_appointments()

    def get_doctor_schedule(self, doctor_id: int) -> Dict[str, Any]:
        return self.service.get_doctor_schedule(doctor_id)

    def get_department_schedule(self, department_id: int) -> Dict[str, Any]:
        return self.service.get_department_schedule(department_id)

    def add_doctor(self, department_id: int, name: str, specialty: str, availability: str, active: int = 1) -> Dict[str, Any]:
        return self.service.add_doctor(department_id, name, specialty, availability, active)

    def update_doctor(self, doctor_id: int, department_id: int, name: str, specialty: str, availability: str, active: int) -> Dict[str, Any]:
        return self.service.update_doctor(doctor_id, department_id, name, specialty, availability, active)

    def update_workflow_status(self, workflow_id: str, action: str, comment: Optional[str], staff_user_id: int) -> Dict[str, Any]:
        return self.service.update_workflow_status(workflow_id, action, comment, staff_user_id)

    def handle_staff_ai_request(self, request_text: str, patient_id: int, staff_user_id: int) -> Dict[str, Any]:
        return self.service.handle_staff_ai_request(request_text, patient_id, staff_user_id)

    def get_escalation_queue(self) -> List[Dict[str, Any]]:
        return self.service.get_escalation_queue()

    def reset_system(self, staff_user_id: int, password: str) -> Dict[str, Any]:
        return self.service.reset_system(staff_user_id, password)

    def get_all_escalations(self) -> List[Dict[str, Any]]:
        return self.service.get_all_escalations()

    def get_audit_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.service.get_audit_events(limit)
