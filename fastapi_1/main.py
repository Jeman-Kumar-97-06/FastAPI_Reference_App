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
from starlette.exceptions       import HTTPException as StarletteException
from database                   import Base, engine, get_db
from routers                    import posts, users

import models

@asynccontextmanager
async def lifespan(_app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
#Base.metadata.create_all(bind=engine)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name='static')
app.mount("/media", StaticFiles(directory="media"), name="media")

temps_ = Jinja2Templates(directory='templates')

# -----------------------------------------------------------------------------------------------
# API ROUTES

app.include_router(users.router, prefix='/api/users', tags=['users'])
app.include_router(posts.router, prefix='/api/posts', tags=['posts'])

# -----------------------------------------------------------------------------------------------
# JINJA ROUTES

@app.get('/',name='home')
def home(request:Request):
    return temps_.TemplateResponse(request, 'home.html',{"title":"Home Page"})

@app.get('/posts')
async def get_posts_api(request:Request, db:Annotated[AsyncSession, Depends(get_db)]):
    results = await db.execute(select(models.Post))
    posts   = results.scalars().all()
    return temps_.TemplateResponse(request, 'allposts.html', {"posts":posts, "title":"All Posts"})

@app.get('/posts/{post_id}')
async def get_post_api(request:Request, post_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
    results = await db.execute(select(models.Post).where(models.Post.id==post_id))
    post    = results.scalars().first()
    if post:
        title = post.title[:50]
        return temps_.TemplateResponse(request, 'aPost.html',{"p":post, "title":title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get('/users/{user_id}/posts',include_in_schema=False)
async def user_posts_page(request:Request, user_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
    results = await db.execute(select(models.User).where(models.User.id==user_id))
    user    = results.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    results = await db.execute(select(models.Post).where(models.Post.user_id==user_id))
    posts   = results.scalars().all()
    return temps_.TemplateResponse(request, "user_posts.html",{"posts":posts, "user":user, "title":f"{user.username}'s Posts"}
    )

#-------------------------------------------------------------------------------------------------
@app.exception_handler(StarletteException)
async def general_http_exception_handler(
    request: Request,
    exception: StarletteException,
):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    return temps_.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

    return temps_.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )