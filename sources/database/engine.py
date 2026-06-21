from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sources.database.models import Base
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent.parent
DATABASE_PATH = BASE_DIR / "dbfiles/database.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(f'sqlite+aiosqlite:///{DATABASE_PATH}', echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def initbaseandtables() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print(f"[DATABASE] Created base at {DATABASE_PATH}")
    except Exception as ex:
        print(f"Error: {ex}")

async def drop_db() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print("Drop DB!")
    except Exception as ex:
        print(f"Error: {ex}")