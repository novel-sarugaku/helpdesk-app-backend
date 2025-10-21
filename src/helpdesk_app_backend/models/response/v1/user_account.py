from pydantic import BaseModel

from helpdesk_app_backend.models.enum.user import AccountType


class GetUserAccountResponse(BaseModel):
    id: int
    name: str
    email: str
    account_type: AccountType
