from typing import Annotated

from fastapi import APIRouter, Depends

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.response.v1.healthcheck import HealthcheckAuthResponse

router = APIRouter()


# テスト用のエンドポイント
@router.get("")
def healthcheck() -> str:
    return "success"


@router.get("/auth")
def auth_healthcheck(
    access_token: Annotated[dict, Depends(validate_access_token)],
) -> HealthcheckAuthResponse:
    account_type = AccountType(access_token.get("account_type"))
    return HealthcheckAuthResponse(account_type=account_type)
