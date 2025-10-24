from collections.abc import Callable

import pytest

from fastapi.testclient import TestClient

from helpdesk_app_backend.models.enum.user import AccountType

BASE_URL = "/api/v1/healthcheck"


def test_healthcheck(test_client: TestClient) -> None:
    # 実行
    response = test_client.get(BASE_URL)

    # 検証
    assert response.json() == "success"
    assert response.status_code == 200


@pytest.mark.parametrize("account_type", [AccountType.ADMIN])
def test_auth_healthcheck_return_account_type(
    test_client: TestClient,
    override_validate_access_token: Callable[[AccountType], None],
    account_type: AccountType,
) -> None:
    override_validate_access_token(account_type)
    # 実行
    response = test_client.get(f"{BASE_URL}/auth")

    # 検証
    assert response.status_code == 200
    assert response.json() == {"account_type": "admin"}
