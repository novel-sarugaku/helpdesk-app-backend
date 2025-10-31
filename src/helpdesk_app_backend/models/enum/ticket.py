from enum import Enum


class TicketStatusType(Enum):
    START = "start"  # 新規質問
    ASSIGNED = "assigned"  # 担当者割り当て済み
    IN_PROGRESS = "in_progress"  # 対応中
    RESOLVED = "resolved"  # 解決済み
    CLOSED = "closed"  # クローズ
