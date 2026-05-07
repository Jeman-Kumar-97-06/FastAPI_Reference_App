from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StHTTPExcep

from schemas import PostCreate, PostResponse

from typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from schemas import PostCreate, PostResponse, UserCreate, UserResponse

Base.metadata.create_all(bind=engine)

#intialize "fastapi" app:
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/media', StaticFiles(directory='media'),name='media')

posts : list[dict] = [
    {"id":1, "author": "jk", "title":"post1", "content":"C1"},
    {"id":2, "author": "jk", "title":"post2", "content":"C2"},
    {"id":3, "author":"jk2", "title":"post3", "content":"C3"}
]

#'/api' route controller:
@app.get("/api")
def home():
    return {"message":"Hello!"}

#USER CONTROLLERS:
@app.post('/api/users',response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user:UserCreate, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.username==user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

#POST CONTROLLERS:
@app.get('/api/posts',response_model = list[PostResponse])
def get_posts():
    return posts

@app.post('/api/posts', response_model= PostResponse, status_code = status.HTTP_201_CREATED)
def create_post(post:PostCreate):
    new_id = max(p['id'] for p in posts) + 1 if posts else 1
    new_post = {
        "id":new_id,
        "author":post.author,
        "title":post.title,
        "content":post.content,
        "date_posted":"April 30, 2025"
    }
    posts.append(new_post)
    return new_post

@app.get('/api/posts/{post_id}',response_model=PostResponse)
def get_post(post_id:int):
    for p in posts:
        if p.get("id") == post_id:
            return p
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')


@app.exception_handler(StHTTPExcep)
def general_http_excep_handler(request:Request, exception: StHTTPExcep):
    message=(
        exception.detail if exception.detail else 'An Error Occured. Check your request.'
    )
    return JSONResponse(
        status_code = exception.status_code,
        content={'detail':message}
    )

@app.exception_handler(RequestValidationError)
def validation_excep_handler(request:Request, exception:RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_402_UNPROCESSABLE_CONTENT,
        content={'detail':exception.errors()}
    )

