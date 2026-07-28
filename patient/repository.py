from typing import Any, Dict, List, Optional

from app.agentcare import AgentCareService


class PatientRepository:
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
