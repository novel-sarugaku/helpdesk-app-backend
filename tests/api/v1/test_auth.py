from dataclasses import dataclass  # テスト用の「ダミーのデータ型」を簡単に作るためのライブラリ
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest  # pytest本体(テスト用ライブラリ)

from fastapi.testclient import TestClient  # FastAPIが用意しているテスト専用のクライアント
from sqlalchemy.orm import Session

import helpdesk_app_backend.api.v1.auth as api_auth

from helpdesk_app_backend.core.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from helpdesk_app_backend.models.enum.user import AccountType


@dataclass
class DummyUser:
    id: int
    name: str
    email: str
    password: str  # ハッシュ済みとして扱う
    account_type: AccountType


BASE_URL = "/api/v1/auth"


# 本物の代わりに使う偽の fake_get_user_by_email 関数（fixture 化したどのテストでも使えるグローバル関数）
@pytest.fixture
def fake_get_user_by_email(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake(_session: Session, email: str) -> DummyUser:
        return DummyUser(
            id=1,
            name="テストユーザー",
            email=email,
            password="hashedpass",
            account_type=AccountType.ADMIN,
        )

    monkeypatch.setattr(api_auth, "get_user_by_email", _fake)


# ログインテスト（成功）
# @pytest.mark.usefixturesに fixture の関数を書く場合 → fixture の値は使わず、差し替え・設定だけが目的の時
@pytest.mark.usefixtures("override_get_db_success", "fake_get_user_by_email")
# テスト引数に fixture の関数を書く場合 → テスト内で fixture の値を使う時
def test_login_success(test_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    body = {"email": "test@example.com", "password": "testP@ssw0rd"}
    current_time = datetime.now()
    expected_payload = {
        "sub": body["email"],
        "account_type": AccountType.ADMIN.value,
        "exp": current_time + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    # Mock / monkeypatch で偽関数に一時的に差し替え
    mock_create_access_token = Mock(return_value="dummy.jwt.token")
    monkeypatch.setattr(api_auth, "create_access_token", mock_create_access_token)
    monkeypatch.setattr(api_auth, "get_now_UTC", lambda: current_time)
    monkeypatch.setattr(api_auth, "verify_password", lambda plain_password, hashed_password: True)

    # 実行
    response = test_client.post(f"{BASE_URL}/login", json=body)

    # 検証
    assert response.status_code == 204
    # アクセストークンが正しいかを確認（Cookie のうち access_token の値を取り出す）
    assert response.cookies.get("access_token") == "dummy.jwt.token"
    # mock_create_access_token が1回呼ばれたかを確認
    mock_create_access_token.assert_called_once()
    # mock_create_access_token の引数が expected_payload と一致しているかを確認
    mock_create_access_token.assert_called_with(expected_payload)


# ログインテスト（失敗：ユーザーがいない）
@pytest.mark.usefixtures("override_get_db_error")
def test_login_user_not_foun(test_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_auth, "get_user_by_email", lambda _session, email: None)

    body = {"email": "notfoundtest@example.com", "password": "testP@ssw0rd"}

    # 実行
    response = test_client.post(f"{BASE_URL}/login", json=body)

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "メールアドレスまたはパスワードが一致しません"}


# ログインテスト（失敗：パスワード不一致）
@pytest.mark.usefixtures("override_get_db_error", "fake_get_user_by_email")
def test_login_wrong_password(test_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_auth, "verify_password", lambda plain_password, hashed_password: False)

    body = {"email": "test@example.com", "password": "wrongtestP@ssw0rd"}

    # 実行
    response = test_client.post(f"{BASE_URL}/login", json=body)

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "メールアドレスまたはパスワードが一致しません"}


# ログアウトテスト
def test_logout(test_client: TestClient) -> None:
    # 疑似ログイン状態
    test_client.cookies.set("access_token", "dummy.jwt.token")

    # 実行
    response = test_client.post(f"{BASE_URL}/logout")

    # 検証
    # Set-Cookie：サーバーがクッキーを保存・削除させるための応答ヘッダー
    # レスポンスの Set-Cookie ヘッダー文字列（無ければ空文字）に "access_token" が含まれているかを確認
    assert "access_token" not in response.cookies
    assert response.status_code == 204
