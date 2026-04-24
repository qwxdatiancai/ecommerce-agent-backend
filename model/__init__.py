import traceback

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import SQLModel

from core.settings import DbSettings
from model.experiment import ClusterExperiment
from model.user import User

engine = create_async_engine(DbSettings.MYSQL_URI, echo=False, future=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        try:
            await conn.run_sync(User.__table__.create)
        except:
            pass


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)
