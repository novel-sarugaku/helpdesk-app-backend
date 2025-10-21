from dataclasses import dataclass

import pytest

from fastapi.testclient import TestClient

import helpdesk_app_backend.api.v1.user_account as api_user_account

from helpdesk_app_backend.models.enum.user import AccountType


@dataclass
class DummyUserAccount:
    id: int
    name: str
    email: str
    password: str
    account_type: AccountType


# GETテスト
@pytest.mark.usefixtures("override_get_db")
def test_get_user_account(test_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # テスト用登録済データ
    registered_data = [
        DummyUserAccount(
            id=1,
            name="テストユーザー",
            email="tester@example.com",
            password="hashedpass",
            account_type=AccountType.STAFF,
        )
    ]

    monkeypatch.setattr(api_user_account, "get_user_account_all", lambda _session: registered_data)

    # 実行
    response = test_client.get("/api/v1/user_account")

    # 検証
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "テストユーザー",
            "email": "tester@example.com",
            "account_type": "staff",
        }
    ]
