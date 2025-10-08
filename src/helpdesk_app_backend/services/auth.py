# ログイン判定とJWTアクセストークンの発行・検証 を行うサービス

from datetime import UTC, datetime, timedelta

from fastapi import Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from helpdesk_app_backend.core.settings import settings
from helpdesk_app_backend.models.db.user import User
from helpdesk_app_backend.schemas.auth import TokenData, UserLogin
from helpdesk_app_backend.services.users import UserService, verify_password

# .env から読み込んだ設定を定数化
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


class AuthService:
    # @staticmethod → インスタンス（self）を作らずに AuthService.get_token_from_header(...)のように呼べる。
    @staticmethod
    # Authorizationヘッダー（"Bearer <token>"）から <token> 部分だけを取り出す関数
    # authorization: str | None = Header(None) → FastAPIの機能で、Authorization を自動で受け取る引数
    def get_token_from_header(authorization: str | None = Header(None)) -> str | None:
        # ヘッダーが無い、または"Bearer "で始まっていない（不正形式）なら None を返す
        if not authorization or not authorization.startswith("Bearer "):
            return None
        # 先頭の"Bearer "を削って、純粋なトークン文字列だけを返す
        return authorization.replace("Bearer ", "")

    @staticmethod
    # 入力されたメールとパスワードが正しいか確認し、正しければユーザー情報を返す・間違っていれば何も返さない関数
    def authenticate_user(db: Session, email: str, password: str) -> User | None:
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    @staticmethod
    # JWTアクセストークンを作って文字列で返す関数
    def create_access_token(data: dict) -> str:
        # いま（UTC）＋ ACCESS_TOKEN_EXPIRE_MINUTES（30分） = トークン有効期限を計算
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = data.copy()  # data（辞書）の控え作成
        payload.update({"exp": expire}) # payload（辞書）に有効期限を追加
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) # payload を秘密鍵で署名して、HTTP で送れるJWT文字列にする

    @staticmethod
    # 受け取ったJWTが正しいか確かめて中身を取り出し、OKなら TokenData を返す関数
    def verify_token(token: str) -> TokenData | None:
        try:
            # 受け取った JWT 文字列 token を、秘密鍵と方式を使って、検証つきで中身（payload）に戻す
            # jwt.decode() → 署名が SECRET_KEY で作られたか（改竄されていないか）？期限が切れていないか？等チェック
            # algorithms=[ALGORITHM] → 許可する署名方式（'HS256'）を指定
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # JWTの中身から、"sub" というキーの値（=だれのトークンか）を取り出す
            sub = payload.get("sub")
            # 取り出した sub が文字列なら TokenData(email=sub) を作って返す
            if not isinstance(sub, str):
                return None
            return TokenData(email=sub)
        # jwt.decode() で、署名不一致／期限切れ／壊れたトークンなどの問題があれば JWTError が発生
        except JWTError:
            return None

    @staticmethod
    # メール＋パスワードをチェックして、OKならJWTを発行してユーザー情報と一緒に返す。NGなら401エラーを返す関数
    def login_user(db: Session, user_login: UserLogin) -> dict:
        # 認証（メールが存在＆パスワード一致しているか確認）
        user = AuthService.authenticate_user(db, user_login.email, user_login.password)
        # NGなら 401 を返して終了
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # OKなら JWT を発行。payload に誰のトークンかを入れる
        access_token = AuthService.create_access_token(data={"sub": user.email})
        # クライアントに返すJSON（レスポンス本文）
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"id": user.user_id, "name": user.username, "email": user.email},
        }
