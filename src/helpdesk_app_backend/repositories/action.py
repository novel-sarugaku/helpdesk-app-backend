from sqlalchemy.orm import Session

from helpdesk_app_backend.models.db.action import Action


# チケットに紐づく対応情報を取得する
def get_actions_by_ticket_id(session: Session, id: int) -> list[Action]:
    return session.query(Action).filter(Action.ticket_id == id).all()
