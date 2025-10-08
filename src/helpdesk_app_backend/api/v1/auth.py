from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.schemas.auth import Token, UserLogin
from helpdesk_app_backend.services.auth import AuthService

router = APIRouter()


# 入力が正しい場合トークン（JWT）を返す。入力が正しくない場合 401 を返す。
@router.post("/login", response_model=Token)
def login(body: UserLogin, session: Annotated[Session, Depends(get_db)]) -> Token:
    try:
        # AuthServiceがログイン処理を行い、返ってきた結果（辞書）を受け取る。
        result = AuthService.login_user(session, body)
        # 受け取った辞書から access_token と token_type を取り出し、Token に詰めて返す（Swaggerのスキーマにも合う形に整えるため）。
        return Token(access_token=result["access_token"], token_type=result["token_type"])
    # 401 エラーを返す
    except HTTPException:
        raise


@router.post("/logout", status_code=204)
def logout() -> Response:
    return Response(status_code=204)
