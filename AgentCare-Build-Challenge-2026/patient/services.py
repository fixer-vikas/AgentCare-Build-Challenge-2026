from typing import Any, Dict, List, Optional

from app.agentcare import AgentCareService


class PatientService:
    def __init__(self, service=None):
        self.service = service or AgentCareService()

    def get_patient_dashboard(self, user_id: int) -> Dict[str, Any]:
        return self.service.get_patient_dashboard(user_id)

    def get_all_patients(self) -> List[Dict[str, Any]]:
        return self.service.get_all_patients()

    def get_all_requests(self) -> List[Dict[str, Any]]:
        return self.service.get_all_requests()

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return self.service.get_all_documents()

    def add_patient_document(self, patient_id: int, file, document_name: Optional[str] = None) -> Dict[str, Any]:
        return self.service.add_patient_document(patient_id, file, document_name)

    def get_doctors(self) -> List[Dict[str, Any]]:
        return self.service.get_doctors()

    def get_departments(self) -> List[Dict[str, Any]]:
        return self.service.get_departments()

    def patient_exists(self, email: str) -> bool:
        return self.service.patient_exists(email)

    def handle_request(self, request: str, patient_name: str, patient_email: Optional[str] = None, patient_age: Optional[str] = None, patient_phone: Optional[str] = None, uploaded_documents: Optional[List[Dict[str, Any]]] = None, patient_id: Optional[int] = None) -> Dict[str, Any]:
        return self.service.handle_request(request, patient_name, patient_email, patient_age, patient_phone, uploaded_documents, patient_id)

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        return self.service.get_workflow(workflow_id)

    def create_request(self, payload, session):
        request_text = payload.get("request", "")
        patient_name = payload.get("patient_name", "Unknown Patient")
        result = self.handle_request(
            request_text,
            patient_name,
            payload.get("patient_email"),
            payload.get("patient_age"),
            payload.get("patient_phone"),
            payload.get("uploaded_documents"),
            payload.get("patient_id"),
        )
        return result, 200

    def create_authenticated_request(self, payload, session):
        user_id = session.get("user_id")
        if not user_id:
            return {"ok": False, "error": "Not authenticated"}, 401
        user = self.service.get_user(user_id)
        if user is None:
            return {"ok": False, "error": "User not found"}, 404
        request_text = payload.get("request", "")
        if user["role"] == "patient":
            profile = self.get_patient_dashboard(user_id)["patient"]
            patient_name = user["name"]
            result = self.handle_request(
                request_text,
                patient_name,
                user["email"],
                profile.get("age"),
                profile.get("phone"),
                payload.get("uploaded_documents"),
                profile.get("id"),
            )
        else:
            patient_name = payload.get("patient_name", "Unknown Patient")
            result = self.handle_request(
                request_text,
                patient_name,
                payload.get("patient_email"),
                payload.get("patient_age"),
                payload.get("patient_phone"),
                payload.get("uploaded_documents"),
                payload.get("patient_id"),
            )
        return result, 200

    def list_requests(self, session):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        return self.get_all_requests(), 200

    def list_patients(self, session):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        return self.get_all_patients(), 200

    def list_documents(self, session):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        return self.get_all_documents(), 200

    def patient_exists_response(self, email):
        return {"ok": True, "exists": self.patient_exists(email)}, 200

    def upload_document(self, session, file, document_name):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        user_id = session["user_id"]
        user = self.service.get_user(user_id)
        if user is None:
            return {"ok": False, "error": "User not found"}, 404
        if user["role"] != "patient":
            return {"ok": False, "error": "Only patients can upload documents"}, 403
        dashboard = self.get_patient_dashboard(user_id)
        patient_id = dashboard["patient"]["id"]
        if not file:
            return {"ok": False, "error": "File is required"}, 400
        result = self.add_patient_document(patient_id, file, document_name)
        return result, 200

    def get_workflow_response(self, workflow_id):
        return self.get_workflow(workflow_id), 200
