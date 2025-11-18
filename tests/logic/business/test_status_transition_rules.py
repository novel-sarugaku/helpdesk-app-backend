from helpdesk_app_backend.logic.business.status_transition_rules import can_status_transition
from helpdesk_app_backend.models.enum.ticket import TicketStatusType


# current_status が「新規質問」で、new_status が「担当割り当て済み」の場合 True を返す
def test_can_status_transition_start_to_assigned_returns_true() -> None:
    result = can_status_transition(TicketStatusType.START, TicketStatusType.ASSIGNED)
    # 検証
    assert result is True


# current_status が「新規質問」で、new_status が「新規質問、対応中、解決済み、クローズ」の場合 False を返す
def test_can_status_transition_start_to_invalid_statuses_returns_false() -> None:
    invalid_new_statuses = [
        TicketStatusType.START,
        TicketStatusType.IN_PROGRESS,
        TicketStatusType.RESOLVED,
        TicketStatusType.CLOSED,
    ]

    for invalid_new_status in invalid_new_statuses:
        result = can_status_transition(TicketStatusType.START, invalid_new_status)
        # 検証
        assert result is False


# current_status が「担当割り当て済み」で、new_status が「新規質問、対応中、解決済み、クローズ」の場合 True を返す
def test_can_status_transition_assigned_to_valid_statuses_returns_true() -> None:
    valid_new_statuses = [
        TicketStatusType.START,
        TicketStatusType.IN_PROGRESS,
        TicketStatusType.RESOLVED,
        TicketStatusType.CLOSED,
    ]

    for valid_new_status in valid_new_statuses:
        result = can_status_transition(TicketStatusType.ASSIGNED, valid_new_status)
        # 検証
        assert result is True


# current_status が「担当割り当て済み」で、new_status が「担当割り当て済み」の場合 False を返す
def test_can_status_transition_assigned_to_assigned_returns_false() -> None:
    result = can_status_transition(TicketStatusType.ASSIGNED, TicketStatusType.ASSIGNED)
    # 検証
    assert result is False


# current_status が「対応中」で、new_status が「新規質問、担当割り当て済み、解決済み、クローズ」の場合 True を返す
def test_can_status_transition_in_progress_to_valid_statuses_returns_true() -> None:
    valid_new_statuses = [
        TicketStatusType.START,
        TicketStatusType.ASSIGNED,
        TicketStatusType.RESOLVED,
        TicketStatusType.CLOSED,
    ]

    for valid_new_status in valid_new_statuses:
        result = can_status_transition(TicketStatusType.IN_PROGRESS, valid_new_status)
        # 検証
        assert result is True


# current_status が「対応中」で、new_status が「対応中」の場合 False を返す
def test_can_status_transition_in_progress_to_in_progress_returns_false() -> None:
    result = can_status_transition(TicketStatusType.IN_PROGRESS, TicketStatusType.IN_PROGRESS)
    # 検証
    assert result is False


# current_status が「解決済み」で、new_status が「対応中、クローズ」の場合 True を返す
def test_can_status_transition_resolved_to_valid_statuses_returns_true() -> None:
    valid_new_statuses = [
        TicketStatusType.IN_PROGRESS,
        TicketStatusType.CLOSED,
    ]

    for valid_new_status in valid_new_statuses:
        result = can_status_transition(TicketStatusType.RESOLVED, valid_new_status)
        # 検証
        assert result is True


# current_status が「解決済み」で、new_status が「新規質問、担当割り当て済み、解決済み」の場合 False を返す
def test_can_status_transition_resolved_to_invalid_statuses_returns_false() -> None:
    invalid_new_statuses = [
        TicketStatusType.START,
        TicketStatusType.ASSIGNED,
        TicketStatusType.RESOLVED,
    ]

    for invalid_new_status in invalid_new_statuses:
        result = can_status_transition(TicketStatusType.RESOLVED, invalid_new_status)
        # 検証
        assert result is False


# current_status が「クローズ」で、new_status が「対応中」の場合 True を返す
def test_can_status_transition_closed_to_in_progress_returns_true() -> None:
    result = can_status_transition(TicketStatusType.CLOSED, TicketStatusType.IN_PROGRESS)
    # 検証
    assert result is True


# current_status が「クローズ」で、new_status が「新規質問、担当割り当て済み、解決済み、クローズ」の場合 False を返す
def test_can_status_transition_closed_to_invalid_statuses_returns_false() -> None:
    invalid_new_statuses = [
        TicketStatusType.START,
        TicketStatusType.ASSIGNED,
        TicketStatusType.RESOLVED,
        TicketStatusType.CLOSED,
    ]

    for invalid_new_status in invalid_new_statuses:
        result = can_status_transition(TicketStatusType.CLOSED, invalid_new_status)
        # 検証
        assert result is False
