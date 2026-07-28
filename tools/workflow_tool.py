from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.workflow_repository import WorkflowRepository

from .audit_tool import AuditTool


class WorkflowTool:
    def __init__(self, db_path: Optional[str] = None, audit_tool: Optional[AuditTool] = None):
        self.workflow_repo = WorkflowRepository(db_path)
        self.audit_tool = audit_tool or AuditTool(db_path)

    def persist_workflow(self, workflow_id: str, patient_id: int, patient_name: str, request: str, department: str, steps: List[Dict[str, Any]], summary: Optional[str] = None) -> None:
        self.workflow_repo.persist_workflow(workflow_id, patient_id, patient_name, request, department, steps, summary)
        self.audit_tool.log_audit("workflow", patient_id, "persisted", f"Workflow {workflow_id} persisted")

    def update_workflow_status(self, workflow_id: str, status: str) -> None:
        self.workflow_repo.update_workflow_status(workflow_id, status)
        self.audit_tool.log_audit("workflow", 0, "updated", f"Workflow {workflow_id} -> {status}")

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.workflow_repo.get_workflow(workflow_id)

    def get_workflow_for_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        return self.workflow_repo.get_workflow_for_patient(patient_id)
