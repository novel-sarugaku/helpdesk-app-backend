import pytest

from fastapi.testclient import TestClient
from jose import JWTError
from jose.exceptions import ExpiredSignatureError

import helpdesk_app_backend.api.v1.healthcheck as api_healthcheck

from helpdesk_app_backend.main import app

# 使用ライブラリ：TestClient（FastAPI標準）
# FastAPIアプリのエンドポイントをテストコードから呼び出すためのクライアント
client = TestClient(app)

base = "/api/v1/healthcheck"


def test_healthcheck() -> None:
    # 実行
    response = client.get(base)

    # 検証
    assert response.json() == "テストOK"
    assert response.status_code == 200


# アクセストークンが存在し正しい
def test_auth_healthcheck_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_verify_access_token(token: str) -> str:
        return "dummy.jwt.token"

    monkeypatch.setattr(api_healthcheck, "verify_access_token", fake_verify_access_token)

    client.cookies.set("access_token", "dummy.jwt")

    # 実行
    response = client.get(f"{base}/auth")

    # 検証
    assert response.status_code == 200
    assert response.json() == "OK：access_token"


# アクセストークンの有効期限が切れている
def test_auth_healthcheck_expired(monkeypatch: pytest.MonkeyPatch) -> None:
    # ExpiredSignatureErrorを投げる
    def fake_verify_access_token(token: str) -> str:
        raise ExpiredSignatureError()

    monkeypatch.setattr(api_healthcheck, "verify_access_token", fake_verify_access_token)

    client.cookies.set("access_token", "dummy.jwt")

    # 実行
    response = client.get(f"{base}/auth")

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "有効期限切です"}


# 不正なアクセストークン
def test_auth_healthcheck_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    # JWTErrorを投げる
    def fake_verify_access_token(token: str) -> str:
        raise JWTError()

    monkeypatch.setattr(api_healthcheck, "verify_access_token", fake_verify_access_token)

    client.cookies.set("access_token", "invalid.jwt")

    # 実行
    response = client.get(f"{base}/auth")

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "不正なアクセストークンです"}
