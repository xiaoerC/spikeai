"""Mod 模组生态与优先级加载流水线 RESTful API 路由模块。

支持 Mod 广场检索、用户激活 Mod 优先级拖拽调序、启用/停用切换、统计指标与自定义 Mod 创建。

Usage:
    >>> from fastapi import APIRouter
    >>> from app.api.v1.mod import router as mod_router
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.mod import (
    ModCreateRequest,
    ModItemResponse,
    ModPrioritySummaryResponse,
    ModPriorityUpdateRequest,
    ModSquareFilterParams,
    ModUpdateRequest,
    UserActiveModResponse,
)
from app.services.mod_service import ModService

router = APIRouter(prefix="/mods", tags=["Mod 模组生态"])


@router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[ModItemResponse]],
    summary="获取 Mod 广场列表",
)
async def list_mods(
    category: str | None = Query(None, description="分类标签"),
    sort: str = Query("heat", description="排序 (heat / rating / newest)"),
    keyword: str | None = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页条数"),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[PaginatedResponse[ModItemResponse]]:
    """查询 Mod 广场列表。"""
    params = ModSquareFilterParams(
        category=category,
        sort=sort,  # type: ignore[arg-type]
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    result = await ModService.list_mods(db=db, params=params)
    return ApiResponse(data=result, message="获取 Mod 广场列表成功")


@router.get(
    "/active",
    response_model=ApiResponse[list[UserActiveModResponse]],
    summary="获取用户已激活 Mod 优先级矩阵",
)
async def get_user_active_mods(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[list[UserActiveModResponse]]:
    """获取当前用户已激活的 Mod 列表及其优先级排序。"""
    mods = await ModService.get_user_active_mods(db=db, user_id=current_user.id)
    return ApiResponse(data=mods, message="获取激活 Mod 列表成功")


@router.put(
    "/priority",
    response_model=ApiResponse[list[UserActiveModResponse]],
    summary="批量更新 Mod 激活与优先级排序",
)
async def update_mod_priorities(
    payload: ModPriorityUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[list[UserActiveModResponse]]:
    """批量调整 Mod 的 priority_order 权重与启停状态。"""
    updated_mods = await ModService.update_user_mod_priorities(
        db=db, user_id=current_user.id, req=payload
    )
    return ApiResponse(data=updated_mods, message="更新 Mod 优先级成功")


@router.get(
    "/summary",
    response_model=ApiResponse[ModPrioritySummaryResponse],
    summary="获取当前生效 Mod 统计横幅指标",
)
async def get_mod_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ModPrioritySummaryResponse]:
    """获取当前用户生效 Mod 的注入词条数与总字数统计。"""
    summary = await ModService.get_mod_priority_summary(db=db, user_id=current_user.id)
    return ApiResponse(data=summary, message="获取 Mod 统计成功")


@router.post(
    "",
    response_model=ApiResponse[ModItemResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建自定义 Mod",
)
async def create_mod(
    payload: ModCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ModItemResponse]:
    """创建并发布用户自定义 Mod。"""
    new_mod = await ModService.create_mod(db=db, user_id=current_user.id, req=payload)
    return ApiResponse(data=new_mod, message="创建 Mod 成功")


@router.get(
    "/{mod_id}",
    response_model=ApiResponse[ModItemResponse],
    summary="获取 Mod 详情",
)
async def get_mod_detail(
    mod_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ModItemResponse]:
    """根据 UUID 获取 Mod 完整详情与词条。"""
    mod = await ModService.get_mod_by_id(db=db, mod_id=mod_id)
    return ApiResponse(data=mod, message="获取 Mod 详情成功")


@router.put(
    "/{mod_id}",
    response_model=ApiResponse[ModItemResponse],
    summary="更新自定义 Mod",
)
async def update_mod(
    mod_id: uuid.UUID,
    payload: ModUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ModItemResponse]:
    """修改自定义 Mod 元数据与词条。"""
    updated_mod = await ModService.update_mod(
        db=db, user_id=current_user.id, mod_id=mod_id, req=payload
    )
    return ApiResponse(data=updated_mod, message="更新 Mod 成功")


@router.delete(
    "/{mod_id}",
    response_model=ApiResponse[dict[str, Any]],
    summary="删除自定义 Mod",
)
async def delete_mod(
    mod_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict[str, Any]]:
    """删除指定自定义 Mod。"""
    await ModService.delete_mod(db=db, user_id=current_user.id, mod_id=mod_id)
    return ApiResponse(data={"deleted_id": str(mod_id)}, message="删除 Mod 成功")


@router.post(
    "/{mod_id}/activate",
    response_model=ApiResponse[UserActiveModResponse],
    summary="快速切换 Mod 激活状态",
)
async def toggle_mod_activate(
    mod_id: uuid.UUID,
    is_active: bool | None = Query(None, description="指定激活状态 (省略则取反)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[UserActiveModResponse]:
    """一键启用或停用指定 Mod。"""
    result = await ModService.toggle_user_mod(
        db=db, user_id=current_user.id, mod_id=mod_id, is_active=is_active
    )
    return ApiResponse(data=result, message="切换 Mod 状态成功")
