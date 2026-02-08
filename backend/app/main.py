from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import settings
from app.core.redis import redis_client
from app.db.session import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['*'],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get('/health')
async def health() -> dict:
    db_ok = False
    redis_ok = False

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text('SELECT 1'))
        db_ok = True
    except Exception:
        db_ok = False

    try:
        redis_ok = bool(await redis_client.ping())
    except Exception:
        redis_ok = False

    status = 'ok' if db_ok and redis_ok else 'degraded'
    return {'status': status, 'database': db_ok, 'redis': redis_ok}
