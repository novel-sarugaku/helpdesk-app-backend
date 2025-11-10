from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

import pytest

from conftest import FakeSessionCommitError, FakeSessionCommitSuccess
from fastapi.testclient import TestClient

from helpdesk_app_backend.api.v1 import ticket as api_ticket
from helpdesk_app_backend.models.enum.ticket import TicketStatusType
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.internal.token_payload import AccessTokenPayload


@dataclass
class DummyUser:
    id: int
    name: str
    is_suspended: bool


@dataclass
class DummyTicket:
    id: int
    title: str
    is_public: bool
    status: TicketStatusType
    description: str
    staff_id: int
    staff: DummyUser
    supporter_id: int
    supporter: DummyUser
    created_at: datetime


# GETテスト：一覧取得（成功：アカウントタイプが社員の場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_get_tickets_success_for_staff(
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

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=True,
            status=TicketStatusType.START,
            description="テスト詳細1",
            staff_id=1,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=2,
            title="テストチケット2",
            is_public=False,
            staff_id=1,
            description="テスト詳細2",
            status=TicketStatusType.START,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=3,
            title="テストチケット3",
            is_public=True,
            status=TicketStatusType.START,
            description="テスト詳細3",
            staff_id=2,
            staff=DummyUser(id=2, name="テスト社員2", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=4,
            title="テストチケット4",
            is_public=False,
            staff_id=2,
            status=TicketStatusType.START,
            description="テスト詳細4",
            staff=DummyUser(id=2, name="テスト社員2", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_ticket,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=1, name="テスト社員1", is_suspended=False),
    )
    monkeypatch.setattr(api_ticket, "get_tickets_all", lambda _session: registered_data)

    # 実行
    response = test_client.get("api/v1/ticket")

    # 検証
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "テストチケット1",
            "is_public": True,
            "status": TicketStatusType.START.value,
            "staff": "テスト社員1",
            "supporter": "テストサポート担当者1",
            "created_at": "2020-07-21T06:12:30.000551",
        },
        {
            "id": 2,
            "title": "テストチケット2",
            "is_public": False,
            "status": TicketStatusType.START.value,
            "staff": "テスト社員1",
            "supporter": "テストサポート担当者1",
            "created_at": "2020-07-21T06:12:30.000551",
        },
        {
            "id": 3,
            "title": "テストチケット3",
            "is_public": True,
            "status": TicketStatusType.START.value,
            "staff": "テスト社員2",
            "supporter": "テストサポート担当者1",
            "created_at": "2020-07-21T06:12:30.000551",
        },
    ]


# GETテスト：一覧取得（成功：アカウントタイプが社員以外の場合）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN, AccountType.SUPPORTER])
def test_get_tickets_success_for_other(
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

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=True,
            status=TicketStatusType.START,
            description="テスト詳細1",
            staff_id=1,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=2,
            title="テストチケット2",
            is_public=False,
            staff_id=1,
            status=TicketStatusType.START,
            description="テスト詳細2",
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=3,
            title="テストチケット3",
            is_public=True,
            status=TicketStatusType.START,
            description="テスト詳細3",
            staff_id=2,
            staff=DummyUser(id=2, name="テスト社員2", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=4,
            title="テストチケット4",
            is_public=False,
            staff_id=2,
            status=TicketStatusType.START,
            description="テスト詳細4",
            staff=DummyUser(id=2, name="テスト社員2", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_ticket,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=1, name="テスト社員1", is_suspended=False),
    )
    monkeypatch.setattr(api_ticket, "get_tickets_all", lambda _session: registered_data)

    # 実行
    response = test_client.get("api/v1/ticket")

    # 検証
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "テストチケット1",
            "is_public": True,
            "status": TicketStatusType.START.value,
            "staff": "テスト社員1",
            "supporter": "テストサポート担当者1",
            "created_at": "2020-07-21T06:12:30.000551",
        },
        {
            "id": 2,
            "title": "テストチケット2",
            "is_public": False,
            "status": TicketStatusType.START.value,
            "staff": "テスト社員1",
            "supporter": "テストサポート担当者1",
            "created_at": "2020-07-21T06:12:30.000551",
        },
        {
            "id": 3,
            "title": "テストチケット3",
            "is_public": True,
            "status": TicketStatusType.START.value,
            "staff": "テスト社員2",
            "supporter": "テストサポート担当者1",
            "created_at": "2020-07-21T06:12:30.000551",
        },
        {
            "id": 4,
            "title": "テストチケット4",
            "is_public": False,
            "status": TicketStatusType.START.value,
            "staff": "テスト社員2",
            "supporter": "テストサポート担当者1",
            "created_at": "2020-07-21T06:12:30.000551",
        },
    ]


