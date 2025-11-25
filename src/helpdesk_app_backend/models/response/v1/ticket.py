from datetime import datetime

from pydantic import BaseModel, Field

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
    is_own_ticket: bool = Field(
        default=False
    )  # 担当が自分であるかどうかのフラグであるが、サポーターが存在しない場合も false となる（FE側で supporter が null の時点で、is_own_ticket の値は気にしないためOK）
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


# チケットに対する質疑応答追加（POST）
class CreateTicketCommentResponse(BaseModel):
    id: int
    action_user: str
    comment: str


# チケット更新（PUT）
class UpdateTicketResponse(BaseModel):
    id: int
    status: TicketStatusType
    supporter: str | None


# チケット公開設定変更（PUT）
class UpdateTicketVisibilityResponse(BaseModel):
    id: int
    action_user: str
    is_public: bool
