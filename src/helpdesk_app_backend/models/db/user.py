from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String

# SQLAlchemy 2.0形式（最新）の書き方
# Mapped：カラムになるものであることを示す。mapped_column：カラムの条件を指定するもの。
from sqlalchemy.orm import Mapped, mapped_column

from helpdesk_app_backend.logic.calculate.calculate_datetime import get_now
from helpdesk_app_backend.models.db.base import Base
from helpdesk_app_backend.models.enum.user import AccountType


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
