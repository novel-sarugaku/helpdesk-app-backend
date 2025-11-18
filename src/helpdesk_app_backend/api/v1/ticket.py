from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.exceptions.business_exception import BusinessException
from helpdesk_app_backend.exceptions.forbidden_exception import ForbiddenException
from helpdesk_app_backend.exceptions.unauthorized_exception import UnauthorizedException
from helpdesk_app_backend.logic.business.status_transition_rules import can_status_transition
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.db.ticket import Ticket
from helpdesk_app_backend.models.db.ticket_history import TicketHistory
from helpdesk_app_backend.models.enum.ticket import TicketStatusType
from helpdesk_app_backend.models.enum.user import AccountType
from helpdesk_app_backend.models.internal.token_payload import AccessTokenPayload
from helpdesk_app_backend.models.request.v1.ticket import (
    CreateTicketRequest,
    UpdateTicketStatusRequest,
)
from helpdesk_app_backend.models.response.v1.ticket import (
    CreateTicketResponse,
    GetTicketDetailResponse,
    GetTicketHistoryResponseItem,
    GetTicketResponseItem,
    UpdateTicketResponse,
)
from helpdesk_app_backend.repositories.ticket import get_ticket_by_id, get_tickets_all
from helpdesk_app_backend.repositories.ticket_history import get_ticket_histories_by_ticket_id
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
    account_type = access_token.account_type
    user_id = access_token.user_id

    target_account = get_user_by_id(session, id=user_id)

    # アカウントが存在しない または 停止状態（is_suspended=True）の場合
    if target_account is None or target_account.is_suspended:
        raise UnauthorizedException("このアカウント情報は不正です")

    all_tickets = get_tickets_all(session)

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


@router.get("/{ticket_id}")
def get_ticket_detail(
    ticket_id: int,
    session: Annotated[Session, Depends(get_db)],
    access_token: Annotated[AccessTokenPayload, Depends(validate_access_token)],
) -> GetTicketDetailResponse:
    account_type = access_token.account_type
    user_id = access_token.user_id

    # アカウント情報取得
    target_account = get_user_by_id(session, id=user_id)

    # アカウントが存在しない または 停止状態（is_suspended=True）の場合
    if target_account is None or target_account.is_suspended:
        raise UnauthorizedException("このアカウント情報は不正です")

    # チケット情報取得
    target_ticket = get_ticket_by_id(session, id=ticket_id)

    # 存在しないチケットを取得しようとした場合
    if target_ticket is None:
        raise BusinessException("指定したチケットは存在しません")

    # アカウントタイプがサポート担当者であり、チケットの担当である場合
    is_own_ticket = bool(
        account_type == AccountType.SUPPORTER and target_ticket.supporter_id == user_id
    )

    # 社員が他人の非公開チケットを取得しようとした場合
    if (
        account_type == AccountType.STAFF
        and target_ticket.staff_id != user_id
        and not target_ticket.is_public
    ):
        raise ForbiddenException("他の社員の非公開チケットは閲覧できません")

    # 対応情報取得
    ticket_histories = get_ticket_histories_by_ticket_id(session, id=ticket_id)

    return GetTicketDetailResponse(
        id=target_ticket.id,
        title=target_ticket.title,
        is_public=target_ticket.is_public,
        status=target_ticket.status,
        description=target_ticket.description,
        supporter=target_ticket.supporter.name if target_ticket.supporter else None,
        created_at=target_ticket.created_at,
        is_own_ticket=is_own_ticket,
        ticket_histories=[
            GetTicketHistoryResponseItem(
                id=ticket_history.id,
                ticket=ticket_history.ticket_id,
                action_user=ticket_history.action_user.name if ticket_history.action_user else None,
                action_description=ticket_history.action_description,
                created_at=ticket_history.created_at,
            )
            for ticket_history in ticket_histories
        ],
    )


@router.post("")
def create_ticket(
    body: CreateTicketRequest,
    session: Annotated[Session, Depends(get_db)],
    access_token: Annotated[AccessTokenPayload, Depends(validate_access_token)],
) -> CreateTicketResponse:
    account_type = access_token.account_type
    user_id = access_token.user_id

    # アカウント情報取得
    target_account = get_user_by_id(session, id=user_id)

    # アカウントが存在しない または 停止状態（is_suspended=True）の場合
    if target_account is None or target_account.is_suspended:
        raise UnauthorizedException("このアカウント情報は不正です")

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


