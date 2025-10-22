from fastapi import Cookie
from jose import JWTError
from jose.exceptions import ExpiredSignatureError

from helpdesk_app_backend.exceptions.unauthorized_exception import UnauthorizedException
from helpdesk_app_backend.logic.business.security import verify_access_token
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.response.v1.healthcheck import HealthcheckAuthResponse


# アクセストークンの検証
def validate_access_token(
    access_token: str | None = Cookie(default=None),
) -> HealthcheckAuthResponse:
    # access_token が None だったら 401エラーを返す
    if access_token is None:
        raise UnauthorizedException("アクセストークンが存在しません")

    # access_token が None でなければ 暗号解除(decode)を試みる
    try:
        # デコードした access_token から account_type を抽出
        decoded_access_token = verify_access_token(access_token)
        user_account_type = decoded_access_token.get("account_type")
        user_account_type_enum = AccountType(user_account_type)

        return HealthcheckAuthResponse(account_type=user_account_type_enum)

    # 暗号解除(decode)できなかった場合、401エラーを返す
    except ExpiredSignatureError as err:
        raise UnauthorizedException("有効期限切れです") from err

    except JWTError as err:
        raise UnauthorizedException("不正なアクセストークンです") from err

    except Exception as err:
        raise err
