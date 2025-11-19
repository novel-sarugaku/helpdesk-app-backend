from pydantic import BaseModel

from helpdesk_app_backend.models.enum.ticket import TicketStatusType


# チケット追加（POST）
class CreateTicketRequest(BaseModel):
    title: str
    is_public: bool
    description: str


# チケットステータス変更（PUT）
class UpdateTicketStatusRequest(BaseModel):
    status: TicketStatusType
