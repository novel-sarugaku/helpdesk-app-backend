from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

import pytest

from fastapi.testclient import TestClient

from helpdesk_app_backend.api.v1 import ticket as api_ticket
from helpdesk_app_backend.models.enum.ticket import TicketStatusType
from helpdesk_app_backend.models.enum.user import AccountType


@dataclass
class DummyUser:
    name: str


@dataclass
class DummyTicket:
    id: int
    title: str
    is_public: bool
    status: TicketStatusType
    staff_id: int
    staff: DummyUser
    supporter_id: int
    supporter: DummyUser
    created_at: datetime


# GETテスト（成功：アカウントタイプが社員の場合）
@pytest.mark.parametrize("account_type", [AccountType.STAFF])
def test_get_accounts_success_for_staff(
    test_client: TestClient,
    override_validate_access_token: Callable[[dict], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    access_token = {
        "sub": "test@example.com",
        "user_id": 1,
        "account_type": account_type.value,
        "exp": 1761905996,
    }

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=True,
            status=TicketStatusType.START,
            staff_id=1,
            staff=DummyUser(name="テスト社員1"),
            supporter_id=1,
            supporter=DummyUser(name="テストサポート担当者1"),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=2,
            title="テストチケット2",
            is_public=False,
            staff_id=1,
            status=TicketStatusType.START,
            staff=DummyUser(name="テスト社員1"),
            supporter_id=1,
            supporter=DummyUser(name="テストサポート担当者1"),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=3,
            title="テストチケット3",
            is_public=True,
            status=TicketStatusType.START,
            staff_id=2,
            staff=DummyUser(name="テスト社員2"),
            supporter_id=1,
            supporter=DummyUser(name="テストサポート担当者1"),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=4,
            title="テストチケット4",
            is_public=False,
            staff_id=2,
            status=TicketStatusType.START,
            staff=DummyUser(name="テスト社員2"),
            supporter_id=1,
            supporter=DummyUser(name="テストサポート担当者1"),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

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


# GETテスト（成功：アカウントタイプが社員以外の場合）
@pytest.mark.parametrize("account_type", [AccountType.ADMIN, AccountType.SUPPORTER])
def test_get_accounts_success_for_other(
    test_client: TestClient,
    override_validate_access_token: Callable[[dict], None],
    account_type: AccountType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    access_token = {
        "sub": "test@example.com",
        "user_id": 1,
        "account_type": account_type.value,
        "exp": 1761905996,
    }

    # テスト用登録済データ
    registered_data = [
        DummyTicket(
            id=1,
            title="テストチケット1",
            is_public=True,
            status=TicketStatusType.START,
            staff_id=1,
            staff=DummyUser(name="テスト社員1"),
            supporter_id=1,
            supporter=DummyUser(name="テストサポート担当者1"),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=2,
            title="テストチケット2",
            is_public=False,
            staff_id=1,
            status=TicketStatusType.START,
            staff=DummyUser(name="テスト社員1"),
            supporter_id=1,
            supporter=DummyUser(name="テストサポート担当者1"),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=3,
            title="テストチケット3",
            is_public=True,
            status=TicketStatusType.START,
            staff_id=2,
            staff=DummyUser(name="テスト社員2"),
            supporter_id=1,
            supporter=DummyUser(name="テストサポート担当者1"),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
        DummyTicket(
            id=4,
            title="テストチケット4",
            is_public=False,
            staff_id=2,
            status=TicketStatusType.START,
            staff=DummyUser(name="テスト社員2"),
            supporter_id=1,
            supporter=DummyUser(name="テストサポート担当者1"),
            created_at=datetime(2020, 7, 21, 6, 12, 30, 551),
        ),
    ]

    override_validate_access_token(access_token)

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
