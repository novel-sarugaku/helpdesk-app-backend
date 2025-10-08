from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Integer, String

# SQLAlchemy 2.0形式（最新）の書き方
# Mapped：カラムになるものであることを示す。mapped_column：カラムの条件を指定するもの。
from sqlalchemy.orm import Mapped, mapped_column

from helpdesk_app_backend.logic.calculate.calculate_datetime import get_now
from helpdesk_app_backend.models.db.base import Base


class UserType(PyEnum):
    STAFF = "staff"  # 社員
    SUPPORTER = "supporter"  # サポーター
    ADMIN = "admin"  # 管理者


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_type: Mapped[UserType] = mapped_column(
        Enum(UserType),
        nullable=False,
        index=True,  # 索引を張る指定。WHERE type='staff' のような絞り込み検索が速くなる
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_now, onupdate=get_now)
