from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name='static')

temps_ = Jinja2Templates(directory='templates')

posts : list[dict] = [
    {"id":1, "author":"jk", "title":"p1", "content":"Post 1 content"},
    {"id":2, "author":"jn", "title":"p2", "content":"Post 2 content"}
]

# -----------------------------------------------------------------------------------------------
# API ROUTES

@app.get('/api/posts')
def get_posts():
    return posts

@app.get('/api/posts/{post_id}')
def get_post(post_id:int):
    for p in posts:
        if p.get("id") == post_id:
            return p
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# -----------------------------------------------------------------------------------------------
# JINJA ROUTES

@app.get('/',name='home')
def home(request:Request):
    return temps_.TemplateResponse(request, 'home.html',{"title":"Home Page"})

@app.get('/posts')
def home(request:Request):
    return temps_.TemplateResponse(request, 'allposts.html', {"posts":posts, "title":"All Posts"})

