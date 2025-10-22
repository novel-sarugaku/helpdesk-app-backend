from unittest.mock import Mock

import pytest

from fastapi.testclient import TestClient

import helpdesk_app_backend.core.check_token as check_token

from helpdesk_app_backend.models.enum.user import AccountType

BASE_URL = "/api/v1/healthcheck"


def test_healthcheck(test_client: TestClient) -> None:
    # 実行
    response = test_client.get(BASE_URL)

    # 検証
    assert response.json() == "success"
    assert response.status_code == 200


# validate_access_token を返す
def test_auth_healthcheck_returns_validate_result(
    test_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_account_type_response = Mock(return_value={"account_type": AccountType.ADMIN.value})
    monkeypatch.setattr(
        check_token,
        "verify_access_token",
        mock_account_type_response,
    )

    test_client.cookies.set("access_token", "dummy.jwt")

    # 実行
    response = test_client.get(f"{BASE_URL}/auth")

    # 検証
    assert response.status_code == 200
    assert response.json() == {"account_type": AccountType.ADMIN.value}
    # validate_access_token が1回呼ばれ、引数は正しいか確認
    mock_account_type_response.assert_called_once_with("dummy.jwt")
