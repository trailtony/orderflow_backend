import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List

from sqlalchemy import String, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database import Base

if TYPE_CHECKING:
    from models.user import User
    from models.payment import Payment


class OrderStatus(str, PyEnum):
    """Order status enumeration.

    Valid transitions:
        pending → confirmed → fulfilled
        pending → cancelled
        confirmed → cancelled
    """
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class Order(Base):
    """Order model representing customer orders."""
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False, length=50),
        default=OrderStatus.PENDING,
        nullable=False
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders", lazy="selectin")
    payments: Mapped[List["Payment"]] = relationship(back_populates="order", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status})>"