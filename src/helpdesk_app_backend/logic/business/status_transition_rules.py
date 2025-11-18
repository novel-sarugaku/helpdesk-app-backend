from helpdesk_app_backend.models.enum.ticket import TicketStatusType


def can_status_transition(current_status: TicketStatusType, new_status: TicketStatusType) -> bool:
    TRANSITION_RULES = {
        # 現在のステータスが「新規質問」のとき
        TicketStatusType.START: [TicketStatusType.ASSIGNED],
        # 現在のステータスが「担当割り当て済み」のとき
        TicketStatusType.ASSIGNED: [
            TicketStatusType.START,
            TicketStatusType.IN_PROGRESS,
            TicketStatusType.RESOLVED,
            TicketStatusType.CLOSED,
        ],
        # 現在のステータスが「対応中」のとき
        TicketStatusType.IN_PROGRESS: [
            TicketStatusType.START,
            TicketStatusType.ASSIGNED,
            TicketStatusType.RESOLVED,
            TicketStatusType.CLOSED,
        ],
        # 現在のステータスが「解決済み」のとき
        TicketStatusType.RESOLVED: [
            TicketStatusType.IN_PROGRESS,
            TicketStatusType.CLOSED,
        ],
        # 現在のステータスが「クローズ」のとき
        TicketStatusType.CLOSED: [
            TicketStatusType.IN_PROGRESS,
        ],
    }

    return new_status in TRANSITION_RULES[current_status]
