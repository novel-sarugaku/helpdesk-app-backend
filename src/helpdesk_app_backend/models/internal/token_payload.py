from pydantic import BaseModel

from helpdesk_app_backend.models.enum.user import AccountType


class AccessTokenPayload(BaseModel):
    sub: str
    user_id: int
    account_type: AccountType
    exp: int
