from dataclasses import dataclass

import pytest

from fastapi.testclient import TestClient

import helpdesk_app_backend.api.v1.admin.account as api_account

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.main import app
from helpdesk_app_backend.models.enum.user import AccountType


@dataclass
class DummyAccount:
    id: int
    name: str
    email: str
    password: str
    account_type: AccountType


# GETテスト（成功）
@pytest.mark.usefixtures("override_get_db")
def test_get_accounts_success(test_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # app.dependency_overrides → Depends() に渡した関数差し替え。今回、AccountType.ADMINで返す
    monkeypatch.setitem(app.dependency_overrides, validate_access_token, lambda: AccountType.ADMIN)

    # テスト用登録済データ
    registered_data = [
        DummyAccount(
            id=1,
            name="テストユーザー",
            email="tester@example.com",
            password="hashedpass",
            account_type=AccountType.STAFF,
        )
    ]

    monkeypatch.setattr(api_account, "get_users_all", lambda _session: registered_data)

    # 実行
    response = test_client.get("/api/v1/admin/account")

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


# GETテスト（失敗）
def test_get_accounts_forbidden_when_staff(
    test_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(app.dependency_overrides, validate_access_token, lambda: AccountType.STAFF)

    # 実行
    response = test_client.get("/api/v1/admin/account")
    # 検証
    assert response.status_code == 403
    assert response.json() == {"detail": "アクセス権限がありません"}
