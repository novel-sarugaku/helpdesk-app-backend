from datetime import datetime

from pydantic import BaseModel

from helpdesk_app_backend.models.enum.ticket import TicketStatusType


# チケット取得（GET）
class GetTicketResponseItem(BaseModel):
    id: int
    title: str
    is_public: bool
    status: TicketStatusType
    staff: str
    supporter: str | None
    created_at: datetime


# チケット追加（POST）
class CreateTicketResponse(BaseModel):
    id: int
    title: str
    is_public: bool
    status: TicketStatusType
    description: str
    staff: int
    created_at: datetime
