from fastapi import APIRouter, Cookie
from jose import JWTError
from jose.exceptions import ExpiredSignatureError

from helpdesk_app_backend.exceptions.unauthorized_exception import UnauthorizedException
from helpdesk_app_backend.logic.business.security import verify_access_token

router = APIRouter()


# テスト用のエンドポイント
@router.get("")
def healthcheck() -> str:
    return "テストOK"


@router.get("/auth")
def auth_healthcheck(access_token: str | None = Cookie(default=None)) -> str | None:
    # access_token が None だったら 401エラーを返す
    if access_token is None:
        raise UnauthorizedException("アクセストークンが存在しません")

    # access_token が None でなければ 暗号解除(decode)を試みる
    try:
        verify_access_token(access_token)
        return "OK：access_token"

    # 暗号解除(decode)できなかった場合、401エラーを返す
    except ExpiredSignatureError as err:
        raise UnauthorizedException("有効期限切です") from err

    except JWTError as err:
        raise UnauthorizedException("不正なアクセストークンです") from err

    except Exception as err:
        raise err
