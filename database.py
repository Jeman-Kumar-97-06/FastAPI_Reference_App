#This file handles the config and connection with database:
# from sqlalchemy import create_engine
# from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# SQLAL_DB_URL = 'sqlite:///./blog.db'
SQLAL_DB_URL='sqlite+aiosqlite:///./blog.db'

#engine = create_engine(SQLAL_DB_URL, connect_args = {"check_same_thread":False},)
engine=create_async_engine(SQLAL_DB_URL, connect_args={"check_same_thread":False})

#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    with AsyncSessionLocal as session:
        yield session