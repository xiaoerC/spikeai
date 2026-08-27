"""API v1 版本主路由聚合模块。

挂载健康检查、用户认证、个人资产中心等子模块路由。

Usage:
    >>> from fastapi import FastAPI
    >>> from app.api.v1.router import api_v1_router
    >>> app = FastAPI()
    >>> app.include_router(api_v1_router, prefix="/api/v1")
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.character import router as character_router
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.api.v1.upload import router as upload_router
from app.api.v1.user import router as user_router

api_v1_router = APIRouter()

# 挂载各子模块路由
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(character_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(upload_router)
