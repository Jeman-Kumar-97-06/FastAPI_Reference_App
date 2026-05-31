from contextlib                 import asynccontextmanager
from typing                     import Annotated
from fastapi                    import Depends, FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import (http_exception_handler, request_validation_exception_handler)
from fastapi.exceptions         import RequestValidationError
from fastapi.staticfiles        import StaticFiles
from fastapi.templating         import Jinja2Templates
from sqlalchemy                 import select
from sqlalchemy.ext.asyncio     import AsyncSession
from sqlalchemy.orm             import selectinload
from starlette.exceptions       import HTTPException as StartletteException
from database                   import Base, engine, get_db
from routers                    import posts, users

import models

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name='static')
app.mount("/media", StaticFiles(directory="media"), name="media")

temps_ = Jinja2Templates(directory='templates')

# posts : list[dict] = [
#     {"id":1, "author":"jk", "title":"p1", "content":"Post 1 content"},
#     {"id":2, "author":"jn", "title":"p2", "content":"Post 2 content"}
# ]

# -----------------------------------------------------------------------------------------------
# API ROUTES

@app.get('/api/posts', response_model=list[PostResponse])
def get_posts(db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts  = result.scalars().all()
    return posts

@app.get('/api/posts/{post_id}', response_model=PostResponse)
def get_post(post_id:int, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id==post_id))
    post   = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post('/api/posts',response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post:PostCreate, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id==post.user_id))
    user   = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "User not found"
        )
    #--------------------Create a New ID for the new post--------
    # new_id = max(p["id"] for p in posts)+1 if posts else 1 --> ID is created automatically
    new_post = models.Post(
        title = post.title,
        content = post.content,
        user_id = post.user_id
    )
    #--------------------Add to the existing posts --------------
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

#--------------------Full PUT update------------------------
@app.put('/api/posts/{post_id}', response_model=PostResponse)
def update_post_full(post_id:int, post_data:PostCreate, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id==post_id))
    post   = result.scalars().first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post_data.user_id!=post.user_id:
        result = db.execute(select(models.User).where(models.User.id==post_data.user_id))
        user   = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail      = "User not found"
            )
    post.tile    = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id
    db.commit()
    db.refresh(post)
    return post

#--------------------Partial PATCH Update---------------
@app.patch('/api/posts/{post_id}',response_model=PostResponse)
def update_post_partial(post_id:int, post_data:PostUpdate, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id==post_id))
    post   = result.scalars().first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail='Post not found')
    update_data = post_data.model_dump(exclude_unset=True)
    for f,v in update_data.item():
        setattr(post, f, v)
    db.commit()
    db.refresh(post)
    return post






# -----------------------------------------------------------------------------------------------
# JINJA ROUTES

@app.get('/',name='home')
def home(request:Request):
    return temps_.TemplateResponse(request, 'home.html',{"title":"Home Page"})

@app.get('/posts')
def get_posts_api(request:Request, db:Annotated[Session, Depends(get_db)]):
    results = db.execute(select(models.Post))
    posts   = results.scalars().all()
    return temps_.TemplateResponse(request, 'allposts.html', {"posts":posts, "title":"All Posts"})

@app.get('/posts/{post_id}')
def get_post_api(request:Request, post_id:int, db:Annotated[Session, Depends(get_db)]):
    results = db.execute(select(models.Post).where(models.Post.id==post_id))
    post    = results.scalars().first()
    if post:
        title = post.title[:50]
        return temps_.TemplateResponse(request, 'aPost.html',{"p":post, "title":title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get('/users/{user_id}/posts',include_in_schema=False)
def user_posts_page(request:Request, user_id:int, db:Annotated[Session, Depends(get_db)]):
    results = db.execute(select(models.User).where(models.User.id==user_id))
    user    = results.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    results = db.execute(select(models.Post).where(models.Post.user_id==user_id))
    posts   = results.scalars().all()
    return temps_.TemplateResponse(request, "user_posts.html",{"posts":posts, "user":user, "title":f"{user.username}'s Posts"}
    )

#-------------------------------------------------------------------------------------------------
@app.exception_handler(sHTTPExcep)
def general_http_excep_handler(request:Request, exception:sHTTPExcep):
    message= (
        exception.detail
        if exception.detail
        else 'An Error Occured. Check ur request!'
    )
    if request.url.path.startswith('/api'):
        return JSONResponse(
            status_code = exception.status_code,
            content={'detail':message}
        )
    return temps_.TemplateResponse(
        request,
        '404.html',
        {
            "status_code":exception.status_code,
            "title":exception.status_code,
            "message":message
        },
        status_code=exception.status_code
    )


@app.exception_handler(RequestValidationError)
def validation_excep_handler(request:Request, exception:RequestValidationError):
    if request.url.path.startswith('/api'):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail":exception.errors()}
        )
    return temps_.TemplateResponse(
        request,
        "404.html",
        {
            "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message":"Invalid Request, Check Input"
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )