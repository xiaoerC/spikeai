"""API v1 版本主路由聚合模块。

Usage:
    >>> from fastapi import FastAPI
    >>> from app.api.v1.router import api_v1_router
    >>> app = FastAPI()
    >>> app.include_router(api_v1_router, prefix="/api/v1")
"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router

api_v1_router = APIRouter()

# 挂载各子模块路由
api_v1_router.include_router(health_router)
