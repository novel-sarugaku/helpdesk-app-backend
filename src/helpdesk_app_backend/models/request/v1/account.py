from pydantic import BaseModel, EmailStr, Field, field_validator

from helpdesk_app_backend.logic.business.security import validate_password
from helpdesk_app_backend.models.enum.user import AccountType


# アカウント追加（POST）
class CreateAccountRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    account_type: AccountType

    # Pydantic のモデルに、password用バリデーションを差し込む
    @field_validator("password")  # Pydantic が password を受け取った直後にこの関数が実行される
    @classmethod
    def password_check(cls, password: str) -> str:  # cls はクラス自身（CreateAccountRequest）を指す
        validate_password(password)  # パスワード制約確認
        return password  # 問題なければ、そのまま返す
