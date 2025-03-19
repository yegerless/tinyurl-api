import uvicorn

from fastapi import FastAPI

from config import DEBUG
from links.router import links_router

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Service is alive!'}


app.include_router(links_router)


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8088, reload=DEBUG)