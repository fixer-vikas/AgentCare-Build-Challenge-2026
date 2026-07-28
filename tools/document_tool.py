from __future__ import annotations

import os
import shutil
from typing import Any, Dict, List, Optional

from repositories.document_repository import DocumentRepository

from .audit_tool import AuditTool


class DocumentTool:
    def __init__(self, db_path: Optional[str] = None, audit_tool: Optional[AuditTool] = None):
        self.document_repo = DocumentRepository(db_path)
        self.audit_tool = audit_tool or AuditTool(db_path)
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_upload(self, file_storage: Any, patient_id: int, document_type: str) -> Dict[str, Any]:
        filename = file_storage.filename or "upload"
        safe_name = os.path.basename(filename)
        target_path = os.path.join(self.upload_dir, safe_name)
        file_storage.save(target_path)
        result = self.document_repo.add_patient_document(patient_id, safe_name, document_type, file_obj=file_storage)
        document_id = result.get("document_id")
        if document_id is None:
            document_id = 0
        self.audit_tool.log_audit("document", document_id, "uploaded", f"Uploaded {safe_name}")
        return {"document_id": document_id, "file_name": safe_name, "path": target_path}

    def delete_document(self, document_id: int) -> None:
        document = self.document_repo.get_document_by_id(document_id)
        if document is None:
            return
        file_path = os.path.join(self.upload_dir, document["file_name"])
        if os.path.exists(file_path):
            os.remove(file_path)
        self.document_repo.delete_document(document_id)
        self.audit_tool.log_audit("document", document_id, "deleted", f"Deleted {document['file_name']}")

    def list_documents(self, patient_id: int) -> List[Dict[str, Any]]:
        return self.document_repo.get_documents_for_patient(patient_id)
