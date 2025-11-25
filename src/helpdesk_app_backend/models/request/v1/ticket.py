from pydantic import BaseModel

from helpdesk_app_backend.models.enum.ticket import TicketStatusType


# チケット追加（POST）
class CreateTicketRequest(BaseModel):
    title: str
    is_public: bool
    description: str


# チケットに対する質疑応答追加（POST）
class CreateTicketCommentRequest(BaseModel):
    comment: str


# チケットステータス変更（PUT）
class UpdateTicketStatusRequest(BaseModel):
    status: TicketStatusType


# チケット公開設定変更（PUT）
class UpdateTicketVisibilityRequest(BaseModel):
    is_public: bool
