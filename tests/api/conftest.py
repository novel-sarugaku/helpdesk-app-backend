from collections.abc import Iterator

import pytest

from fastapi.testclient import TestClient

from helpdesk_app_backend.main import app
from helpdesk_app_backend.models.db.base import get_db


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


# 使用ライブラリ：TestClient（FastAPI標準）
# FastAPIアプリのエンドポイントをテストコードから呼び出すためのクライアント
@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)
