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


#404 and Validation Error handlers: 
@app.exception_handler(RequestValidationError)
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