from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Users


async def get_all_users(db: AsyncSession) -> list[Users]:
    result = await db.execute(select(Users))
    return list(result.scalars().all())


async def get_user_username(username: str, db: AsyncSession) -> Users | None:
    result = await db.execute(select(Users).where(Users.username == username))
    return result.scalar_one_or_none()


async def get_user_email(email: str, db: AsyncSession) -> Users | None:
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()