# GETテスト：一覧取得（失敗：アカウントが停止中の場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_get_tickets_is_suspended_account(
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

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=True,
            status=TicketStatusType.START,
            description="テスト詳細1",
            staff_id=1,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_ticket,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=1, name="テスト社員1", is_suspended=True),
    )
    monkeypatch.setattr(api_ticket, "get_tickets_all", lambda _session: registered_data)

    # 実行
    response = test_client.get("api/v1/ticket")

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "このアカウントは停止中です"}


# GETテスト：詳細取得（成功：アカウントタイプが社員の場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_get_ticket_detail_success_for_staff(
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

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=False,
            status=TicketStatusType.START,
            description="テスト詳細1",
            staff_id=1,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=2,
            title="テストチケット2",
            is_public=True,
            staff_id=1,
            description="テスト詳細2",
            status=TicketStatusType.START,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_ticket,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=1, name="テスト社員1", is_suspended=False),
    )
    monkeypatch.setattr(
        api_ticket,
        "get_ticket_by_id",
        lambda _session, id: next((ticket for ticket in registered_data if ticket.id == id), None),
    )  # next() → 条件に合う最初のチケットを返す、なければ None

    # 実行
    response = test_client.get("api/v1/ticket/2")

    # 検証
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "title": "テストチケット2",
        "is_public": True,
        "status": TicketStatusType.START.value,
        "description": "テスト詳細2",
        "supporter": "テストサポート担当者1",
        "created_at": "2020-07-21T06:12:30.000551",
    }


# GETテスト：詳細取得（成功：アカウントタイプが社員以外の場合）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN, AccountType.SUPPORTER])
def test_get_ticket_detail_success_for_other(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccessTokenPayload], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    access_token = AccessTokenPayload(
        sub="test@example.com",
        user_id=5,
        account_type=account_type,
        exp=1761905996,
    )

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=False,
            status=TicketStatusType.START,
            description="テスト詳細1",
            staff_id=1,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=2,
            title="テストチケット2",
            is_public=True,
            staff_id=1,
            description="テスト詳細2",
            status=TicketStatusType.START,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_ticket,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
    )
    monkeypatch.setattr(
        api_ticket,
        "get_ticket_by_id",
        lambda _session, id: next((ticket for ticket in registered_data if ticket.id == id), None),
    )  # next() → 条件に合う最初のチケットを返す、なければ None

    # 実行
    response = test_client.get("api/v1/ticket/1")

    # 検証
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "テストチケット1",
        "is_public": False,
        "status": TicketStatusType.START.value,
        "description": "テスト詳細1",
        "supporter": "テストサポート担当者1",
        "created_at": "2020-07-21T06:12:30.000551",
    }


# GETテスト：詳細取得（失敗：指定したチケットが存在しない場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_get_ticket_detail_not_found_for_unknown_id(
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

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=False,
            status=TicketStatusType.START,
            description="テスト詳細1",
            staff_id=1,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=2,
            title="テストチケット2",
            is_public=True,
            staff_id=1,
            description="テスト詳細2",
            status=TicketStatusType.START,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_ticket,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=1, name="テスト社員1", is_suspended=False),
    )
    monkeypatch.setattr(
        api_ticket,
        "get_ticket_by_id",
        lambda _session, id: next((ticket for ticket in registered_data if ticket.id == id), None),
    )  # next() → 条件に合う最初のチケットを返す、なければ None

    # 実行
    response = test_client.get("api/v1/ticket/99")

    # 検証
    assert response.status_code == 422
    assert response.json() == {"detail": "指定したチケットは存在しません"}


