import uuid
from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


async def create(session: AsyncSession, user: User) -> User:
    """Insert a new user into the database."""
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def get_by_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Fetch a single user by primary key."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Fetch a single user by email address."""
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def list_all(
    session: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[User]:
    """Return a paginated list of users."""
    result = await session.execute(
        select(User).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_user(
    session: AsyncSession,
    user_id: uuid.UUID,
    **fields,
) -> Optional[User]:
    """Update arbitrary fields on an existing user."""
    await session.execute(
        update(User).where(User.id == user_id).values(**fields)
    )
    await session.flush()
    return await get_by_id(session, user_id)


async def deactivate(session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Soft-delete a user by setting is_active to False."""
    return await update_user(session, user_id, is_active=False)
