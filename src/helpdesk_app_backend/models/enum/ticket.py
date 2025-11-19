from enum import Enum


class TicketStatusType(Enum):
    START = "start"  # 新規質問
    ASSIGNED = "assigned"  # 担当者割り当て済み
    IN_PROGRESS = "in_progress"  # 対応中
    RESOLVED = "resolved"  # 解決済み
    CLOSED = "closed"  # クローズ

    # @property → クラスから値を返すことができるデコレーター
    @property
    def label_ja(self) -> str:
        return {
            TicketStatusType.START: "新規質問",
            TicketStatusType.ASSIGNED: "担当者割り当て済み",
            TicketStatusType.IN_PROGRESS: "対応中",
            TicketStatusType.RESOLVED: "解決済み",
            TicketStatusType.CLOSED: "クローズ",
        }[self]
