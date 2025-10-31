from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.exceptions.business_exception import (
    BusinessException,
)
from helpdesk_app_backend.exceptions.forbidden_exception import ForbiddenException
from helpdesk_app_backend.logic.business.security import trans_password_hash
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.db.user import User
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.request.v1.admin.account import (
    CreateAccountRequest,
    UpdateAccountRequest,
)
from helpdesk_app_backend.models.response.v1.admin.account import (
    CreateAccountResponse,
    GetAccountResponseItem,
    UpdateAccountResponse,
)
from helpdesk_app_backend.repositories.user import get_user_by_email, get_user_by_id, get_users_all

router = APIRouter()


# Annotated[指定したい型, 関数]
# 例：Annotated は Depends(関数)で返されたレスポンス（アカウントタイプ）を、AccountType にする役割
# 管理者以外のアカウントタイプの場合
def check_account(
    current_account_type: AccountType,
) -> None:
    if current_account_type != AccountType.ADMIN:
        raise ForbiddenException("アクセス権限がありません")


@router.get("")
def get_accounts(
    # Depends(関数) → この関数を呼ぶ前に、()内の関数を実行
    session: Annotated[Session, Depends(get_db)],
    # トークンの確認し、問題なければ get_accounts 実行
    access_token: Annotated[dict, Depends(validate_access_token)],
) -> list[GetAccountResponseItem]:
    account_type = AccountType(access_token.get("account_type"))

    check_account(account_type)

    accounts = get_users_all(session)

    return [
        GetAccountResponseItem(
            id=account.id,
            name=account.name,
            email=account.email,
            account_type=account.account_type,
            is_suspended=account.is_suspended,
        )
        # accounts の中から、1つずつ順番に account に入れる
        for account in accounts
    ]


@router.post("")
def create_account(
    body: CreateAccountRequest,
    session: Annotated[Session, Depends(get_db)],
    access_token: Annotated[dict, Depends(validate_access_token)],
) -> CreateAccountResponse:
    account_type = AccountType(access_token.get("account_type"))

    check_account(account_type)

    if get_user_by_email(session, body.email) is not None:
        raise BusinessException("すでに存在するメールアドレスです")

    if body.account_type == AccountType.ADMIN:
        raise BusinessException("管理者アカウントは作成できません")

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
        is_suspended=new_account.is_suspended,
    )


@router.put("")
def update_account(
    body: UpdateAccountRequest,
    session: Annotated[Session, Depends(get_db)],
    access_token: Annotated[dict, Depends(validate_access_token)],
) -> UpdateAccountResponse:
    account_type = AccountType(access_token.get("account_type"))

    check_account(account_type)

    target_account = get_user_by_id(session, id=body.id)

    if target_account is None:
        raise BusinessException("指定したアカウントが存在しません")

    if target_account.account_type == AccountType.ADMIN:
        raise BusinessException("管理者アカウントの利用状態は変更できません")

    target_account.is_suspended = body.is_suspended

    try:
        session.commit()
    except Exception as error:
        session.rollback()
        raise error

    return UpdateAccountResponse(
        id=target_account.id,
        name=target_account.name,
        email=target_account.email,
        account_type=target_account.account_type,
        is_suspended=target_account.is_suspended,
    )
