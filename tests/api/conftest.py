from collections.abc import Iterator

import pytest

from fastapi.testclient import TestClient

import helpdesk_app_backend.api.v1.account as api_account

from helpdesk_app_backend.main import app
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.response.v1.healthcheck import HealthcheckAuthResponse


# fixture：テストで毎回使う準備を自動でしてくれる仕組み
@pytest.fixture
def override_get_db() -> Iterator[None]:
    # 本来 get_db が返すはずのDBセッションの代わりに、適当なオブジェクトを返す関数を作成
    def _fake_db() -> Iterator[object]:
        yield object()

    app.dependency_overrides[get_db] = (
        _fake_db  # 本物の get_db を _fake_db に差し替え（実際のDBは使わない）
    )

    yield  # このフィクスチャを使ったテスト本体が実行される

    app.dependency_overrides.pop(get_db, None)  # 元の状態に戻す（差し替え解除）


@pytest.fixture
def override_auth_healthcheck() -> Iterator[None]:
    # 有効なトークンを持っている程
    def _fake_auth_healthcheck() -> HealthcheckAuthResponse:
        return HealthcheckAuthResponse(account_type=AccountType.ADMIN)

    app.dependency_overrides[api_account.auth_healthcheck] = _fake_auth_healthcheck

    yield

    app.dependency_overrides.pop(api_account.auth_healthcheck, None)


# 使用ライブラリ：TestClient（FastAPI標準）
# FastAPIアプリのエンドポイントをテストコードから呼び出すためのクライアント
@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)
