from typing import Any, Dict, List, Optional

from app.agentcare import AgentCareService


class DocumentService:
    def __init__(self, service=None):
        self.service = service or AgentCareService()

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return self.service.get_all_documents()

    def add_patient_document(self, patient_id: int, file, document_name: Optional[str] = None) -> Dict[str, Any]:
        return self.service.add_patient_document(patient_id, file, document_name)

    def required_documents_for_department(self, department_name: str) -> List[str]:
        return self.service._required_documents_for_department(department_name)

    def infer_documents(self, request: str) -> List[str]:
        return self.service._infer_documents(request)

    def classify_document(self, file_name: str) -> str:
        return self.service._classify_document(file_name)

    def get_documents_response(self, session):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        return self.get_all_documents(), 200

    def upload_document_response(self, session, file, document_name):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        user_id = session["user_id"]
        user = self.service.get_user(user_id)
        if user is None:
            return {"ok": False, "error": "User not found"}, 404
        if user["role"] != "patient":
            return {"ok": False, "error": "Only patients can upload documents"}, 403
        dashboard = self.service.get_patient_dashboard(user_id)
        patient_id = dashboard["patient"]["id"]
        if not file:
            return {"ok": False, "error": "File is required"}, 400
        result = self.add_patient_document(patient_id, file, document_name)
        return result, 200
