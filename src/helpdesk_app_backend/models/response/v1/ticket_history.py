from datetime import datetime

from pydantic import BaseModel


# 対応履歴取得（GET）
class GetTicketHistoryResponseItem(BaseModel):
    id: int
    ticket: int
    action_user: str | None
    action_description: str
    created_at: datetime
