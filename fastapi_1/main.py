from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as sHTTPExcep
from fastapi.exceptions import RequestValidationError
from schemas import PostCreate, PostResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name='static')

temps_ = Jinja2Templates(directory='templates')

posts : list[dict] = [
    {"id":1, "author":"jk", "title":"p1", "content":"Post 1 content"},
    {"id":2, "author":"jn", "title":"p2", "content":"Post 2 content"}
]

# -----------------------------------------------------------------------------------------------
# API ROUTES

@app.get('/api/posts', response_model=list[PostResponse])
def get_posts():
    return posts

@app.get('/api/posts/{post_id}', response_model=PostResponse)
def get_post(post_id:int):
    for p in posts:
        if p.get("id") == post_id:
            return p
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post('/api/posts',response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post:PostCreate):
    new_id = max(p["id"] for p in posts)+1 if posts else 1
    new_post = {
        "id" : new_id,
        "author"  : post.author,
        "title"  : post.title,
        "content" : post.content,
        "date_posted":"April 30, 2025"
    }
    posts.append(new_post)
    return new_post


# -----------------------------------------------------------------------------------------------
# JINJA ROUTES

@app.get('/',name='home')
def home(request:Request):
    return temps_.TemplateResponse(request, 'home.html',{"title":"Home Page"})

@app.get('/posts')
def get_posts_api(request:Request):
    return temps_.TemplateResponse(request, 'allposts.html', {"posts":posts, "title":"All Posts"})

@app.get('/posts/{post_id}')
def get_post_api(request:Request, post_id:int):
    for p in posts:
        if p.get("id") == post_id:
            return temps_.TemplateResponse(request,"aPost.html",{"p":p, "title":p["title"]})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

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