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
    is_suspended: bool


# GETテスト（成功）
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
            is_suspended=False,
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
            "is_suspended": False,
        }
    ]


# GETテスト（失敗：管理者以外がアカウント登録しようとした場合）
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
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    override_validate_access_token(account_type)

    monkeypatch.setattr(api_account, "get_user_by_email", lambda _session, email: None)

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
    print(response.text)
    assert response.status_code == 200
    assert success_session.commit_called is True  # commitが呼ばれたことを確認
    assert response.json() == {
        "id": 1,
        "name": "テストユーザー",
        "email": "tester@example.com",
        "account_type": "staff",
        "is_suspended": False,
    }


# POSTテスト（失敗）
@pytest.mark.usefixtures("override_get_db_error")
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_create_account_error(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    error_session: "FakeSessionCommitError",
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    override_validate_access_token(account_type)

    monkeypatch.setattr(api_account, "get_user_by_email", lambda _session, email: None)

    # テスト用登録予定データ
    body = {
        "name": "テストユーザー",
        "email": "tester@example.com",
        "password": "testPass123",
        "account_type": "staff",
        "is_suspended": "false",
    }

    # 実行
    test_client.post("/api/v1/admin/account", json=body)

    # 検証
    assert error_session.commit_called is True  # commitが呼ばれたことを確認
    assert error_session.rolled_back is True  # rollbackが呼ばれたことを確認


# POSTテスト（失敗：管理者以外がアカウント登録しようとした場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF, AccountType.SUPPORTER])
def test_create_accounts_forbidden(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
) -> None:
    override_validate_access_token(account_type)

    # テスト用登録予定データ
    body = {
        "name": "テストユーザー",
        "email": "tester@example.com",
        "password": "testPass123",
        "account_type": "staff",
        "is_suspended": "false",
    }

    # 実行
    response = test_client.post("/api/v1/admin/account", json=body)

    # 検証
    assert response.status_code == 403
    assert response.json() == {"detail": "アクセス権限がありません"}


# POSTテスト（失敗：登録済みEメールで登録しようとした場合）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_create_account_email_conflict(
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
            is_suspended=False,
        )
    ]

    monkeypatch.setattr(api_account, "get_user_by_email", lambda _session, email: registered_data)

    override_validate_access_token(account_type)

    # テスト用登録予定データ
    body = {
        "name": "テストユーザー",
        "email": "tester@example.com",
        "password": "testPass123",
        "account_type": "staff",
        "is_suspended": "false",
    }

    # 実行
    response = test_client.post("/api/v1/admin/account", json=body)

    # 検証
    assert response.status_code == 422
    assert response.json() == {"detail": "すでに存在するメールアドレスです"}


# POSTテスト（失敗：アカウントタイプを管理者で登録しようとした場合）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_create_account_admin_type_forbidden(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    override_validate_access_token(account_type)

    monkeypatch.setattr(api_account, "get_user_by_email", lambda _session, email: None)

    # テスト用登録予定データ
    body = {
        "name": "テストユーザー",
        "email": "tester@example.com",
        "password": "testPass123",
        "account_type": "admin",
        "is_suspended": "false",
    }

    # 実行
    response = test_client.post("/api/v1/admin/account", json=body)

    # 検証
    assert response.status_code == 422
    assert response.json() == {"detail": "管理者アカウントは作成できません"}


# PUTテスト（成功）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_update_account_success(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    override_validate_access_token(account_type)

    # テスト用登録済データ
    registered_data = DummyAccount(
        id=2,
        name="テストユーザー",
        email="tester@example.com",
        password="hashedpass",
        account_type=AccountType.STAFF,
        is_suspended=False,
    )

    monkeypatch.setattr(api_account, "get_user_by_id", lambda _session, id: registered_data)

    # テスト用更新予定データ
    body = {
        "id": "2",
        "is_suspended": True,
    }

    # 実行
    response = test_client.put("/api/v1/admin/account", json=body)

    # 検証
    assert response.status_code == 200


# PUTテスト（失敗）
@pytest.mark.usefixtures("override_get_db_error")
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_update_account_error(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    error_session: "FakeSessionCommitError",
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    override_validate_access_token(account_type)

    # テスト用登録済データ
    registered_data = DummyAccount(
        id=2,
        name="テストユーザー",
        email="tester@example.com",
        password="hashedpass",
        account_type=AccountType.STAFF,
        is_suspended=False,
    )

    monkeypatch.setattr(api_account, "get_user_by_id", lambda _session, id: registered_data)

    # テスト用更新予定データ
    body = {
        "id": "2",
        "is_suspended": True,
    }

    # 実行
    test_client.put("/api/v1/admin/account", json=body)

    # 検証
    assert error_session.commit_called is True  # commitが呼ばれたことを確認
    assert error_session.rolled_back is True  # rollbackが呼ばれたことを確認


# PUTテスト（失敗：管理者以外がアカウント更新しようとした場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF, AccountType.SUPPORTER])
def test_update_accounts_forbidden(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
) -> None:
    override_validate_access_token(account_type)

    # テスト用更新予定データ
    body = {
        "id": "2",
        "is_suspended": True,
    }

    # 実行
    response = test_client.put("/api/v1/admin/account", json=body)

    # 検証
    assert response.status_code == 403
    assert response.json() == {"detail": "アクセス権限がありません"}


# PUTテスト（失敗：指定したアカウントが存在しない場合）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_update_account_id_missing(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    override_validate_access_token(account_type)

    monkeypatch.setattr(api_account, "get_user_by_id", lambda _session, id: None)

    # テスト用更新予定データ
    body = {
        "id": "999",
        "is_suspended": True,
    }

    # 実行
    response = test_client.put("/api/v1/admin/account", json=body)

    # 検証
    assert response.status_code == 422
    assert response.json() == {"detail": "指定したアカウントが存在しません"}


# PUTテスト（失敗：管理者の利用状態を更新しようとした場合）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_update_account_admin_type_forbidden(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    override_validate_access_token(account_type)

    # テスト用登録済データ
    registered_data = DummyAccount(
        id=1,
        name="テスト管理者",
        email="testAdmin@example.com",
        password="hashedpass",
        account_type=AccountType.ADMIN,
        is_suspended=False,
    )

    monkeypatch.setattr(api_account, "get_user_by_id", lambda _session, id: registered_data)

    # テスト用更新予定データ
    body = {
        "id": "1",
        "is_suspended": True,
    }

    # 実行
    response = test_client.put("/api/v1/admin/account", json=body)

    # 検証
    assert response.status_code == 422
    assert response.json() == {"detail": "管理者アカウントの利用状態は変更できません"}
