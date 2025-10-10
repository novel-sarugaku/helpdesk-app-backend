
from sqlalchemy.orm import Session

from helpdesk_app_backend.models.db.user import User


# email情報からユーザー取得する
def get_user_by_email(session: Session, email: str) -> User:
    return session.query(User).filter(User.email == email).first()
