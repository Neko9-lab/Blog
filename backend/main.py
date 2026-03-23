from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.api import router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine, async_session
from app.db.init_db import ensure_schema, init_db
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(ensure_schema)
    session = async_session()
    try:
        await init_db(session)
    finally:
        await session.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
setup_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "msg": exc.detail, "data": {}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    # 中文注释：统一参数校验错误格式
    # 参考文档：https://fastapi.tiangolo.com/tutorial/handling-errors/
    return JSONResponse(
        status_code=422,
        content={"code": 422, "msg": "Validation error", "data": exc.errors()},
    )


app.include_router(router, prefix=settings.api_prefix)

base_dir = Path(__file__).resolve().parent
static_dir = base_dir / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
