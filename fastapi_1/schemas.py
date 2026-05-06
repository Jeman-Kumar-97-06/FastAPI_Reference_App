'''
This file is for data validation.
This file says : What format of 'Post' should i expect from client side and What format of response to send.
'''

from pydantic import BaseModel, ConfigDict, Field

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