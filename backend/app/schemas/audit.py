from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor_id: UUID | None
    action: str
    entity_type: str
    entity_id: str
    details: dict
    created_at: datetime


class AuditLogListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[AuditLogRead]
