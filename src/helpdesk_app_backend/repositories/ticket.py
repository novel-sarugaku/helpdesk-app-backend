from sqlalchemy.orm import Session

from helpdesk_app_backend.models.db.ticket import Ticket


# 全チケットを取得する
def get_tickets_all(session: Session) -> list[Ticket]:
    return session.query(Ticket).all()

# 指定したIDのチケット情報を取得
def get_ticket_by_id(session: Session, id: int) -> Ticket:
    return session.query(Ticket).where(Ticket.id == id).first()
