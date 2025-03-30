from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_DB, POSTGRES_EXTERNAL_PORT, POSTGRES_INTERNAL_PORT

DB_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:{POSTGRES_INTERNAL_PORT}/{POSTGRES_DB}'
ASYNC_DB_URL = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:{POSTGRES_INTERNAL_PORT}/{POSTGRES_DB}'



engine = create_engine(DB_URL)
session_maker = sessionmaker(engine, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with session_maker() as session:
        return session



async_engine = create_async_engine(ASYNC_DB_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
