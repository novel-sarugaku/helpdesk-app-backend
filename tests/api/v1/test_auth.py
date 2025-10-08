import pytest  # pytest本体(テスト用ライブラリ)

from fastapi import HTTPException
from fastapi.testclient import TestClient  # FastAPIが用意しているテスト専用のクライアント

import helpdesk_app_backend.api.v1.auth as api_auth

from helpdesk_app_backend.main import app  # アプリ本体(FastAPIで作ったインスタンス)を読み込み

client = TestClient(app)  # 読み込んだappを渡して、擬似的なHTTPクライアントを作成


# ログインテスト（成功）
# /api/v1/auth/login に正しい入力を送ったとき、200 とトークンが返る
@pytest.mark.usefixtures("override_get_db")
def test_login_success(monkeypatch: pytest.MonkeyPatch) -> None:

    # 本物の AuthService.login_user(session, body) の代わりに使う関数
    def fake_login_user(_session: object, _body: object) -> dict[str, str]:
        return {"access_token": "testtoken", "token_type": "bearer"} # 成功時の想定レスポンス

    # monkeypatchで AuthService.login_user を上の偽関数に一時的に差し替え
    # 元の login_user は @staticmethod のため、置き換え側も staticmethod で包んで「self が要らないメソッド」の形にする。
    monkeypatch.setattr(api_auth.AuthService, "login_user", staticmethod(fake_login_user))

    body = {"email": "test@example.com", "password": "testP@ssw0rd"}

    # 実行
    response = client.post("/api/v1/auth/login", json=body)

    # 検証
    assert response.status_code == 200
    assert response.json() == {"access_token": "testtoken", "token_type": "bearer"}


# ログインテスト（失敗）
# /api/v1/auth/login に誤った入力を送ったとき、401 とメッセージが返る
@pytest.mark.usefixtures("override_get_db")
def test_login_unauthorized(monkeypatch: pytest.MonkeyPatch) -> None:
    # 401 を投げる偽関数
    def fake_login_user(_session: object, _body: object) -> None:
        raise HTTPException(
            status_code=401,
            detail="メールアドレスまたはパスワードが正しくありません",
        )

    monkeypatch.setattr(api_auth.AuthService, "login_user", staticmethod(fake_login_user))

    body = {"email": "failure@example.com", "password": "failure"}

    # 実行
    response = client.post("/api/v1/auth/login", json=body)

    # 検証
    assert response.status_code == 401
    assert response.json() == {"detail": "メールアドレスまたはパスワードが正しくありません"}


# ログアウトテスト
# /api/v1/auth/logout を送ったとき、204 が返る
def test_logout() -> None:
    # 実行
    response = client.post("/api/v1/auth/logout")

    # 検証
    assert response.status_code == 204
