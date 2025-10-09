from dataclasses import dataclass  # テスト用の「ダミーのデータ型」を簡単に作るためのライブラリ

import pytest  # pytest本体(テスト用ライブラリ)

from fastapi.testclient import TestClient  # FastAPIが用意しているテスト専用のクライアント

import helpdesk_app_backend.api.v1.auth as api_auth

from helpdesk_app_backend.main import app  # アプリ本体(FastAPIで作ったインスタンス)を読み込み

client = TestClient(app)  # 読み込んだappを渡して、擬似的なHTTPクライアントを作成


@dataclass
class DummyAccountType:
    value: str


@dataclass
class DummyUser:
    id: int
    name: str
    email: str
    password: str  # ハッシュ済みとして扱う
    account_type: DummyAccountType


base = "/api/v1/auth"


# ログインテスト（成功）
@pytest.mark.usefixtures("override_get_db")
def test_login_success(monkeypatch: pytest.MonkeyPatch) -> None:
    # 本物の代わりに使う偽関数
    def fake_get_user_by_email(_session: object, email: str) -> DummyUser:
        return DummyUser(
            id=1,
            name="テストユーザー",
            email=email,
            password="hashedpass",
            account_type=DummyAccountType("admin"),
        )  # 成功時の想定レスポンス

    # 本物の代わりに使う偽関数
    def fake_verify_password(plain_password: str, hashed_password: str) -> bool:
        return True

    # 本物の代わりに使う偽関数
    def fake_create_access_token(payload: dict) -> str:
        return "dummy.jwt.token"

    # monkeypatchで AuthService.login_user を上の偽関数に一時的に差し替え
    monkeypatch.setattr(api_auth, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(api_auth, "verify_password", fake_verify_password)
    monkeypatch.setattr(api_auth, "create_access_token", fake_create_access_token)

    body = {"email": "test@example.com", "password": "testP@ssw0rd"}

    # 実行
    response = client.post(f"{base}/login", json=body)

    # 検証
    assert response.status_code == 204
    # アクセストークンが正しいかを確認（Cookie のうち access_token の値を取り出す）
    assert response.cookies.get("access_token") == "dummy.jwt.token"


# ログインテスト（失敗：ユーザーがいない）
@pytest.mark.usefixtures("override_get_db")
def test_login_user_not_foun(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get_user_by_email(_session: object, email: str) -> None:
        return None # 見つからない想定

    monkeypatch.setattr(api_auth, "get_user_by_email", fake_get_user_by_email)

    body = {"email": "notfoundtest@example.com", "password": "testP@ssw0rd"}

    # 実行
    response = client.post(f"{base}/login", json=body)

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "メールアドレスまたはパスワードが一致しません"}


# ログインテスト（失敗：パスワード不一致）
@pytest.mark.usefixtures("override_get_db")
def test_login_wrong_password(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get_user_by_email(_session: object, email: str) -> DummyUser:
        return DummyUser(
            id=1,
            name="テストユーザー",
            email=email,
            password="hashedpass",
            account_type=DummyAccountType("admin"),
        )

    def fake_verify_password(plain_password: str, hashed_password: str) -> bool:
        return False

    monkeypatch.setattr(api_auth, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(api_auth, "verify_password", fake_verify_password)

    body = {"email": "test@example.com", "password": "wrongtestP@ssw0rd"}

    # 実行
    response = client.post(f"{base}/login", json=body)

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "メールアドレスまたはパスワードが一致しません"}


# ログアウトテスト
def test_logout() -> None:
    # 疑似ログイン状態
    client.cookies.set("access_token", "dummy.jwt.token")

    # 実行
    response = client.post(f"{base}/logout")

    # 検証
    # Set-Cookie：サーバーがクッキーを保存・削除させるための応答ヘッダー
    # レスポンスの Set-Cookie ヘッダー文字列（無ければ空文字）に "access_token=" が含まれているかを確認
    assert "access_token=" in response.headers.get("set-cookie", "")
    assert response.status_code == 204
