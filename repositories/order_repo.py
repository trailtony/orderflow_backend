import uuid
from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.order import Order, OrderStatus


async def create(session: AsyncSession, order: Order) -> Order:
    """Insert a new order into the database."""
    session.add(order)
    await session.flush()
    await session.refresh(order)
    return order


async def get_by_id(session: AsyncSession, order_id: uuid.UUID) -> Optional[Order]:
    """Fetch a single order by primary key."""
    result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    return result.scalar_one_or_none()


async def list_by_user(
    session: AsyncSession,
    user_id: uuid.UUID,
    *,
    status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Order]:
    """Return a paginated list of orders for a given user, optionally filtered by status."""
    stmt = select(Order).where(Order.user_id == user_id)
    if status is not None:
        stmt = stmt.where(Order.status == status)
    stmt = stmt.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_status(
    session: AsyncSession,
    order_id: uuid.UUID,
    new_status: OrderStatus,
) -> Optional[Order]:
    """Update the status of an existing order."""
    await session.execute(
        update(Order)
        .where(Order.id == order_id)
        .values(status=new_status)
    )
    await session.flush()
    return await get_by_id(session, order_id)


async def get_by_idempotency_key(
    session: AsyncSession,
    key: str,
) -> Optional[Order]:
    """Fetch an order by its idempotency key."""
    result = await session.execute(
        select(Order).where(Order.idempotency_key == key)
    )
    return result.scalar_one_or_none()
