from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from helpdesk_app_backend.core.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from helpdesk_app_backend.exceptions.unauthorized_exception import UnauthorizedException
from helpdesk_app_backend.logic.business.security import create_access_token, verify_password
from helpdesk_app_backend.logic.calculate.calculate_datetime import get_now_UTC
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.db.user import User
from helpdesk_app_backend.models.request.v1.auth import LoginRequest
from helpdesk_app_backend.repositories.user import get_user_by_email

router = APIRouter()


@router.post("/login")
def login(
    body: LoginRequest, session: Annotated[Session, Depends(get_db)], response: Response
) -> None:
    # リクエスト展開
    target_user_email = body.email
    target_user_pass = body.password

    # target userの取得
    target_user: User = get_user_by_email(session, email=target_user_email)

    # ユーザーの存在、パスワードの確認
    if not target_user or not verify_password(
        plain_password=target_user_pass, hashed_password=target_user.password
    ):
        raise UnauthorizedException("メールアドレスまたはパスワードが一致しません")

    # payload作成
    payload = {
        "sub": target_user.email,
        "exp": get_now_UTC() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    access_token = create_access_token(payload)

    # cookieにtokenを付与
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.status_code = 204


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie("access_token")
    response.status_code = 204
