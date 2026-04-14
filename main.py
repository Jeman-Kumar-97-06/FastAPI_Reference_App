from fastapi import Depends,FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPExcep
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from sqlalchemy import select
from sqlalchemy.orm import Session

import models

from database import Base, engine, get_db
from schemas import PostCreate, PostResponse, UserCreate, UserResponse

from typing import Annotated

from schemas import PostCreate, PostResponse

'''
What the Following line does : 
    Create tables according to the models, incase if they don't exist
'''
Base.metadata.create_all(bind=engine)

app = FastAPI()

temp_ = Jinja2Templates(directory='templates')

app.mount('/static',StaticFiles(directory='static'),name='static')

app.mount('/media',StaticFiles(cirectory='media'),name='media')

posts:list[dict] = [
    {
        "id":1, 
        "author":"J1",
        "title":"T1",
        "content":"C1"
     },
    {
        "id":2,
        "author":"J2",
        "title":"T2",
        "content":"C2"
    }
]

#Home Route:
@app.get('/')
def home():
    return {"message":"Hello!"}

#USERS API ROUTES:
@app.post('/api/users',response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user:UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.username==user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    result = db.execute(select(models.User).where(models.User.email==user.email))
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already registered")
    new_user = models.User(
        username = user.username,
        email    = user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#POSTS API ROUTES:
#GET : /api/posts:
@app.get('/api/posts',response_model=list[PostResponse])
def get_posts():
    return posts

#POST : /api/posts:
@app.post('/api/posts',response_model=PostResponse,status_code=status.HTTP_201_CREATED)
def create_post(post:PostCreate):
    new_id = max(p['id'] for p in posts) + 1 if posts else 1
    new_post = {"id":new_id, "author":post.author, "title":post.title, "content":post.content, "date_posted":"April 30, 2025"}
    posts.append(new_post)
    return new_post

#GET : /api/posts/{post_id}:
@app.get('/api/posts/{post_id}',response_model=PostResponse)
def get_post(post_id:int):
    for p in posts:
        if p.get("id")==post_id:
            return p
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found!")


@app.get('/api/posts/{post_id}')
def get_post(post_id:int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Post not found!')


#Validation Error Handler:
@app.exception_handler(RequestValidationError)
def validation_excep_handler(request:Request, exception:RequestValidationError):
    # if request.url.path.startswith('/api'):
    #     return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,content={"detail":exception.errors()})
    return temp_.TemplateResponse(
        request,
        "vError.html",
        {
            "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message":"Invalid request, check input :("
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )

#404 error handler:
'''
The following route sends 404.html whenevee a non-existent api route is accessed.
THE FACT WHETHER THE ROUTE IS NON-EXISTENT IS DETECTED BY THE 'STARLETTE' WE IMPORTED.
IF THE NON-EXISTENT ROUTE STARTS WITH '/api', A RAW JSON RESPONSE IS GIVEN TO THE CLIENT,
IF THE NON-EXISTENT ROUTE STARTS WITHOUT '/api', A 404.HTML IS RECIEVED BY THE CLIENT
'''
@app.exception_handler(StarletteHTTPExcep)
def general_http_excep_handler(request:Request, exception:StarletteHTTPExcep):
    message=(exception.detail if exception.detail else "An error occured. Check ur request!")
    if request.url.path.startswith('/api'):
        return JSONResponse(
            status_code = exception.status_code,
            content={"detail":message}
        )
    
    return temp_.TemplateResponse(request, '404.html',{
        "status_code":exception.status_code,
        "title":exception.status_code,
        "message":message
    },status_code=exception.status_code)
