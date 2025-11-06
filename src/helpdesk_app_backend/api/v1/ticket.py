from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.exceptions.forbidden_exception import ForbiddenException
from helpdesk_app_backend.exceptions.unauthorized_exception import UnauthorizedException
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.db.ticket import Ticket
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.internal.token_payload import AccessTokenPayload
from helpdesk_app_backend.models.request.v1.ticket import CreateTicketRequest
from helpdesk_app_backend.models.response.v1.ticket import (
    CreateTicketResponse,
    GetTicketResponseItem,
)
from helpdesk_app_backend.repositories.ticket import get_tickets_all
from helpdesk_app_backend.repositories.user import get_user_by_id

router = APIRouter()


# 社員以外のアカウントタイプの場合
def check_account(
    current_account_type: AccountType,
) -> None:
    if current_account_type != AccountType.STAFF:
        raise ForbiddenException("社員でないためチケットの登録はできません")


@router.get("")
def get_tickets(
    session: Annotated[Session, Depends(get_db)],
    access_token: Annotated[AccessTokenPayload, Depends(validate_access_token)],
) -> list[GetTicketResponseItem]:
    all_tickets = get_tickets_all(session)

    account_type = access_token.account_type
    user_id = access_token.user_id

    target_account = get_user_by_id(session, id=user_id)

    # アカウントが停止状態（is_suspended=True）の場合
    if target_account.is_suspended:
        raise UnauthorizedException("このアカウントは停止中です")

    # アカウントタイプが「社員」以外の場合
    target_tickets = all_tickets

    # アカウントタイプが「社員」の場合
    if account_type == AccountType.STAFF:
        # 以下のパターンでも同様に表現することが可能
        # not_target_tickets = list(
        #     filter(lambda ticket: not ticket.is_public and ticket.staff_id != user_id, all_tickets)
        # )
        # # set = 集合（ベン図）という概念 listからsetに変換して計算してから、setからlistに変換
        # target_tickets = list(set(all_tickets) - set(not_target_tickets))

        target_tickets = list(
            filter(lambda ticket: ticket.staff_id == user_id or ticket.is_public, all_tickets)
        )

    return [
        GetTicketResponseItem(
            id=target_ticket.id,
            title=target_ticket.title,
            is_public=target_ticket.is_public,
            status=target_ticket.status,
            staff=target_ticket.staff.name,
            supporter=target_ticket.supporter.name if target_ticket.supporter else None,
            created_at=target_ticket.created_at,
        )
        for target_ticket in target_tickets
    ]


@router.post("")
def create_ticket(
    body: CreateTicketRequest,
    session: Annotated[Session, Depends(get_db)],
    access_token: Annotated[AccessTokenPayload, Depends(validate_access_token)],
) -> CreateTicketResponse:
    account_type = access_token.account_type
    user_id = access_token.user_id

    check_account(account_type)

    new_ticket = Ticket(
        title=body.title,
        is_public=body.is_public,
        description=body.description,
        staff_id=user_id,
    )

    session.add(new_ticket)

    try:
        session.commit()
    except Exception as error:
        session.rollback()
        raise error

    return CreateTicketResponse(
        id=new_ticket.id,
        title=new_ticket.title,
        is_public=new_ticket.is_public,
        status=new_ticket.status,
        description=new_ticket.description,
        staff=new_ticket.staff_id,
        created_at=new_ticket.created_at,
    )
