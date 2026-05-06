#This file tells what to store and the structure of 'how to store':
from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

#
class User(Base):
    __tablename__='users' #table name in DB = 'users'
    id:         Mapped[int]        = mapped_column(Integer, primary_key=True, index=True)
    username:   Mapped[str]        = mapped_column(String(50), unique=True, nullable=False)
    email:      Mapped[str]        = mapped_column(String(120), unique=True, nullable=False)
    image_file: Mapped[str|None]   = mapped_column(String(200), nullable=True, default=None)
    #This 'posts' field doesn't actually exist in the table.
    #This line just creates a relationship.You can access shit like 'user.posts'
    #The reason 'users' find 'user_id' in 'posts' the table as a magic link is bcoz we added 'Foreign Key' that links it to 'id' in this table.
    posts:      Mapped[list[Post]] = relationship(back_populates="author")

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f'/media/pics/{self.image_file}'
        return '/static/pics/default.jpg'
    

class Post(Base):
    __tablename__='posts' #table name in DB = 'posts'
    id:          Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    title:       Mapped[str]         = mapped_column(String(100), nullable=False)
    content:     Mapped[str]         = mapped_column(Text, nullable=False)
    user_id:     Mapped[int]         = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    date_posted: Mapped[datetime]    = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC))
    author:      Mapped[User]        = relationship(back_populates='posts')