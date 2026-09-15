"""Admin SillyTavern 全局酒馆调音台与 Prompt 流水线管理路由。

提供全平台统一大模型生成参数调控、78 项 Transformer 提示词排版流水线管理、
出厂默认一键回滚与版本历史查询。

Usage:
    GET  /api/v1/admin/tavern/preset
    PUT  /api/v1/admin/tavern/preset
    POST /api/v1/admin/tavern/reset
    GET  /api/v1/admin/tavern/presets
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import RequirePermission
from app.models.admin import AdminUser
from app.schemas.common import ApiResponse
from app.schemas.tavern import TavernPresetConfig
from app.services.tavern_service import TavernService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tavern", tags=["SillyTavern 全局调音中枢 (Admin)"])


@router.get(
    "/preset",
    response_model=ApiResponse[TavernPresetConfig],
    summary="获取全平台当前生效的全局酒馆预设",
)
async def get_admin_tavern_preset(
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:view")),
) -> ApiResponse[TavernPresetConfig]:
    """获取全平台当前生效的全局预设配置 (78 项流水线及物理采样参数)。"""
    preset = await TavernService.get_system_preset(db=db)
    return ApiResponse(
        data=preset,
        message="获取平台全局酒馆预设成功",
    )


@router.get(
    "/default-preset",
    response_model=ApiResponse[TavernPresetConfig],
    summary="获取官方出厂默认「仓鼠之神V2」原始预设配置 (只读基准)",
)
async def get_admin_tavern_default_preset(
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:view")),
) -> ApiResponse[TavernPresetConfig]:
    """获取官方原版出厂预设 (包含 78 项纯净初始流水线条目与超参数)，供单项还原对比。"""
    default_preset = TavernService.get_default_preset()
    return ApiResponse(
        data=default_preset,
        message="获取出厂默认预设基准成功",
    )


@router.put(
    "/preset",
    response_model=ApiResponse[TavernPresetConfig],
    summary="保存并全平台热发布全局酒馆预设",
)
async def update_admin_tavern_preset(
    payload: TavernPresetConfig,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:edit")),
) -> ApiResponse[TavernPresetConfig]:
    """更新并发布全平台生效的酒馆预设。所有用户后续请求将立即按此新预设生成。"""
    updated = await TavernService.update_system_preset(
        db=db,
        updated=payload,
        admin_user=current_admin.username,
        description=f"管理员 [{current_admin.username}] 热更新发布",
    )
    return ApiResponse(
        data=updated,
        message="全局酒馆调音台配置已更新并全平台实时生效",
        show_message=True,
    )


@router.post(
    "/reset",
    response_model=ApiResponse[TavernPresetConfig],
    summary="一键恢复全平台官方出厂原版「仓鼠之神V2」预设",
)
async def reset_admin_tavern_preset(
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:edit")),
) -> ApiResponse[TavernPresetConfig]:
    """将全平台预设一键回退恢复至官方出厂标准配置。"""
    fresh = await TavernService.reset_system_preset(
        db=db,
        admin_user=current_admin.username,
    )
    return ApiResponse(
        data=fresh,
        message="全平台已成功恢复官方出厂默认「仓鼠之神V2」预设",
        show_message=True,
    )


class TavernPresetRenameRequest(BaseModel):
    """预设重命名请求。"""

    name: str = Field(..., min_length=1, max_length=64, description="新的预设名称")


@router.get(
    "/presets",
    response_model=ApiResponse[list[dict[str, Any]]],
    summary="获取平台预设库全部自导入/已保存预设列表",
)
async def list_admin_tavern_presets(
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:view")),
) -> ApiResponse[list[dict[str, Any]]]:
    """获取所有可用预设列表（来自数据库真实存储，支持切换）。"""
    list_data = await TavernService.list_presets(db=db)
    return ApiResponse(
        data=list_data,
        message="获取预设列表成功",
    )


@router.get(
    "/presets/{preset_id}",
    response_model=ApiResponse[TavernPresetConfig],
    summary="获取指定 ID 的预设完整配置详情",
)
async def get_admin_tavern_preset_by_id(
    preset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:view")),
) -> ApiResponse[TavernPresetConfig]:
    """获取特定预设完整提示词流水线及参数配置。"""
    config = await TavernService.get_preset_by_id(db=db, preset_id=preset_id)
    return ApiResponse(
        data=config,
        message=f"获取预设「{config.preset_name}」配置成功",
    )


@router.post(
    "/presets",
    response_model=ApiResponse[dict[str, Any]],
    summary="导入或新建一个预设入库",
)
async def create_admin_tavern_preset(
    payload: TavernPresetConfig,
    is_active: bool = False,
    description: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:edit")),
) -> ApiResponse[dict[str, Any]]:
    """导入/新建全新预设实体。"""
    created = await TavernService.create_preset(
        db=db,
        preset=payload,
        admin_user=current_admin.username,
        is_active=is_active,
        description=description,
    )
    return ApiResponse(
        data=created,
        message=f"预设「{payload.preset_name}」已成功保存入库",
        show_message=True,
    )


@router.put(
    "/presets/{preset_id}",
    response_model=ApiResponse[dict[str, Any]],
    summary="更新指定已有预设的配置",
)
async def update_admin_tavern_preset_by_id(
    preset_id: uuid.UUID,
    payload: TavernPresetConfig,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:edit")),
) -> ApiResponse[dict[str, Any]]:
    """更新已有预设实体内容。"""
    updated = await TavernService.update_preset_by_id(
        db=db,
        preset_id=preset_id,
        updated=payload,
        admin_user=current_admin.username,
    )
    return ApiResponse(
        data=updated,
        message=f"预设「{payload.preset_name}」配置已更新",
        show_message=True,
    )


@router.post(
    "/presets/{preset_id}/activate",
    response_model=ApiResponse[TavernPresetConfig],
    summary="将指定预设激活设为全平台全局生效",
)
async def activate_admin_tavern_preset(
    preset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:edit")),
) -> ApiResponse[TavernPresetConfig]:
    """一键切换并激活指定预设为全平台生效。"""
    activated = await TavernService.activate_preset(
        db=db,
        preset_id=preset_id,
        admin_user=current_admin.username,
    )
    return ApiResponse(
        data=activated,
        message=f"已成功将预设「{activated.preset_name}」设为全平台全局生效！",
        show_message=True,
    )


@router.delete(
    "/presets/{preset_id}",
    response_model=ApiResponse[bool],
    summary="删除指定预设 (非生效预设)",
)
async def delete_admin_tavern_preset(
    preset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:edit")),
) -> ApiResponse[bool]:
    """删除非激活的预设。"""
    success = await TavernService.delete_preset(db=db, preset_id=preset_id)
    return ApiResponse(
        data=success,
        message="预设已成功删除",
        show_message=True,
    )


@router.post(
    "/presets/{preset_id}/rename",
    response_model=ApiResponse[dict[str, Any]],
    summary="重命名指定预设",
)
async def rename_admin_tavern_preset(
    preset_id: uuid.UUID,
    payload: TavernPresetRenameRequest,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:tavern:edit")),
) -> ApiResponse[dict[str, Any]]:
    """快速修改预设名称。"""
    renamed = await TavernService.rename_preset(
        db=db,
        preset_id=preset_id,
        new_name=payload.name,
        admin_user=current_admin.username,
    )
    return ApiResponse(
        data=renamed,
        message=f"预设已成功更名为「{payload.name}」",
        show_message=True,
    )
