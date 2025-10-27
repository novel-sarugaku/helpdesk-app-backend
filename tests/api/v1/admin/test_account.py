from collections.abc import Callable
from dataclasses import dataclass

import pytest

from conftest import FakeSessionCommitError, FakeSessionCommitSuccess
from fastapi.testclient import TestClient

from helpdesk_app_backend.api.v1.admin import account as api_account
from helpdesk_app_backend.models.enum.user import AccountType


@dataclass
class DummyAccount:
    id: int
    name: str
    email: str
    password: str
    account_type: AccountType


# GETテスト（成功）
@pytest.mark.usefixtures("override_get_db_success")
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_get_accounts_success(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
    override_validate_access_token(account_type)

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
# @pytest.mark.parametrize → 同じテスト関数を、入力だけ変えて何回も実行するための仕組み
@pytest.mark.parametrize("account_type", [AccountType.STAFF, AccountType.SUPPORTER])
def test_get_accounts_forbidden(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
) -> None:
    # 受け取った account_type（STAFF/SUPPORTER）で、override_validate_access_token を実行
    override_validate_access_token(account_type)

    # 実行
    response = test_client.get("/api/v1/admin/account")
    # 検証
    assert response.status_code == 403
    assert response.json() == {"detail": "アクセス権限がありません"}


# POSTテスト（成功）
@pytest.mark.usefixtures("override_get_db_success")
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_create_account_success(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    success_session: "FakeSessionCommitSuccess",
) -> None:
    override_validate_access_token(account_type)

    # テスト用登録予定データ
    body = {
        "name": "テストユーザー",
        "email": "tester@example.com",
        "password": "testPass123",
        "account_type": "staff",
    }

    # 実行
    response = test_client.post("/api/v1/admin/account", json=body)

    # 検証
    assert response.status_code == 200
    assert success_session.commit_called is True  # commitが呼ばれたことを確認
    assert response.json() == {
        "id": 1,
        "name": "テストユーザー",
        "email": "tester@example.com",
        "account_type": "staff",
    }


# POSTテスト（失敗）
@pytest.mark.usefixtures("override_get_db_error")
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_create_account_error(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    error_session: "FakeSessionCommitError",
) -> None:
    override_validate_access_token(account_type)

    # テスト用登録予定データ
    body = {
        "name": "テストユーザー",
        "email": "tester@example.com",
        "password": "testPass123",
        "account_type": "staff",
    }

    # 実行
    test_client.post("/api/v1/admin/account", json=body)

    # 検証
    assert error_session.commit_called is True  # commitが呼ばれたことを確認
    assert error_session.rolled_back is True  # rollbackが呼ばれたことを確認


# POSTテスト（失敗：アクセス権限なし）
@pytest.mark.usefixtures("override_get_db_error")
@pytest.mark.parametrize("account_type", [AccountType.STAFF, AccountType.SUPPORTER])
def test_create_accounts_forbidden(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    error_session: "FakeSessionCommitError",
) -> None:
    override_validate_access_token(account_type)

    # テスト用登録予定データ
    body = {
        "name": "テストユーザー",
        "email": "tester@example.com",
        "password": "testPass123",
        "account_type": "staff",
    }

    # 実行
    response = test_client.post("/api/v1/admin/account", json=body)

    # 検証
    assert response.status_code == 403
    assert response.json() == {"detail": "アクセス権限がありません"}
