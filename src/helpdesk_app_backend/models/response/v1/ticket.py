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
    supporter: str
    created_at: datetime
