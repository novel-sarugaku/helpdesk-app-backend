from collections.abc import Callable
from dataclasses import dataclass

import pytest

from fastapi.testclient import TestClient

from helpdesk_app_backend.api.v1 import healthcheck as api_healthcheck
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.internal.token_payload import AccessTokenPayload

BASE_URL = "/api/v1/healthcheck"


@dataclass
class DummyUser:
    id: int
    name: str
    is_suspended: bool


def test_healthcheck(test_client: TestClient) -> None:
    # 実行
    response = test_client.get(BASE_URL)

    # 検証
    assert response.json() == "success"
    assert response.status_code == 200


# GETテスト（成功）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_auth_healthcheck_return_account_type(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccessTokenPayload], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    access_token = AccessTokenPayload(
        sub="test@example.com",
        user_id=1,
        account_type=account_type,
        exp=1761905996,
    )

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_healthcheck,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=1, name="テスト社員1", is_suspended=False),
    )

    # 実行
    response = test_client.get(f"{BASE_URL}/auth")

    # 検証
    assert response.status_code == 200
    assert response.json() == {"account_type": "admin"}


# GETテスト（失敗：アカウントが停止中の場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_auth_healthcheck_is_suspended_account(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccessTokenPayload], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    access_token = AccessTokenPayload(
        sub="test@example.com",
        user_id=1,
        account_type=account_type,
        exp=1761905996,
    )

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_healthcheck,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=1, name="テスト社員1", is_suspended=True),
    )

    # 実行
    response = test_client.get(f"{BASE_URL}/auth")

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "このアカウントは停止中です"}
