import pytest

from fastapi.testclient import TestClient
from jose import JWTError
from jose.exceptions import ExpiredSignatureError

import helpdesk_app_backend.api.v1.healthcheck as api_healthcheck

BASE_URL = "/api/v1/healthcheck"


def test_healthcheck(test_client: TestClient) -> None:
    # 実行
    response = test_client.get(BASE_URL)

    # 検証
    assert response.json() == "success"
    assert response.status_code == 200


# アクセストークンが有効である
def test_auth_healthcheck_success(test_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_healthcheck, "verify_access_token", lambda token: "dummy.decode.token")

    test_client.cookies.set("access_token", "dummy.jwt")

    # 実行
    response = test_client.get(f"{BASE_URL}/auth")

    # 検証
    assert response.status_code == 200
    assert response.json() == "OK：access_token"


# アクセストークンが存在しない
def test_not_access_token(test_client: TestClient) -> None:
    # 実行
    response = test_client.get(f"{BASE_URL}/auth")

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "アクセストークンが存在しません"}


# アクセストークンの有効期限が切れている
def test_auth_healthcheck_expired(test_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # ExpiredSignatureErrorを投げる
    def fake_verify_access_token(token: str) -> str:
        raise ExpiredSignatureError()

    monkeypatch.setattr(api_healthcheck, "verify_access_token", fake_verify_access_token)

    test_client.cookies.set("access_token", "dummy.jwt")

    # 実行
    response = test_client.get(f"{BASE_URL}/auth")

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "有効期限切です"}


# 不正なアクセストークン
def test_auth_healthcheck_invalid(test_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # JWTErrorを投げる
    def fake_verify_access_token(token: str) -> str:
        raise JWTError()

    monkeypatch.setattr(api_healthcheck, "verify_access_token", fake_verify_access_token)

    test_client.cookies.set("access_token", "invalid.jwt")

    # 実行
    response = test_client.get(f"{BASE_URL}/auth")

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "不正なアクセストークンです"}
