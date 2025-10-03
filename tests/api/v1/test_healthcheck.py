from fastapi.testclient import TestClient

from helpdesk_app_backend.main import app

# 使用ライブラリ：TestClient（FastAPI標準）
# FastAPIアプリのエンドポイントをテストコードから呼び出すためのクライアント
client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/api/v1/healthcheck")

    assert response.json() == "テストOK"
    assert response.status_code == 200
