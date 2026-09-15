"""SillyTavern (酒馆) 预设与提示词编排 RESTful 路由。

提供酒馆调音台当前预设的查询、自定义修改、重置与状态查询。

Usage:
    GET  /api/v1/tavern/preset
    PUT  /api/v1/tavern/preset
    POST /api/v1/tavern/reset
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.tavern import TavernPresetConfig, TavernPresetUpdateRequest
from app.services.tavern_service import TavernService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tavern", tags=["SillyTavern 酒馆调音台 (内部测试)"])


@router.get(
    "/preset",
    response_model=ApiResponse[TavernPresetConfig],
    summary="获取当前用户的酒馆预设 (若无则返回仓鼠之神V2默认预设)",
)
async def get_tavern_preset(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TavernPresetConfig]:
    """获取当前生效的酒馆预设配置。"""
    preset = await TavernService.get_user_preset(current_user.id)
    return ApiResponse(data=preset, message="获取酒馆预设成功")


@router.put(
    "/preset",
    response_model=ApiResponse[TavernPresetConfig],
    summary="保存或更新酒馆预设配置",
)
async def update_tavern_preset(
    payload: TavernPresetConfig,
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TavernPresetConfig]:
    """更新当前用户的酒馆预设。"""
    updated = await TavernService.update_user_preset(current_user.id, payload)
    return ApiResponse(
        data=updated,
        message="酒馆调音台预设已成功保存",
        show_message=True,
    )


@router.post(
    "/reset",
    response_model=ApiResponse[TavernPresetConfig],
    summary="一键重置为官方原版「仓鼠之神V2」预设",
)
async def reset_tavern_preset(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TavernPresetConfig]:
    """重置回官方原版配置。"""
    fresh = await TavernService.reset_user_preset(current_user.id)
    return ApiResponse(
        data=fresh,
        message="已恢复官方原版「仓鼠之神V2」配置",
        show_message=True,
    )


@router.get(
    "/presets",
    response_model=ApiResponse[list[dict[str, Any]]],
    summary="获取当前用户所有可用预设列表 (含官方内置与自定义另存)",
)
async def list_tavern_presets(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[list[dict[str, Any]]]:
    """获取预设列表。"""
    list_data = await TavernService.list_user_presets(current_user.id)
    return ApiResponse(data=list_data, message="获取预设列表成功")


@router.post(
    "/presets",
    response_model=ApiResponse[TavernPresetConfig],
    summary="另存为或覆盖用户自定义酒馆预设",
)
async def save_named_tavern_preset(
    payload: TavernPresetConfig,
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TavernPresetConfig]:
    """另存自定义预设。"""
    saved = await TavernService.save_named_preset(current_user.id, payload)
    return ApiResponse(
        data=saved,
        message=f"预设「{saved.preset_name}」已成功保存并设为当前生效预设",
        show_message=True,
    )


@router.delete(
    "/presets/{preset_name}",
    response_model=ApiResponse[bool],
    summary="删除用户自定义酒馆预设 (官方内置预设不可删除)",
)
async def delete_named_tavern_preset(
    preset_name: str,
    current_user: User = Depends(get_current_user),
) -> ApiResponse[bool]:
    """删除自建预设。"""
    success = await TavernService.delete_named_preset(current_user.id, preset_name)
    if not success:
        return ApiResponse(
            code=40001,
            data=False,
            message="内置预设不可删除或未找到对应自定义预设",
            show_message=True,
        )
    return ApiResponse(
        data=True,
        message=f"已成功删除预设「{preset_name}」",
        show_message=True,
    )
