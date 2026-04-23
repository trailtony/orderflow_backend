import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.payment import Payment


async def create(session: AsyncSession, payment: Payment) -> Payment:
    """Insert a new payment into the database."""
    session.add(payment)
    await session.flush()
    await session.refresh(payment)
    return payment


async def get_by_order_id(
    session: AsyncSession,
    order_id: uuid.UUID,
) -> Sequence[Payment]:
    """Fetch all payments for a given order."""
    result = await session.execute(
        select(Payment)
        .where(Payment.order_id == order_id)
        .order_by(Payment.created_at.desc())
    )
    return result.scalars().all()


async def get_by_transaction_id(
    session: AsyncSession,
    transaction_id: str,
) -> Optional[Payment]:
    """Fetch a single payment by its unique transaction ID."""
    result = await session.execute(
        select(Payment).where(Payment.transaction_id == transaction_id)
    )
    return result.scalar_one_or_none()
