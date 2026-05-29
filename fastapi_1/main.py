from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

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

# -----------------------------------------------------------------------------------------------
# JINJA ROUTES

@app.get('/')
def home(request:Request):
    return temps_.TemplateResponse(request, 'home.html')

@app.get('/posts')
def home(request:Request):
    return temps_.TemplateResponse(request, 'allposts.html', {"posts":posts})

