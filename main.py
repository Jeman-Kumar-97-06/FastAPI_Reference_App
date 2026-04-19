from contextlib import asynccontextmanager
from fastapi.exception_handlers import (http_exception_handler, request_validation_exception_handler)

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPExcep

from sqlalchemy import select
#from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from schemas import PostCreate, PostResponse, PostUpdate

from typing import Annotated

import models
from database import Base, engine, get_db
from schemas import PostCreate, PostResponse, UserCreate, UserResponse, UserUpdate

from routers import posts, users

#Base.metadata.create_all(bind=engine)
'''
The @asynccontextmanager is used to define the lifespan for the FastAPI application.
it manages the setup and teardown processes : Specifically for DBs.
App Startup : shit that comes before 'yield'.
'Yield' : Passes control to main untill all the shit is done.
App Shutdown : When the app is shutdown 'engine.dispose()' is executed.
'''
@asynccontextmanager
async def lifespan(_app:FastAPI):
    #Startup:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)#Connects to db or creates one if there's none
    yield
    #ShutDown:
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.mount('/static',StaticFiles(directory='static'))
app.mount('/media',StaticFiles(directory='media'),name='media')

temp_ = Jinja2Templates(directory='templates')

app.include_router(users.router, prefix='/api/users', tags=["users"])
app.include_router(posts.router, prefix='/api/posts', tags=["posts"])

#API Routes : 
# user ROUTES:
# POST : create user : /api/users : 
# @app.post('/api/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# # def create_user(user:UserCreate, db:Annotated[Session, Depends(get_db)]):
# #     result = db.execute(select(models.User).where(models.User.username == user.username))
# #     existing_user = result.scalars().first()
# #     if existing_user:
# #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
# #     result = db.execute(select(models.User).where(models.User.email==user.email))
# #     existing_email = result.scalars().first()
# #     if existing_email:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Email already registered"
# #         )
# #     new_user = models.User(
# #         username=user.username,
# #         email   =user.email
# #     )

# #     db.add(new_user)
# #     db.commit()
# #     db.refresh(new_user)
# #     return new_user
# async def create_user(user:UserCreate, db:Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.User).where(models.User.username == user.username))
#     existing_user = res.scalars().first()
#     if existing_user:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exists')
#     res = await db.execute(select(models.User).where(models.User.email==user.email))
#     existing_email = res.scalars().first()
#     if existing_email:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
#     new_user = models.User(
#         username = user.username,
#         email = user.email
#     )
#     db.add(new_user)
#     await db.commit()
#     await db.refresh(new_user)
#     return new_user


# #GET : user data/ login : /api/users/{user_id} : 
# @app.get('/api/users/{user_id}', response_model=UserResponse)
# # def get_user(user_id:int, db:Annotated[Session, Depends(get_db)]):
# #     result = db.execute(select(models.User).where(models.User.id == user_id))
# #     user = result.scalars().first()
# #     if user:
# #         return user
# #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
# async def get_use(user_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.User).where(models.User.id==user_id))
#     user = res.scalars().first()
#     if user:
#         return user
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

# #GET : posts by user_id: /api/users/{user_id}/posts:
# @app.get('/api/users/{user_id}/posts',response_model=list[PostResponse])
# # def get_user_posts(user_id:int, db:Annotated[Session, Depends(get_db)]):
# #     results = db.execute(select(models.User).where(models.User.id == user_id))
# #     user = results.scalars().first()
# #     if not user:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
# #     results = db.execute(select(models.Post).where(models.Post.user_id==user_id))
# #     posts = results.scalars().all()
# #     return posts
# async def get_user_posts(user_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.User).where(models.User.id==user_id))
#     user = res.scalars().first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
#     res = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id==user_id))
#     posts = res.scalars().all()
#     return posts
 
