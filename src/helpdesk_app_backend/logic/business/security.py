from jose import jwt
from passlib.context import CryptContext

from helpdesk_app_backend.core.auth import ALGORITHM, SECRET_KEY


# パスワード制約確認
def validate_password(password: str) -> None:
    # any(...) → 1つでも条件を満たす要素があれば True、not any(...) → 大文字/数字が1つもないときに True
    # .isupper() → その文字が大文字かどうかを判定するメソッド
    # .isdigit() → その文字が数字かどうかを判定するメソッド
    # for char in password → password の中の1文字ずつを char に入れて順番に見る
    if not any(char.isupper() for char in password):
        raise ValueError("パスワードには大文字を1文字以上含めてください")
    if not any(char.isdigit() for char in password):
        raise ValueError("パスワードには数字を1文字以上含めてください")


# CryptContext(...) → パスワードハッシュの設定（どの方式を使うか等）
# schemes=["bcrypt"] → 使うハッシュ方式は bcrypt だけにするという指定
# deprecated="auto" → 将来ほかの方式を追加したとき、新規ハッシュは先頭の方式（bcrypt）だけを使い、他方式は非推奨扱いにする設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# パスワードを安全に変換して保存用にする（生パスワードを bcrypt でハッシュにする）
def trans_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ログイン時にパスワードを確認する（入力された生パスと、DBにあるハッシュが一致するかをチェック）
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# トークン作成
def create_access_token(payload: dict) -> str:
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# トークン検証
def verify_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
