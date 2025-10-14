from pydantic import BaseModel, EmailStr, Field


# ログインAPIの入力フォーム（型と必須チェック）
class LoginRequest(BaseModel):
    # email はメール形式の文字列じゃないとNG。 ... は必須。description はSwaggerの説明文に出る
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")
