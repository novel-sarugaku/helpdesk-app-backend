import pytest

from jose import jwt

import helpdesk_app_backend.core.check_token as check_token
import helpdesk_app_backend.logic.business.security as security

from helpdesk_app_backend.exceptions.unauthorized_exception import UnauthorizedException
from helpdesk_app_backend.models.enum.user import AccountType


# アクセストークンが有効
def test_validate_access_token_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        check_token,
        "verify_access_token",
        lambda token: {"account_type": AccountType.ADMIN.value, "user_id": 1},
    )

    # 実行
    response = check_token.validate_access_token("dummy.jwt")

    # 検証
    assert response ==  {'account_type': 'admin', 'user_id': 1}


# アクセストークンが存在しない
def test_not_access_token() -> None:
    # 検証
    # トークンが None である場合 UnauthorizedException が返る
    with pytest.raises(UnauthorizedException, match="アクセストークンが存在しません"):
        check_token.validate_access_token(None)


# アクセストークンの有効期限が切れている
def test_validate_access_token_expired(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(security, "SECRET_KEY", "testsecret")
    monkeypatch.setattr(security, "ALGORITHM", "HS256")

    # 有効期限切れトークン
    test_expired_token = jwt.encode(
        {"account_type": AccountType.ADMIN.value, "exp": 1},  # 1970/1/1 から1秒後
        "testsecret",
        algorithm="HS256",
    )

    # 検証
    with pytest.raises(UnauthorizedException, match="有効期限切れです"):
        check_token.validate_access_token(test_expired_token)


# 不正なアクセストークン
def test_validate_access_token_invalid() -> None:
    # 検証
    with pytest.raises(UnauthorizedException, match="不正なアクセストークンです"):
        check_token.validate_access_token("wrong_token")
