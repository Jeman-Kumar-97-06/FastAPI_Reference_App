from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
temp_ = Jinja2Templates(directory='templates')

@app.get("/")
def home():
    return {"message":"Hello!"}

posts:list[dict] = [
    {"id":1, "author":"J1", "title":"post1", "content":"C1"},
    {"id":2, "author":"J2", "title":"post2", "content":"C2"},
    {"id":3, "author":"J3", "title":"post3", "content":"C3"}
]

@app.get("/api/posts")
def get_posts():
    return posts

