from sqlalchemy.orm import Session

from helpdesk_app_backend.models.db.ticket_history import TicketHistory


# チケットに紐づく対応履歴を取得する
def get_ticket_histories_by_ticket_id(session: Session, id: int) -> list[TicketHistory]:
    return session.query(TicketHistory).filter(TicketHistory.ticket_id == id).all()
