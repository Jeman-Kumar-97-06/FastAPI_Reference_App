from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPExcep

from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas import PostCreate, PostResponse

from typing import Annotated

import models
from database import Base, engine, get_db
from schemas import PostCreate, PostResponse, UserCreate, UserResponse

app = FastAPI()
app.mount('/static',StaticFiles(directory='static'))

temp_ = Jinja2Templates(directory='templates')

posts:list[dict] = [
    {"id":1, "author":"J1", "title":"post1", "content":"C1"},
    {"id":2, "author":"J2", "title":"post2", "content":"C2"},
    {"id":3, "author":"J3", "title":"post3", "content":"C3"}
] 

#API Routes : 
#GET : get all posts: /api/posts
@app.get("/api/posts",response_model=list[PostResponse])
def get_posts():
    return posts

#GET : get a post by id : /api/posts/{post_id} : 
@app.get('/api/posts/{post_id}',response_model=PostResponse)
def get_post(post_id:int):
    for post in posts:
        if post.get("id") == post_id:
            return post
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

#POST : create a new post: /api/posts : 
@app.post('/api/posts',response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post:PostCreate):
    new_id = max(p["id"] for p in posts)+1 if posts else 1
    new_post = {
        "id" : new_id,
        "author" : post.author,
        "title" : post.title,
        "content" : post.content,
        "date_posted" : "April 20, 2025"
    }

    posts.append(new_post)
    return new_post

#404 and Validation Error handlers: 
@app.exception_handler(RequestValidationError)
def validation_excep_handler(request:Request, exception: RequestValidationError):
    return temp_.TemplateResponse(request, "vError.html",{
        "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
        "title":status.HTTP_422_UNPROCESSABLE_CONTENT,
        "message":"Invalid Request, Please check input"
    },
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    )

@app.exception_handler(StarletteHTTPExcep)
def general_http_excep_handler(request:Request, exception: StarletteHTTPExcep):
    message = (exception.detail if exception.detail else "An Error occured. Check you request!")
    return temp_.TemplateResponse(request, '404.html', {
        "status_code":exception.status_code,
        "title": exception.status_code,
        "message":message
    },status_code=exception.status_code)