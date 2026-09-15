"""Admin 大模型 (LLM) API 渠道与模型上架配置管理路由。

提供多供应商 API 渠道管理 (CRUD)、上游 /v1/models 在线拉取、连通性探测 Ping、
模型上架状态与定价维护等管理能力。

Usage:
    GET    /api/v1/admin/llm/providers
    POST   /api/v1/admin/llm/providers
    PUT    /api/v1/admin/llm/providers/{provider_id}
    DELETE /api/v1/admin/llm/providers/{provider_id}
    POST   /api/v1/admin/llm/providers/{provider_id}/toggle-active
    POST   /api/v1/admin/llm/providers/{provider_id}/models/{model_id}/toggle-public
    POST   /api/v1/admin/llm/test-connection
    POST   /api/v1/admin/llm/fetch-models
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import RequirePermission
from app.models.admin import AdminUser
from app.schemas.common import ApiResponse
from app.schemas.llm import (
    LLMFetchModelsRequest,
    LLMFetchModelsResponse,
    LLMProviderCreate,
    LLMProviderResponse,
    LLMProviderUpdate,
    LLMTestConnectionRequest,
    LLMTestConnectionResponse,
)
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["Admin 大模型 API 与模型调度中枢"])


@router.get(
    "/providers",
    response_model=ApiResponse[list[LLMProviderResponse]],
    summary="获取所有大模型 API 渠道配置列表 (已脱敏)",
)
async def list_admin_llm_providers(
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:llm:view", "system:settings:view")),
) -> ApiResponse[list[LLMProviderResponse]]:
    """检索系统内全部已配置的大模型 API 供应商渠道列表。"""
    providers = await LLMService.list_providers(db=db)
    return ApiResponse(
        data=providers,
        message="获取大模型 API 渠道列表成功",
    )


@router.post(
    "/providers",
    response_model=ApiResponse[LLMProviderResponse],
    summary="新建大模型 API 渠道配置",
)
async def create_admin_llm_provider(
    payload: LLMProviderCreate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:llm:edit", "system:settings:edit")),
) -> ApiResponse[LLMProviderResponse]:
    """创建新的大模型 API 渠道（支持反代 Base URL、密钥与初始模型列表）。"""
    provider = await LLMService.create_provider(db=db, payload=payload)
    return ApiResponse(
        data=provider,
        message="新建大模型渠道成功",
    )


@router.put(
    "/providers/{provider_id}",
    response_model=ApiResponse[LLMProviderResponse],
    summary="更新指定大模型 API 渠道配置",
)
async def update_admin_llm_provider(
    payload: LLMProviderUpdate,
    provider_id: uuid.UUID = Path(..., description="渠道唯一 UUID"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:llm:edit", "system:settings:edit")),
) -> ApiResponse[LLMProviderResponse]:
    """更新大模型渠道基础信息、密钥或模型上架清单。若包含星号脱敏则保持历史密钥不变。"""
    provider = await LLMService.update_provider(db=db, provider_id=provider_id, payload=payload)
    return ApiResponse(
        data=provider,
        message="更新大模型渠道成功",
    )


@router.delete(
    "/providers/{provider_id}",
    response_model=ApiResponse[dict[str, Any]],
    summary="删除指定大模型 API 渠道",
)
async def delete_admin_llm_provider(
    provider_id: uuid.UUID = Path(..., description="渠道唯一 UUID"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:llm:edit", "system:settings:edit")),
) -> ApiResponse[dict[str, Any]]:
    """删除指定的 API 供应商渠道配置。"""
    await LLMService.delete_provider(db=db, provider_id=provider_id)
    return ApiResponse(
        data={"deleted": True, "provider_id": str(provider_id)},
        message="删除大模型渠道成功",
    )


@router.post(
    "/providers/{provider_id}/toggle-active",
    response_model=ApiResponse[LLMProviderResponse],
    summary="快捷切换渠道启用/停用状态",
)
async def toggle_admin_provider_active(
    provider_id: uuid.UUID = Path(..., description="渠道唯一 UUID"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:llm:edit", "system:settings:edit")),
) -> ApiResponse[LLMProviderResponse]:
    """快捷启停渠道，停用后其下所有模型将不再下发给 C 端客户端。"""
    provider = await LLMService.toggle_provider_active(db=db, provider_id=provider_id)
    return ApiResponse(
        data=provider,
        message=f"渠道已{'启用' if provider.is_active else '停用'}",
    )


@router.post(
    "/providers/{provider_id}/models/{model_id}/toggle-public",
    response_model=ApiResponse[LLMProviderResponse],
    summary="快捷切换特定模型的 C 端上架可见性",
)
async def toggle_admin_model_public(
    provider_id: uuid.UUID = Path(..., description="渠道唯一 UUID"),
    model_id: str = Path(..., description="模型唯一标识 ID"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:llm:edit", "system:settings:edit")),
) -> ApiResponse[LLMProviderResponse]:
    """切换指定模型是否上架至用户端模型选择面板。"""
    provider = await LLMService.toggle_model_public(db=db, provider_id=provider_id, model_id=model_id)
    return ApiResponse(
        data=provider,
        message="模型客户端上架状态已更新",
    )


@router.post(
    "/test-connection",
    response_model=ApiResponse[LLMTestConnectionResponse],
    summary="测试上游 API 端点连通性 (Ping 测速与探测)",
)
async def test_llm_connection(
    req: LLMTestConnectionRequest,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:llm:view", "system:settings:view")),
) -> ApiResponse[LLMTestConnectionResponse]:
    """向目标 Base URL 探测连通性并返回网络延迟毫秒数与探测到的模型概览。"""
    result = await LLMService.test_connection(db=db, req=req)
    return ApiResponse(
        data=result,
        message=result.message,
    )


@router.post(
    "/fetch-models",
    response_model=ApiResponse[LLMFetchModelsResponse],
    summary="请求上游 /v1/models 在线拉取该渠道全部可用模型标识",
)
async def fetch_upstream_llm_models(
    req: LLMFetchModelsRequest,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:llm:view", "system:settings:view")),
) -> ApiResponse[LLMFetchModelsResponse]:
    """请求供应商的 /models 端点，拉取真实授权可用的模型列表，供管理员一键勾选入库。"""
    result = await LLMService.fetch_upstream_models(db=db, req=req)
    return ApiResponse(
        data=result,
        message=result.message,
    )