# #PATCH : Update User details : /api/users/{user_id} :
# @app.patch('/api/users/{user_id}',response_model=UserResponse)
# # def update_user(user_id:int, user_update:UserUpdate, db:Annotated[Session, Depends(get_db)]):
# #     res = db.execute(select(models.User).where(models.User.id==user_id))
# #     user= res.scalars().first()
# #     if not user:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
# #     if user_update.username is not None and user_update.username != user.username:
# #         res = db.execute(select(models.User).where(models.User.username==user_update.username))
# #         existing_user = res.scalars().first()
# #         if existing_user:
# #             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exists')
# #     if user_update.email is not None and user_update.email != user.email:
# #         res=db.execute(select(models.User).where(models.User.email==user_update.email))
# #         existing_email = res.scalars().first()
# #         if existing_email:
# #             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
# #     if user_update.username is not None:
# #         user.username = user_update.username
# #     if user_update.email is not None:
# #         user.email = user_update.email
# #     if user_update.image_file is not None:
# #         user.image_file = user_update.image_file

# #     db.commit()
# #     db.refresh(user)
# #     return user
# async def update_user(user_id:int, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.User).where(models.User.id==user_id))
#     user = res.scalars().first()
#     if not user:
#         raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User not found")
#     if user_update.username is not None and user_update.username != user.username:
#         res=await db.execute(select(models.User).where(models.User.username==user_update.username))
#         existing_user = res.scalars().first()
#         if existing_user:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Username already exists!")
#     if user_update.email is not None and user_update.email != user.email:
#         res = await db.execute(select(models.User).where(models.User.email == user_update.email))
#         existing_email = res.scalars().first()
#         if existing_email:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered!")
#     if user_update.username is not None:
#         user.username = user_update.username
#     if user_update.email is not None:
#         user.email = user_update.email
#     if user_update.image_file is not None:
#         user.image_file = user_update.image_file
#     await db.commit()
#     await db.refresh(user)
#     return user
    
# #DELETE: Delete a User (and his posts automatically) :
# @app.delete('/api/users/{user_id}',status_code=status.HTTP_204_NO_CONTENT)
# # def delete_user(user_id:int, db:Annotated[Session, Depends(get_db)]):
# #     res=db.execute(select(models.User).where(models.User.id==user_id))
# #     user=res.scalars().first()
# #     if not user:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
# #     db.delete(user)
# #     db.commit()
# async def delete_user(user_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.User).where(models.User.id==user_id))
#     user= res.scalars().first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
#     await db.delete(user)
#     await db.commit()

# # post ROUTES:
# #GET : get all posts: /api/posts
# @app.get("/api/posts",response_model=list[PostResponse])
# # def get_posts(db:Annotated[Session, Depends(get_db)]):
# #     result = db.execute(select(models.Post))
# #     posts = result.scalars().all()
# #     return posts
# async def home(request:Request, db:Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.Post).options(selectinload(models.Post.author)))
#     posts = res.scalars().all()
#     return posts

# #GET : get a post by id : /api/posts/{post_id} : 
# @app.get('/api/posts/{post_id}',response_model=PostResponse)
# # def get_post(post_id:int, db:Annotated[Session, Depends(get_db)]):
# #     res = db.execute(select(models.Post).where(models.Post.id == post_id))
# #     post = res.scalars().first()
# #     if post:
# #         return post
# #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found!")
# async def get_post(post_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id==post_id))
#     post = res.scalars().first()
#     if post:
#         return post
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found!')

# #POST : create a new post: /api/posts : 
# @app.post('/api/posts',response_model=PostResponse, status_code=status.HTTP_201_CREATED)
# # def create_post(post:PostCreate, db:Annotated[Session, Depends(get_db)]):
# #     res = db.execute(select(models.User).where(models.User.id==post.user_id))
# #     user = res.scalars().first()
# #     if not user:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
# #     new_p = models.Post(
# #         title = post.title,
# #         content=post.content,
# #         user_id = post.user_id
# #     )
# #     db.add(new_p)
# #     db.commit()
# #     db.refresh(new_p)
# #     return new_p
# async def create_post(post:PostCreate, db:Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.User).where(models.User.id==post.user_id))
#     usr = res.scalars().first()
#     if not usr:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='User not found')
#     new_post = models.Post(title=post.title, content= post.content, user_id=post.user_id)
#     db.add(new_post)
#     await db.commit()
#     await db.refresh(new_post, attribute_names=['author'])
#     return new_post


