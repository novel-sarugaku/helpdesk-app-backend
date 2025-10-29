from pydantic import BaseModel

from helpdesk_app_backend.models.enum.user import AccountType


# アカウント取得（GET）
class GetAccountResponseItem(BaseModel):
    id: int
    name: str
    email: str
    account_type: AccountType
    is_suspended: bool


# アカウント追加（POST）
class CreateAccountResponse(BaseModel):
    id: int
    name: str
    email: str
    account_type: AccountType
    is_suspended: bool


# アカウント利用状態更新（PUT）
class UpdateAccountResponse(BaseModel):
    id: int
    name: str
    email: str
    account_type: AccountType
    is_suspended: bool
