from sqlalchemy.orm import Session

from helpdesk_app_backend.models.db.user import User


# そのメールアドレスのユーザーを1人だけ取得する
def get_user_by_email(session: Session, email: str) -> User:
    return session.query(User).filter(User.email == email).first()


# ユーザーアカウントを取得する　.query()：参照するテーブルを指定　.all()：データすべて指定
def get_users_all(session: Session) -> list[User]:
    return session.query(User).all()
