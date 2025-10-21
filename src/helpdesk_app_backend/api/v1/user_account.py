from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.response.v1.user_account import GetUserAccountResponse
from helpdesk_app_backend.repositories.user import get_user_account_all

router = APIRouter()


@router.get("")
def get_user_account(session: Annotated[Session, Depends(get_db)]) -> list[GetUserAccountResponse]:
    user_accounts = get_user_account_all(session)

    return [
        GetUserAccountResponse(
            id=user_account.id,
            name=user_account.name,
            email=user_account.email,
            account_type=user_account.account_type,
        )
        # user_accounts の中から、1つずつ順番に user_account に入れる
        for user_account in user_accounts
    ]
