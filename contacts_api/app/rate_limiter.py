from fastapi_limiter import FastAPILimiter
from fastapi import FastAPI
import os

async def init_limiter(app: FastAPI):
    redis_url = os.getenv("REDIS_URL")
    await FastAPILimiter.init(redis_url)