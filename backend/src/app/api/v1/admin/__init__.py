"""后台管理专属 API 路由包聚合。"""

from fastapi import APIRouter
from app.api.v1.admin.auth import router as auth_router
from app.api.v1.admin.c_user import router as c_user_router
from app.api.v1.admin.character import router as character_router
from app.api.v1.admin.chat_ops import router as chat_ops_router
from app.api.v1.admin.cms import router as cms_router
from app.api.v1.admin.finance import router as finance_router
from app.api.v1.admin.rbac import router as rbac_router
from app.api.v1.admin.tavern import router as tavern_router
from app.api.v1.admin.llm import router as llm_router

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(auth_router)
admin_router.include_router(rbac_router)
admin_router.include_router(c_user_router)
admin_router.include_router(character_router)
admin_router.include_router(chat_ops_router)
admin_router.include_router(finance_router)
admin_router.include_router(cms_router)
admin_router.include_router(tavern_router)
admin_router.include_router(llm_router)

__all__ = ["admin_router"]
