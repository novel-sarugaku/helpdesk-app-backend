from sqlalchemy.orm import Session

from helpdesk_app_backend.models.db.ticket import Ticket


# 全チケットを取得する
def get_tickets_all(session: Session) -> list[Ticket]:
    return session.query(Ticket).all()
