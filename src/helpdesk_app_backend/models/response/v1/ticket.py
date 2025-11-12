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


# 対応履歴取得（GET）
class GetTicketHistoryResponseItem(BaseModel):
    id: int
    ticket: int
    action_user: str | None
    action_description: str
    created_at: datetime


# チケット詳細取得（GET）
class GetTicketDetailResponse(BaseModel):
    id: int
    title: str
    is_public: bool
    status: TicketStatusType
    description: str
    supporter: str | None
    created_at: datetime
    ticket_histories: list[GetTicketHistoryResponseItem]


# チケット追加（POST）
class CreateTicketResponse(BaseModel):
    id: int
    title: str
    is_public: bool
    status: TicketStatusType
    description: str
    staff: int
    created_at: datetime
