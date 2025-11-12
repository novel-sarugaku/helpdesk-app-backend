from datetime import datetime

from pydantic import BaseModel


# 対応情報取得（GET）
class GetActionResponseItem(BaseModel):
    id: int
    ticket: int
    action_user: str | None
    action_description: str
    created_at: datetime