# GETテスト：詳細取得（失敗：社員が他人の非公開チケットを取得しようとした場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_get_ticket_detail_forbidden_when_staff_accesses_others_private(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccessTokenPayload], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    access_token = AccessTokenPayload(
        sub="test@example.com",
        user_id=2,
        account_type=account_type,
        exp=1761905996,
    )

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=False,
            status=TicketStatusType.START,
            description="テスト詳細1",
            staff_id=1,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=2,
            title="テストチケット2",
            is_public=True,
            staff_id=1,
            description="テスト詳細2",
            status=TicketStatusType.START,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=False),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_ticket,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=2, name="テスト社員2", is_suspended=False),
    )
    monkeypatch.setattr(
        api_ticket,
        "get_ticket_by_id",
        lambda _session, id: next((ticket for ticket in registered_data if ticket.id == id), None),
    )  # next() → 条件に合う最初のチケットを返す、なければ None

    # 実行
    response = test_client.get("api/v1/ticket/1")

    # 検証
    assert response.status_code == 403
    assert response.json() == {"detail": "他の社員の非公開チケットは閲覧できません"}


# GETテスト：詳細取得（失敗：アカウントが停止中の場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_get_ticket_detail_is_suspended_account(
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

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=False,
            status=TicketStatusType.START,
            description="テスト詳細1",
            staff_id=1,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=True),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=2,
            title="テストチケット2",
            is_public=True,
            staff_id=1,
            description="テスト詳細2",
            status=TicketStatusType.START,
            staff=DummyUser(id=1, name="テスト社員1", is_suspended=True),
            supporter_id=1,
            supporter=DummyUser(id=5, name="テストサポート担当者1", is_suspended=False),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

    monkeypatch.setattr(
        api_ticket,
        "get_user_by_id",
        lambda _session, id: DummyUser(id=1, name="テスト社員1", is_suspended=True),
    )
    monkeypatch.setattr(
        api_ticket,
        "get_ticket_by_id",
        lambda _session, id: next((ticket for ticket in registered_data if ticket.id == id), None),
    )  # next() → 条件に合う最初のチケットを返す、なければ None

    # 実行
    response = test_client.get("api/v1/ticket/1")

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "このアカウントは停止中です"}


# POSTテスト（成功）
@pytest.mark.usefixtures("override_get_db_success")
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_create_ticket_success(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccessTokenPayload], None],
    account_type: AccountType,
    success_session: "FakeSessionCommitSuccess",
) -> None:
    access_token = AccessTokenPayload(
        sub="test@example.com",
        user_id=1,
        account_type=account_type,
        exp=1761905996,
    )

    override_validate_access_token(access_token)

    # テスト用登録予定データ
    body = {
        "title": "テストタイトル",
        "is_public": True,
        "description": "テスト詳細",
        "staff_id": 1,
    }

    # 実行
    response = test_client.post("/api/v1/ticket", json=body)

    # 検証
    assert response.status_code == 200
    assert success_session.commit_called is True


# POSTテスト（失敗）
@pytest.mark.usefixtures("override_get_db_error")
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_create_account_error(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccessTokenPayload], None],
    account_type: AccountType,
    error_session: "FakeSessionCommitError",
) -> None:
    access_token = AccessTokenPayload(
        sub="test@example.com",
        user_id=1,
        account_type=account_type,
        exp=1761905996,
    )

    override_validate_access_token(access_token)

    # テスト用登録予定データ
    body = {
        "title": "テストタイトル",
        "is_public": True,
        "description": "テスト詳細",
        "staff_id": 1,
    }

    # 実行
    test_client.post("/api/v1/ticket", json=body)

    # 検証
    assert error_session.commit_called is True
    assert error_session.rolled_back is True


# POSTテスト（失敗：社員以外がチケット登録しようとした場合）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN, AccountType.SUPPORTER])
def test_create_accounts_forbidden(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccessTokenPayload], None],
    account_type: AccountType,
) -> None:
    access_token = AccessTokenPayload(
        sub="test@example.com",
        user_id=1,
        account_type=account_type,
        exp=1761905996,
    )

    override_validate_access_token(access_token)

    # テスト用登録予定データ
    body = {
        "title": "テストタイトル",
        "is_public": True,
        "description": "テスト詳細",
        "staff_id": 1,
    }

    # 実行
    response = test_client.post("/api/v1/ticket", json=body)

    # 検証
    assert response.status_code == 403
    assert response.json() == {"detail": "社員でないためチケットの登録はできません"}
