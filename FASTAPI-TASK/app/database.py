from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

URL_DATABASE='postgresql+asyncpg://postgres:123@127.0.0.1:5432/fastapi-db'

engine = create_async_engine(URL_DATABASE, echo=True)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base=declarative_base()
