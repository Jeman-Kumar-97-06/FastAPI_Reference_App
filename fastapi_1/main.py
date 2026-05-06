from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StHTTPExcep

#intialize "fastapi" app:
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

posts : list[dict] = [
    {"id":1, "author": "jk", "title":"post1", "content":"C1"},
    {"id":2, "author": "jk", "title":"post2", "content":"C2"},
    {"id":3, "author":"jk2", "title":"post3", "content":"C3"}
]

#'/api' route controller:
@app.get("/api")
def home():
    return {"message":"Hello!"}


@app.get('/api/posts')
def get_posts():
    return posts

@app.get('/api/posts/{post_id}')
def get_post(post_id:int):
    for post in posts:
        if post.get('id') == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')


@app.exception_handler(StHTTPExcep)
def general_http_excep_handler(request:Request, exception: StHTTPExcep):
    message=(
        exception.detail if exception.detail else 'An Error Occured. Check your request.'
    )
    return JSONResponse(
        status_code = exception.status_code,
        content={'detail':message}
    )
