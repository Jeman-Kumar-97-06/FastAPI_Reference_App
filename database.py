#This file handles the config and connection with database:
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLAL_DB_URL = 'sqlite:///./blog.db'

engine = create_engine(
    SQLAL_DB_URL,
    connect_args = {"check_same_thread":False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal as db:
        yield db