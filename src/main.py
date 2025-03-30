from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from time import sleep

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from config import DEBUG, HOST_PORT, REDIS_PASSWORD
from links.router import links_router
from auth.router import auth_router



@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(f"redis://default:{REDIS_PASSWORD}@redis:5370/0")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)


@app.get('/')
@cache(expire=30)
async def root():
    sleep(5)
    return {'message': 'Сервис работает!'}

app.include_router(links_router)
app.include_router(auth_router)


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=HOST_PORT, reload=DEBUG)