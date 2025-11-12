# このファイルが読み込まれた瞬間に、本来型チェックも同時に行われるが、その時点ではチェックできずエラーになるため、
# 型チェックについては遅延させ、このファイル読み込みが完了した後に行うようにする設定
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, Integer, String

# SQLAlchemy 2.0形式（最新）の書き方
# Mapped：カラムになるものであることを示す。mapped_column：カラムの条件を指定するもの。
from sqlalchemy.orm import Mapped, mapped_column, relationship

from helpdesk_app_backend.logic.calculate.calculate_datetime import get_now
from helpdesk_app_backend.models.db.base import Base
from helpdesk_app_backend.models.enum.user import AccountType

# 型チェック専用にしたいときに使う
# 循環インポートはロジックを含むファイルを互いに読み込んだときに発生する
# 型のチェックを行いたいときだけ TYPE_CHECKING を使い、型のみであることを教え循環インポートを防ぐ
if TYPE_CHECKING:
    from helpdesk_app_backend.models.db.action import Action
    from helpdesk_app_backend.models.db.ticket import Ticket


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType),
        nullable=False,
        index=True,  # 索引を張る指定。WHERE type='staff' のような絞り込み検索が速くなる
    )
    is_suspended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_now, onupdate=get_now)

    # relationship(): テーブル間のリレーションシップを定義
    # back_populates: 双方向のリレーションシップを定義するために使用
    # Userから見てTicketは複数あるため list[Ticket] とする
    staff_tickets: Mapped[list[Ticket]] = relationship(
        foreign_keys="Ticket.staff_id", back_populates="staff"
    )
    supporter_tickets: Mapped[list[Ticket]] = relationship(
        foreign_keys="Ticket.supporter_id", back_populates="supporter"
    )
    actions: Mapped[list[Action]] = relationship(
        "Action",
        foreign_keys="Action.action_user_id", back_populates="action_user"
    )
