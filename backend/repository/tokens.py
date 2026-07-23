from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import UserTokens
import uuid
from datetime import datetime

async def add_access_and_refresh_tokens(
        db: AsyncSession,
        id: uuid.UUID,
        user_id: uuid.UUID,
        access_token: str,
        refresh_token: str,
        access_token_expires_at: datetime,
        refresh_token_expires_at: datetime,
        device_info: str | None,
        is_revoked: bool
        ):

    try:
        tokens = UserTokens(
            id=id,
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_at=access_token_expires_at,
            refresh_token_expires_at=refresh_token_expires_at,
            device_info=device_info,
            is_revoked=is_revoked
        )

        db.add(tokens)
        await db.commit()
        await db.refresh(tokens)
        print("Tokens added to DB")
    except Exception as E:
        print(f"Tokens Not Added to DB: {E}")



async def update_access_and_expiry(db: AsyncSession, refresh_token: str, new_token: str, new_expiry: datetime):
    try:
        stmt = (
            update(UserTokens)
            .where(UserTokens.refresh_token == refresh_token)
            .values(
                access_token=new_token,
                access_token_expires_at=new_expiry
            )
        )
        await db.execute(stmt)
        await db.commit()
        print("New Token Updated")
    except Exception as e:
        print(f"Token update failed: {e}")