from pydantic import BaseModel

from helpdesk_app_backend.models.enum.user import AccountType


# アカウント取得（GET）
class GetAccountResponseItem(BaseModel):
    id: int
    name: str
    email: str
    account_type: AccountType


# アカウント追加（POST）
class CreateAccountResponse(BaseModel):
    id: int
    name: str
    email: str
    account_type: AccountType
