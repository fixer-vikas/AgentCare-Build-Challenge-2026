from __future__ import annotations

from typing import Optional

from repositories.audit_repository import AuditRepository


class AuditTool:
    def __init__(self, db_path: Optional[str] = None):
        self.audit_repo = AuditRepository(db_path)

    def log_audit(self, entity_type: str, entity_id: int, action: str, details: str) -> None:
        self.audit_repo.log_audit(entity_type, entity_id, action, details)

    def get_audit_events(self, limit: int = 100):
        return self.audit_repo.get_audit_events(limit)
