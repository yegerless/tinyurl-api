import uvicorn

from fastapi import FastAPI

from config import DEBUG, HOST_PORT
from links.router import links_router
from auth.router import auth_router

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Service is alive!'}

app.include_router(links_router)
app.include_router(auth_router)


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=HOST_PORT, reload=DEBUG)