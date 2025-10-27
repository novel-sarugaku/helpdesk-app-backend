from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.exceptions.forbidden_exception import ForbiddenException
from helpdesk_app_backend.exceptions.unprocessable_entity_exception import (
    UnprocessableEntityException,
)
from helpdesk_app_backend.logic.business.security import trans_password_hash
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.db.user import User
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.request.v1.account import CreateAccountRequest
from helpdesk_app_backend.models.response.v1.account import (
    CreateAccountResponse,
    GetAccountResponseItem,
)
from helpdesk_app_backend.repositories.user import get_user_by_email, get_users_all

router = APIRouter()


@router.get("")
def get_accounts(
    # Depends(関数) → この関数を呼ぶ前に、()内の関数を実行
    session: Annotated[Session, Depends(get_db)],
    # トークンの確認し、問題なければ get_accounts 実行
    current_acount_type: Annotated[AccountType, Depends(validate_access_token)],
) -> list[GetAccountResponseItem]:
    if current_acount_type != AccountType.ADMIN:
        raise ForbiddenException("アクセス権限がありません")

    accounts = get_users_all(session)

    return [
        GetAccountResponseItem(
            id=account.id,
            name=account.name,
            email=account.email,
            account_type=account.account_type,
        )
        # accounts の中から、1つずつ順番に account に入れる
        for account in accounts
    ]


@router.post("")
def create_account(
    body: CreateAccountRequest,
    session: Annotated[Session, Depends(get_db)],
    current_acount_type: Annotated[AccountType, Depends(validate_access_token)],
) -> CreateAccountResponse:
    if current_acount_type != AccountType.ADMIN:
        raise ForbiddenException("アクセス権限がありません")

    if get_user_by_email(session, body.email) is not None:
        raise UnprocessableEntityException("すでに存在するメールアドレスです")

    if body.account_type == AccountType.ADMIN:
        raise UnprocessableEntityException("管理者アカウントは作成できません")

    new_account = User(
        name=body.name,
        email=body.email,
        password=trans_password_hash(body.password),
        account_type=body.account_type,
    )

    session.add(new_account)

    try:
        session.commit()
    except Exception as error:
        session.rollback()
        raise error

    return CreateAccountResponse(
        id=new_account.id,
        name=new_account.name,
        email=new_account.email,
        account_type=new_account.account_type,
    )
