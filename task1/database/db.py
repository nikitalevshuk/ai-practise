from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


from task1.config import db_settings


async_engine = create_async_engine(db_settings.DATABASE_URL_asyncpg)

session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

class Base(DeclarativeBase):
    """
    Этот класс будет хранить в себе данные о созданных моделях
    """
    pass


