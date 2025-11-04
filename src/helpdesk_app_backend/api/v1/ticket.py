from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.exceptions.unauthorized_exception import UnauthorizedException
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.internal.token_payload import AccessTokenPayload
from helpdesk_app_backend.models.response.v1.ticket import GetTicketResponseItem
from helpdesk_app_backend.repositories.ticket import get_tickets_all
from helpdesk_app_backend.repositories.user import get_user_by_id

router = APIRouter()


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
            supporter=target_ticket.supporter.name,
            created_at=target_ticket.created_at,
        )
        for target_ticket in target_tickets
    ]
