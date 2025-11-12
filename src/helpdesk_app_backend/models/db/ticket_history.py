from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from helpdesk_app_backend.logic.calculate.calculate_datetime import get_now
from helpdesk_app_backend.models.db.base import Base

if TYPE_CHECKING:
    from helpdesk_app_backend.models.db.ticket import Ticket
    from helpdesk_app_backend.models.db.user import User


class TicketHistory(Base):
    __tablename__ = "ticket_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    action_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    action_description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_now, onupdate=get_now)

    ticket: Mapped[Ticket] = relationship(
        "Ticket", foreign_keys=[ticket_id], back_populates="ticket_histories"
    )
    action_user: Mapped[User] = relationship(
        "User", foreign_keys=[action_user_id], back_populates="ticket_histories"
    )
