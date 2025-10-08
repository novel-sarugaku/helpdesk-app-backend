# ログイン用の入力とトークンの出力・中身を表す認証用Pydanticスキーマを定義するファイル

from pydantic import BaseModel, EmailStr, Field


# ログインAPIの入力フォーム（型と必須チェック）
class UserLogin(BaseModel):
    # email はメール形式の文字列じゃないとNG。 ... は必須。description はSwaggerの説明文に出る
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")

# クライアントに返す「ログイン成功の証明書（トークン）」の形
class Token(BaseModel):
    access_token: str # 実際のトークン（JWT）。超長い英数字、これが「ログイン済み」の証拠になる
    token_type: str = "bearer" # トークンの種類。常に "bearer" を使う


# サーバー側でJWTを解読したあと、アプリ内で使う最低限の情報
class TokenData(BaseModel):
    email: str | None = None # トークンの中から取り出したユーザーのメール。取れなければ None
