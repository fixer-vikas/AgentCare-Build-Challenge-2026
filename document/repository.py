from typing import Any, Dict, List, Optional

from app.agentcare import AgentCareService


class DocumentRepository:
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
