from collections.abc import Iterator

import pytest

from fastapi.testclient import TestClient

from helpdesk_app_backend.core.check_token import validate_access_token
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
def override_validate_access_token() -> Iterator[None]:
    # 有効なトークンを持っている程
    def _fake_validate_access_token() -> HealthcheckAuthResponse:
        return HealthcheckAuthResponse(account_type=AccountType.ADMIN)

    app.dependency_overrides[validate_access_token] = _fake_validate_access_token

    yield

    app.dependency_overrides.pop(validate_access_token, None)


# 使用ライブラリ：TestClient（FastAPI標準）
# FastAPIアプリのエンドポイントをテストコードから呼び出すためのクライアント
@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)
