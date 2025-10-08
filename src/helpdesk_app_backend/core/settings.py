# .env から JWT設定を読み込んで、settings としてアプリ全体で使えるようにする設定ファイル

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # env_file=".env" → .env ファイル（KEY=VALUE形式）を読み込む
    # extra="ignore" → Settingsクラスに定義されていないキーは無視
    model_config = SettingsConfigDict(env_file="src/helpdesk_app_backend/.env", extra="ignore")

    # validation_alias で入力名（環境変数名）を指定
    # .env の SECRET_KEY を読み込んで settings.secret_key に入れる。
    secret_key: str = Field(..., validation_alias="SECRET_KEY")
    # .env の ALGORITHM があればそれ、なければ "HS256" を使う
    algorithm: str = Field("HS256", validation_alias="ALGORITHM")
    # .env の ACCESS_TOKEN_EXPIRE_MINUTES があればそれ、なければ 30 分を使う
    access_token_expire_minutes: int = Field(30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")


settings = Settings()  # pyright: ignore[reportCallIssue] Pylance（型チェッカー）の誤検知防止
