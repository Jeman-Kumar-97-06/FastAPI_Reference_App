from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPExcep

from schemas import PostCreate, PostResponse

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
@app.get("/api/posts")
def get_posts():
    return posts

#GET : get a post by id : /api/posts/{post_id} : 
@app.get('/api/posts/{post_id}')
def get_post(post_id:int):
    for post in posts:
        if post.get("id") == post_id:
            return post
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')


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