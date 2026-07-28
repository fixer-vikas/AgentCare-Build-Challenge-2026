from typing import Any, Dict, List, Optional

from app.agentcare import AgentCareService


class AppointmentService:
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

    def get_appointments_response(self, session):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        return self.get_all_appointments(), 200

    def handle_doctors_request(self, method, session, payload):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        user = self.service.get_user(session["user_id"])
        if user is None:
            return {"ok": False, "error": "User not found"}, 404
        if method == "GET":
            return self.get_all_appointments(), 200
        if user["role"] != "staff":
            return {"ok": False, "error": "Only staff can manage doctors"}, 403
        try:
            doctor = self.add_doctor(
                payload.get("department_id"),
                payload.get("name", ""),
                payload.get("specialty", ""),
                payload.get("availability", ""),
                1 if payload.get("active", True) else 0,
            )
            return {"ok": True, "doctor": doctor}, 200
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}, 400

    def update_doctor_response(self, session, doctor_id, payload):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        user = self.service.get_user(session["user_id"])
        if user is None:
            return {"ok": False, "error": "User not found"}, 404
        if user["role"] != "staff":
            return {"ok": False, "error": "Only staff can update doctors"}, 403
        try:
            doctor = self.update_doctor(
                doctor_id,
                payload.get("department_id"),
                payload.get("name", ""),
                payload.get("specialty", ""),
                payload.get("availability", ""),
                1 if payload.get("active", True) else 0,
            )
            return {"ok": True, "doctor": doctor}, 200
        except KeyError:
            return {"ok": False, "error": "Doctor not found"}, 404
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}, 400

    def get_doctor_schedule_response(self, session, doctor_id):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        try:
            return self.get_doctor_schedule(doctor_id), 200
        except KeyError:
            return {"ok": False, "error": "Doctor not found"}, 404

    def get_department_schedule_response(self, session, department_id):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        try:
            return self.get_department_schedule(department_id), 200
        except KeyError:
            return {"ok": False, "error": "Department not found"}, 404

    def get_escalation_queue_response(self, session):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        return self.get_escalation_queue(), 200

    def update_workflow_status_response(self, session, workflow_id, payload):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        user = self.service.get_user(session["user_id"])
        if user is None or user["role"] != "staff":
            return {"ok": False, "error": "Only staff can take workflow actions"}, 403
        action = payload.get("action", "").lower()
        comment = payload.get("comment")
        try:
            result = self.update_workflow_status(workflow_id, action, comment, session["user_id"])
            return {"ok": True, "result": result}, 200
        except KeyError:
            return {"ok": False, "error": "Workflow not found"}, 404
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}, 400

    def staff_ai_request_response(self, session, payload):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        user = self.service.get_user(session["user_id"])
        if user is None or user["role"] != "staff":
            return {"ok": False, "error": "Only staff can use AI requests"}, 403
        patient_id = payload.get("patient_id")
        request_text = payload.get("request", "").strip()
        if not patient_id or not request_text:
            return {"ok": False, "error": "patient_id and request are required"}, 400
        try:
            result = self.handle_staff_ai_request(request_text, int(patient_id), session["user_id"])
            return {"ok": True, "result": result}, 200
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}, 400

    def system_reset_response(self, session, payload):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        user = self.service.get_user(session["user_id"])
        if user is None or user["role"] != "staff":
            return {"ok": False, "error": "Only staff can reset the system"}, 403
        password = payload.get("password", "")
        try:
            result = self.reset_system(session["user_id"], password)
            return {"ok": True, "result": result}, 200
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}, 401

    def get_escalations_response(self, session):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        return self.get_all_escalations(), 200
