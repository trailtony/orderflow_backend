import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database import Base

if TYPE_CHECKING:
    from models.order import Order


class UserRole(str, PyEnum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """User model representing system users."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=50),
        default=UserRole.USER,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    orders: Mapped[List["Order"]] = relationship(back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
