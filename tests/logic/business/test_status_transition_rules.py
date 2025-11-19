import pytest

from helpdesk_app_backend.logic.business.status_transition_rules import can_status_transition
from helpdesk_app_backend.models.enum.ticket import TicketStatusType


# current_status が「新規質問」の場合、各 new_status に対する正しい結果を返す
# 各変更先とその場合に期待する結果をまとめる
@pytest.mark.parametrize(
    "new_status,expected",
    [
        (TicketStatusType.START, False),
        (TicketStatusType.ASSIGNED, True),
        (TicketStatusType.IN_PROGRESS, False),
        (TicketStatusType.RESOLVED, False),
        (TicketStatusType.CLOSED, False),
    ],
)
def test_transition_from_start(new_status: TicketStatusType, expected: bool) -> None:
    # 検証
    assert can_status_transition(TicketStatusType.START, new_status) is expected


# current_status が「担当割り当て済み」の場合、各 new_status に対する正しい結果を返す
@pytest.mark.parametrize(
    "new_status,expected",
    [
        (TicketStatusType.START, True),
        (TicketStatusType.ASSIGNED, False),
        (TicketStatusType.IN_PROGRESS, True),
        (TicketStatusType.RESOLVED, True),
        (TicketStatusType.CLOSED, True),
    ],
)
def test_transition_from_assigned(new_status: TicketStatusType, expected: bool) -> None:
    # 検証
    assert can_status_transition(TicketStatusType.ASSIGNED, new_status) is expected


# current_status が「対応中」の場合、各 new_status に対する正しい結果を返す
@pytest.mark.parametrize(
    "new_status,expected",
    [
        (TicketStatusType.START, True),
        (TicketStatusType.ASSIGNED, True),
        (TicketStatusType.IN_PROGRESS, False),
        (TicketStatusType.RESOLVED, True),
        (TicketStatusType.CLOSED, True),
    ],
)
def test_transition_from_in_progress(new_status: TicketStatusType, expected: bool) -> None:
    # 検証
    assert can_status_transition(TicketStatusType.IN_PROGRESS, new_status) is expected


# current_status が「解決済み」の場合、各 new_status に対する正しい結果を返す
@pytest.mark.parametrize(
    "new_status,expected",
    [
        (TicketStatusType.START, False),
        (TicketStatusType.ASSIGNED, False),
        (TicketStatusType.IN_PROGRESS, True),
        (TicketStatusType.RESOLVED, False),
        (TicketStatusType.CLOSED, True),
    ],
)
def test_transition_from_resolved(new_status: TicketStatusType, expected: bool) -> None:
    # 検証
    assert can_status_transition(TicketStatusType.RESOLVED, new_status) is expected


# current_status が「クローズ」の場合、各 new_status に対する正しい結果を返す
@pytest.mark.parametrize(
    "new_status,expected",
    [
        (TicketStatusType.START, False),
        (TicketStatusType.ASSIGNED, False),
        (TicketStatusType.IN_PROGRESS, True),
        (TicketStatusType.RESOLVED, False),
        (TicketStatusType.CLOSED, False),
    ],
)
def test_transition_from_closed(new_status: TicketStatusType, expected: bool) -> None:
    # 検証
    assert can_status_transition(TicketStatusType.CLOSED, new_status) is expected
