from fastapi import APIRouter, Cookie

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.models.response.v1.healthcheck import HealthcheckAuthResponse

router = APIRouter()


# テスト用のエンドポイント
@router.get("")
def healthcheck() -> str:
    return "success"


@router.get("/auth")
def auth_healthcheck(access_token: str | None = Cookie(default=None)) -> HealthcheckAuthResponse:
    return validate_access_token(access_token)