# #Full Update : PUT : /api/posts/{post_id}
# @app.put('/api/posts/{post_id}', response_model=PostResponse)
# # def update_post_full(post_id:int, post_data:PostCreate, db:Annotated[Session, Depends(get_db)]):
# #     res = db.execute(select(models.Post).where(models.Post.id==post_id))
# #     post = res.scalars().first()
# #     if not post:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
# #     if post_data.user_id != post.user_id:
# #         res=db.execute(select(models.User).where(models.User.id==post_data.user_id))
# #         usr = res.scalars().first()
# #         if not usr:
# #             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
# #     post.title = post_data.title
# #     post.content = post_data.content
# #     post.user_id = post_data.user_id
# #     db.commit()
# #     db.refresh(post)
# #     return post
# async def update_post_full(post_id:int, post_data:PostCreate, db:Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.Post).where(models.Post.id==post_id))
#     post= res.scalars().first()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
#     if post_data.user_id != post.user_id:
#         res = await db.execute(select(models.User).where(models.User.id==post_data.user_id))
#         user = res.scalars().first()
#         if not user:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     post.title = post_data.title
#     post.content=post_data.content
#     post.user_id = post_data.user_id

#     await db.commit()
#     await db.refresh(post, attribute_names=["author"])
#     return post

# # Partial Update : PATCH : /api/posts/{post_id} : 
# @app.patch('/api/posts/{post_id}', response_model=PostResponse)
# # def update_post_partial(post_id:int, post_data:PostUpdate, db: Annotated[Session, Depends(get_db)]):
# #     res = db.execute(select(models.Post).where(models.Post.id==post_id))
# #     post = res.scalars().first()
# #     if not post:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post Not Found')
# #     update_data = post_data.model_dump(exclude_unset=True)
# #     for field, value in update_data.items():
# #         setattr(post,field,value)
# #     db.commit()
# #     db.refresh(post)
# #     return post
# @app.patch('/api/posts/{post_id}', response_model=PostResponse)
# async def update_post_partial(post_id:int, post_data:PostUpdate, db:Annotated[AsyncSession, Depends(get_db)]):
#     result = await db.execute(select(models.Post).where(models.Post.id==post_id))
#     post   = result.scalars().first()
#     if not post:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Post not found'
#         )
#     update_data = post_data.model_dump(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(post, field, value)
#     await db.commit()
#     await db.refresh(post, attribute_names=["author"])
#     return post

# #DELETE : delete a post : /api/posts/{post_id} : 
# @app.delete('/api/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
# # def delete_post(post_id:int, db:Annotated[Session, Depends(get_db)]):
# #     res = db.execute(select(models.Post).where(models.Post.id==post_id))
# #     post = res.scalars().first()
# #     if not post:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
# #     db.delete(post)
# #     db.commit()
# async def delete_post(post_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
#     res = await db.execute(select(models.Post).where(models.Post.id==post_id))
#     post = res.scalars().first()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
#     await db.delete(post)
#     await db.commit()

#404 and Validation Error handlers: 
@app.exception_handler(RequestValidationError)
# def validation_excep_handler(request:Request, exception: RequestValidationError):
#     return temp_.TemplateResponse(request, "vError.html",{
#         "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
#         "title":status.HTTP_422_UNPROCESSABLE_CONTENT,
#         "message":"Invalid Request, Please check input"
#     },
#     status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
#     )
async def validation_excep_handler(request:Request, exception: RequestValidationError):
    return temp_.TemplateResponse(request, "vError.html",{
        "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
        "title":status.HTTP_422_UNPROCESSABLE_CONTENT,
        "message":"Invalid Request. Please check your input and try again!"
    },status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)

@app.exception_handler(StarletteHTTPExcep)
def general_http_excep_handler(request:Request, exception: StarletteHTTPExcep):
    message = (exception.detail if exception.detail else "An Error occured. Check you request!")
    return temp_.TemplateResponse(request, '404.html', {
        "status_code":exception.status_code,
        "title": exception.status_code,
        "message":message
    },status_code=exception.status_code)