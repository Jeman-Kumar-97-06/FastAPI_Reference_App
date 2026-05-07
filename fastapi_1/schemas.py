'''
This file is for data validation.
This file says : What format of 'Post' should i expect from client side and What format of response to send.
'''

from pydantic import BaseModel, ConfigDict, Field, EmailStr

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config=ConfigDict(from_attributes=True)
    id:int
    image_file:str | None
    image_path:str

class PostBase(BaseModel):
    title:str = Field(min_length=1, max_length=100)
    content:str = Field(min_length=1)
    author:str = Field(min_length=1, max_length=50)

#Post create format
class PostCreate(PostBase):
    pass

#What should client recieve when asking for a post:
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id:int
    date_posted:str