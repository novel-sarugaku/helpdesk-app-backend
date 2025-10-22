from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.response.v1.account import GetAccountResponse
from helpdesk_app_backend.models.response.v1.healthcheck import HealthcheckAuthResponse
from helpdesk_app_backend.repositories.user import get_users_all

router = APIRouter()


@router.get("")
def get_accounts(
    # Depends(関数) → この関数を呼ぶ前に、()内の関数を実行
    session: Annotated[Session, Depends(get_db)],
    # トークンの確認し、問題なければ get_accounts 実行
    _: Annotated[HealthcheckAuthResponse, Depends(validate_access_token)],
) -> list[GetAccountResponse]:
    accounts = get_users_all(session)

    return [
        GetAccountResponse(
            id=account.id,
            name=account.name,
            email=account.email,
            account_type=account.account_type,
        )
        # accounts の中から、1つずつ順番に account に入れる
        for account in accounts
    ]
