from fastapi import Cookie
from jose import JWTError
from jose.exceptions import ExpiredSignatureError

from helpdesk_app_backend.exceptions.unauthorized_exception import UnauthorizedException
from helpdesk_app_backend.logic.business.security import verify_access_token
from helpdesk_app_backend.models.internal.token_payload import AccessTokenPayload


# アクセストークンの検証
def validate_access_token(
    access_token: str | None = Cookie(default=None),
) -> AccessTokenPayload:
    # access_token が None だったら 401エラーを返す
    if access_token is None:
        raise UnauthorizedException("アクセストークンが存在しません")

    # access_token が None でなければ 暗号解除(decode)を試みる
    try:
        # access_token の user_id が None だったらエラーを返す
        access_token_payload = verify_access_token(access_token)
        user_id = access_token_payload.get("user_id")
        if user_id is None:
            raise JWTError
        # デコードした access_token 返す
        return AccessTokenPayload(
            sub=access_token_payload["sub"],
            user_id=access_token_payload["user_id"],
            account_type=access_token_payload["account_type"],
            exp=access_token_payload["exp"],
        )

    # 暗号解除(decode)できなかった場合、401エラーを返す
    except ExpiredSignatureError as err:
        raise UnauthorizedException("有効期限切れです") from err

    except JWTError as err:
        raise UnauthorizedException("不正なアクセストークンです") from err

    except Exception as err:
        raise err
