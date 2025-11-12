from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from helpdesk_app_backend.logic.calculate.calculate_datetime import get_now
from helpdesk_app_backend.models.db.base import Base
from helpdesk_app_backend.models.enum.ticket import TicketStatusType

if TYPE_CHECKING:
    from helpdesk_app_backend.models.db.action import Action
    from helpdesk_app_backend.models.db.user import User


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[TicketStatusType] = mapped_column(
        Enum(TicketStatusType), nullable=False, default=TicketStatusType.START
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    staff_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    supporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_now, onupdate=get_now)

    staff: Mapped[User] = relationship(
        "User", foreign_keys=[staff_id], back_populates="staff_tickets"
    )
    supporter: Mapped[User] = relationship(
        "User", foreign_keys=[supporter_id], back_populates="supporter_tickets"
    )

    # チケットから見てアクションは「多」のためlist
    actions: Mapped[list[Action]] = relationship(
        "Action", foreign_keys="Action.ticket_id", back_populates="ticket"
    )
