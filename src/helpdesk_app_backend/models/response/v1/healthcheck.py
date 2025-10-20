from pydantic import BaseModel

from helpdesk_app_backend.models.enum.user import AccountType


class HealthcheckAuthResponse(BaseModel):
    account_type: AccountType
