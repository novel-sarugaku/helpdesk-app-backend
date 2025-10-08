# ユーザー取得とパスワードのハッシュ化・照合 を行うサービス

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from helpdesk_app_backend.models.db.user import User

# CryptContext(...) → パスワードハッシュの設定（どの方式を使うか等）
# schemes=["bcrypt"] → 使うハッシュ方式は bcrypt だけにするという指定
# deprecated="auto" → 将来ほかの方式を追加したとき、新規ハッシュは先頭の方式（bcrypt）だけを使い、他方式は非推奨扱いにする設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# パスワードを安全に変換して保存用にする（生パスワードを bcrypt でハッシュにする）
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ログイン時にパスワードを確認する（入力された生パスと、DBにあるハッシュが一致するかをチェック）
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# そのメールアドレスのユーザーをDBから1人探して返す（見つからなければ None）
class UserService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()
