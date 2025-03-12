from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from task1.database.models import User

async def create_user(
        db: AsyncSession,
        user_id: str,
):

    new_user = User(
        telegram_user_id=user_id,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_by_telegram_id(
        db: AsyncSession,
        telegram_user_id: str
):
    stmt = select(User).where(User.telegram_user_id == telegram_user_id)
    result= await db.execute(stmt)
    return result.scalars().first()