# [URLのパス設計]
# 「どのリソースに何をしたいか」がURLで表現されているのが望ましい
# 動詞を先頭に置いたり、動詞だけのパスは避ける
# 一般的な形「/リソース（複数形）/{リソースID}/状態を変える特別なアクション」
@router.put("/{ticket_id}/assign")
def assign_supporter(
    ticket_id: int,
    session: Annotated[Session, Depends(get_db)],
    access_token: Annotated[AccessTokenPayload, Depends(validate_access_token)],
) -> UpdateTicketResponse:
    account_type = access_token.account_type
    user_id = access_token.user_id

    # アカウントタイプがサポート担当者でない場合
    if account_type != AccountType.SUPPORTER:
        raise ForbiddenException("サポート担当者でないため、チケットの担当にはなれません")

    # アカウント情報取得
    target_account = get_user_by_id(session, id=user_id)

    # アカウントが存在しない または 停止状態（is_suspended=True）の場合
    if target_account is None or target_account.is_suspended:
        raise UnauthorizedException("このアカウント情報は不正です")

    # チケット情報取得
    target_ticket = get_ticket_by_id(session, id=ticket_id)

    # 存在しないチケットを取得しようとした場合
    if target_ticket is None:
        raise BusinessException("指定したチケットは存在しません")

    # すでにチケットのサポート担当者が存在する場合
    if target_ticket.supporter_id:
        raise BusinessException("すでにサポート担当者が存在します")

    # チケットのサポート担当者を更新
    target_ticket.supporter_id = user_id

    # ステータスが「新規質問」でない場合
    if target_ticket.status != TicketStatusType.START:
        raise Exception

    # 遷移不可のステータスに変更しようとした場合
    if not can_status_transition(target_ticket.status, TicketStatusType.ASSIGNED):
        raise BusinessException("選択したステータスには変更できません")

    # ステータスを「新規質問」から「担当者割り当て済み」に変更
    target_ticket.status = TicketStatusType.ASSIGNED

    # 対応履歴の追加
    new_ticket_history = TicketHistory(
        ticket_id=target_ticket.id,
        action_user_id=None,
        action_description=f"担当者 {target_account.name} を担当に割り当てました",
    )

    session.add(new_ticket_history)

    try:
        session.commit()
    except Exception as error:
        session.rollback()
        raise error

    # FEを意識した必要最低限のレスポンスにする(以下以外の変更内容はDBを確認)
    return UpdateTicketResponse(
        id=target_ticket.id,
        status=target_ticket.status,
        supporter=target_account.name,
    )


@router.put("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    body: UpdateTicketStatusRequest,
    session: Annotated[Session, Depends(get_db)],
    access_token: Annotated[AccessTokenPayload, Depends(validate_access_token)],
) -> UpdateTicketResponse:
    account_type = access_token.account_type
    user_id = access_token.user_id
    new_status = body.status

    # ステータスを「新規質問」に変更しようとした場合
    if new_status == TicketStatusType.START:
        raise BusinessException("「新規質問」には遷移できません")

    # アカウントタイプが社員（サポート担当者または管理者でない場合）の場合
    if account_type == AccountType.STAFF:
        raise ForbiddenException("社員のため、ステータスを変更することができません")

    # アカウント情報取得
    target_account = get_user_by_id(session, id=user_id)

    # アカウントが存在しない または 停止状態（is_suspended=True）の場合
    if target_account is None or target_account.is_suspended:
        raise UnauthorizedException("このアカウント情報は不正です")

    # チケット情報取得
    target_ticket = get_ticket_by_id(session, id=ticket_id)

    # 存在しないチケットを取得しようとした場合
    if target_ticket is None:
        raise BusinessException("指定したチケットは存在しません")

    # 現在のステータスが「新規質問」の場合、ステータス変更不可
    if target_ticket.status == TicketStatusType.START:
        raise BusinessException("現在のステータスからの変更はできません")

    # チケットの担当者が存在しない場合
    if target_ticket.supporter_id is None:
        raise BusinessException("担当者が設定されていません")

    # 権限がない（担当者でない、または管理者でない）アカウントがステータスを変更しようとした場合
    if not (
        (account_type == AccountType.ADMIN) or (target_ticket.supporter_id == target_account.id)
    ):
        raise ForbiddenException("ステータスを変更する権限がありません")

    # 遷移不可のステータスに変更しようとした場合
    if not can_status_transition(target_ticket.status, new_status):
        raise BusinessException("選択したステータスには変更できません")

    # 選択したステータスに変更
    target_ticket.status = new_status

    # 対応履歴の追加
    new_ticket_history = TicketHistory(
        ticket_id=target_ticket.id,
        action_user_id=user_id,
        action_description=f"ステータスを「{target_ticket.status.label_ja}」に変更しました",
    )

    session.add(new_ticket_history)

    try:
        session.commit()
    except Exception as error:
        session.rollback()
        raise error

    return UpdateTicketResponse(
        id=target_ticket.id,
        status=target_ticket.status,
        supporter=target_account.name,
    )
