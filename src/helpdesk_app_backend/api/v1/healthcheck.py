from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.exceptions.unauthorized_exception import UnauthorizedException
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.internal.token_payload import AccessTokenPayload
from helpdesk_app_backend.models.response.v1.healthcheck import HealthcheckAuthResponse
from helpdesk_app_backend.repositories.user import get_user_by_id

router = APIRouter()


# テスト用のエンドポイント
@router.get("")
def healthcheck() -> str:
    return "success"


@router.get("/auth")
def auth_healthcheck(
    session: Annotated[Session, Depends(get_db)],
    access_token: Annotated[AccessTokenPayload, Depends(validate_access_token)],
) -> HealthcheckAuthResponse:
    account_type = access_token.account_type
    user_id = access_token.user_id

    target_account = get_user_by_id(session, id=user_id)

    # アカウントが停止状態（is_suspended=True）の場合
    if target_account.is_suspended:
        raise UnauthorizedException("このアカウントは停止中です")

    return HealthcheckAuthResponse(account_type=account_type)
