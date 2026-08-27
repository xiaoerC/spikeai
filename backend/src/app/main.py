"""FastAPI 异步主应用入口。

配置生命周期管理 (Lifespan)、跨域 (CORS) 中间件、全局异常处理器及 API 路由。

Usage:
    启动服务:
    $ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.config import get_settings
from app.core.database import async_engine
from app.core.exceptions import AppException
from app.core.redis import close_redis_connection

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("spikeai.main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用程序生命周期上下文管理器。

    在服务启动时验证连接与种子数据预热，在服务停机时优雅释放数据库与 Redis 连接池。
    """
    logger.info("SpikeAI 异步后端服务正在启动 (Env: %s)...", settings.APP_ENV)
    try:
        from app.core.database import AsyncSessionLocal
        from app.services.character_service import CharacterService

        async with AsyncSessionLocal() as db:
            await CharacterService.ensure_seed_characters(db)
            await CharacterService.prewarm_market_cache(db)
    except Exception as e:
        logger.warning("服务启动时种子注入与预热检查跳过: %s", e)
    yield
    logger.info("SpikeAI 异步后端服务正在停止，正在释放连接池资源...")
    await close_redis_connection()
    await async_engine.dispose()
    logger.info("资源已安全释放，进程安全退出。")


def create_application() -> FastAPI:
    """初始化并配置 FastAPI 实例。

    Returns:
        FastAPI: 配置完毕的应用实例。
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="SpikeAI / Narratium 叙梦 Naro 1:1 复刻全栈系统异步接口网关",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # 配置 CORS 跨域支持 (支持前端 Vue 3 本地开发与生产域名)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    # 1. 拦截所有 HTTP 异常 (401, 403, 404, 400 等)，统一输出标准业务 JSON
    @app.exception_handler(StarletteHTTPException)
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning(
            "HTTP 请求异常 [URI: %s] [Status: %s]: %s",
            request.url.path,
            exc.status_code,
            exc.detail,
        )
        code = exc.status_code * 100 if exc.status_code >= 400 else exc.status_code
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": code,
                "message": str(exc.detail),
                "show_message": True,
                "data": None,
            },
            headers=getattr(exc, "headers", None),
        )

    # 2. 拦截 Pydantic DTO 参数校验异常 (422)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("请求参数校验失败 [URI: %s]: %s", request.url.path, exc.errors())
        first_err = exc.errors()[0] if exc.errors() else {}
        err_msg = first_err.get("msg", "请求参数格式不正确")
        field = ".".join(str(loc) for loc in first_err.get("loc", []))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 42201,
                "message": f"参数格式错误 ({field}): {err_msg}" if field else f"参数错误: {err_msg}",
                "show_message": True,
                "data": None,
            },
        )

    # 3. 注册系统自定义业务异常处理器
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "业务逻辑异常 [URI: %s] [%s]: %s (Details: %s)",
            request.url.path,
            exc.error_code,
            exc.message,
            exc.details,
        )
        code = exc.status_code * 100 if exc.status_code >= 400 else exc.status_code
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": code,
                "message": exc.message,
                "show_message": True,
                "data": exc.details if exc.details else None,
            },
        )

    # 4. 注册全局未处理兜底异常处理器 (防御性编程：不静默吞掉异常，记录完整堆栈)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "未捕获的系统严重异常 [URI: %s]",
            request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 50001,
                "message": "服务器发生未知异常，请联系管理员",
                "show_message": True,
                "data": {"type": type(exc).__name__, "error": str(exc)}
                if settings.DEBUG
                else None,
            },
        )

    # 注册 API 路由树
    app.include_router(api_v1_router, prefix="/api/v1")

    # 挂载本地上传静态文件目录 (Local Fallback)
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

    return app


app: FastAPI = create_application()
