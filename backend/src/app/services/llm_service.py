"""大模型 (LLM) API 渠道与可用模型管理服务。

负责管理平台级多大模型供应商配置、连通性探测、在线 /v1/models 远端拉取、
C 端安全公开可用模型聚合以及为动态流式网关提供路由选路支持。

Usage:
    >>> from app.services.llm_service import LLMService
    >>> providers = await LLMService.list_providers(db)
"""

import logging
import time
import uuid
from typing import Any

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.config import get_settings
from app.models.llm import SystemLLMProvider
from app.schemas.llm import (
    ClientModelItem,
    LLMFetchModelsRequest,
    LLMFetchModelsResponse,
    LLMModelItem,
    LLMProviderCreate,
    LLMProviderResponse,
    LLMProviderUpdate,
    LLMTestConnectionRequest,
    LLMTestConnectionResponse,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    """大模型 API 渠道与模型配置中枢服务。"""

    @staticmethod
    def mask_api_key(key: str | None) -> str:
        """对敏感 API Key 进行脱敏保护处理 (前4后4星号脱敏)。"""
        if not key:
            return ""
        if len(key) <= 8:
            return "sk-****"
        return f"{key[:4]}****{key[-4:]}"

    @classmethod
    async def seed_default_providers(cls, db: AsyncSession) -> list[SystemLLMProvider]:
        """初始化出厂默认大模型 API 渠道 (DeepSeek 官方 + OpenAI 兼容示例)。"""
        # 1. 默认 DeepSeek 官方
        deepseek_key = getattr(settings, "DEEPSEEK_API_KEY", "") or ""
        deepseek_provider = SystemLLMProvider(
            name="DeepSeek 官方 API",
            provider_type="openai",
            base_url="https://api.deepseek.com/v1",
            api_key=deepseek_key,
            is_active=True,
            timeout_seconds=90,
            custom_headers={},
            models=[
                {
                    "id": "deepseek-chat",
                    "display_name": "DeepSeek-V3 旗舰大模型",
                    "is_enabled": True,
                    "is_public": True,
                    "is_default": True,
                    "supports_streaming": True,
                    "supports_reasoning": False,
                    "cost": 1,
                    "family": "deepseek",
                    "context_limit": 64000,
                    "sort_order": 100,
                },
                {
                    "id": "deepseek-reasoner",
                    "display_name": "DeepSeek-R1 深度思考",
                    "is_enabled": True,
                    "is_public": True,
                    "is_default": False,
                    "supports_streaming": True,
                    "supports_reasoning": True,
                    "cost": 2,
                    "family": "deepseek",
                    "context_limit": 64000,
                    "sort_order": 90,
                },
            ],
            description="DeepSeek 官方直连 API，支持 V3 极速生成与 R1 深度思考链",
            sort_order=100,
        )

        # 2. 备选 OpenAI 直连 / 聚合中转
        openai_key = getattr(settings, "OPENAI_API_KEY", "") or ""
        openai_provider = SystemLLMProvider(
            name="OpenAI 兼容 / 聚合中转",
            provider_type="openai",
            base_url=getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1") or "https://api.openai.com/v1",
            api_key=openai_key,
            is_active=bool(openai_key),
            timeout_seconds=60,
            custom_headers={},
            models=[
                {
                    "id": "gpt-4o",
                    "display_name": "GPT-4o 全能旗舰",
                    "is_enabled": True,
                    "is_public": True,
                    "is_default": False,
                    "supports_streaming": True,
                    "supports_reasoning": False,
                    "cost": 2,
                    "family": "gpt",
                    "context_limit": 128000,
                    "sort_order": 80,
                },
                {
                    "id": "gpt-4o-mini",
                    "display_name": "GPT-4o-mini 快速版",
                    "is_enabled": True,
                    "is_public": True,
                    "is_default": False,
                    "supports_streaming": True,
                    "supports_reasoning": False,
                    "cost": 1,
                    "family": "gpt",
                    "context_limit": 128000,
                    "sort_order": 70,
                },
            ],
            description="支持 OpenAI 官方或各类 OneAPI / NewAPI 反向代理中转站",
            sort_order=50,
        )

        db.add(deepseek_provider)
        db.add(openai_provider)
        await db.commit()
        await db.refresh(deepseek_provider)
        await db.refresh(openai_provider)
        logger.info("已自动初始化出厂默认大模型渠道: DeepSeek + OpenAI")
        return [deepseek_provider, openai_provider]

    @classmethod
    async def list_providers(cls, db: AsyncSession) -> list[LLMProviderResponse]:
        """获取所有 API 提供商渠道列表 (已脱敏 API Key)。"""
        stmt = select(SystemLLMProvider).order_by(
            SystemLLMProvider.sort_order.desc(),
            SystemLLMProvider.created_at.asc(),
        )
        res = await db.execute(stmt)
        rows = res.scalars().all()

        if not rows:
            rows = await cls.seed_default_providers(db)

        result: list[LLMProviderResponse] = []
        for r in rows:
            raw_models = r.models if isinstance(r.models, list) else []
            model_items: list[LLMModelItem] = []
            for m in raw_models:
                if isinstance(m, dict):
                    model_items.append(LLMModelItem.model_validate(m))

            public_count = sum(1 for m in model_items if m.is_public and m.is_enabled)
            result.append(
                LLMProviderResponse(
                    id=r.id,
                    name=r.name,
                    provider_type=r.provider_type,
                    base_url=r.base_url,
                    api_key=cls.mask_api_key(r.api_key),
                    has_api_key=bool(r.api_key and r.api_key.strip()),
                    is_active=r.is_active,
                    timeout_seconds=r.timeout_seconds,
                    custom_headers=r.custom_headers if isinstance(r.custom_headers, dict) else {},
                    models=model_items,
                    models_count=len(model_items),
                    public_models_count=public_count,
                    description=r.description,
                    sort_order=r.sort_order,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
            )
        return result

    @classmethod
    async def get_provider_entity(cls, db: AsyncSession, provider_id: uuid.UUID) -> SystemLLMProvider:
        """获取指定渠道 ORM 实体 (含明文密钥，供内部流式调用与更新使用)。"""
        stmt = select(SystemLLMProvider).where(SystemLLMProvider.id == provider_id)
        res = await db.execute(stmt)
        entity = res.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=404, detail=f"未找到 ID 为 {provider_id} 的 API 渠道配置")
        return entity

    @classmethod
    async def create_provider(cls, db: AsyncSession, payload: LLMProviderCreate) -> LLMProviderResponse:
        """新建一个大模型 API 提供商实体。"""
        new_row = SystemLLMProvider(
            name=payload.name.strip(),
            provider_type=payload.provider_type,
            base_url=payload.base_url.strip().rstrip("/"),
            api_key=payload.api_key.strip(),
            is_active=payload.is_active,
            timeout_seconds=payload.timeout_seconds,
            custom_headers=payload.custom_headers,
            models=[m.model_dump() for m in payload.models],
            description=payload.description,
            sort_order=payload.sort_order,
        )
        db.add(new_row)
        await db.commit()
        await db.refresh(new_row)
        logger.info("已创建大模型 API 渠道: ID=%s, 名称=%s", new_row.id, new_row.name)

        model_items = [LLMModelItem.model_validate(m) for m in (new_row.models or [])]
        public_count = sum(1 for m in model_items if m.is_public and m.is_enabled)
        return LLMProviderResponse(
            id=new_row.id,
            name=new_row.name,
            provider_type=new_row.provider_type,
            base_url=new_row.base_url,
            api_key=cls.mask_api_key(new_row.api_key),
            has_api_key=bool(new_row.api_key),
            is_active=new_row.is_active,
            timeout_seconds=new_row.timeout_seconds,
            custom_headers=new_row.custom_headers or {},
            models=model_items,
            models_count=len(model_items),
            public_models_count=public_count,
            description=new_row.description,
            sort_order=new_row.sort_order,
            created_at=new_row.created_at,
            updated_at=new_row.updated_at,
        )

    @classmethod
    async def update_provider(
        cls, db: AsyncSession, provider_id: uuid.UUID, payload: LLMProviderUpdate
    ) -> LLMProviderResponse:
        """更新指定已有渠道的配置。"""
        entity = await cls.get_provider_entity(db, provider_id)

        if payload.name is not None:
            entity.name = payload.name.strip()
        if payload.provider_type is not None:
            entity.provider_type = payload.provider_type
        if payload.base_url is not None:
            entity.base_url = payload.base_url.strip().rstrip("/")
        if payload.api_key is not None:
            # 防御：如果传入包含星号 ****，说明未修改原密钥，保持原样
            if "****" not in payload.api_key:
                entity.api_key = payload.api_key.strip()
        if payload.is_active is not None:
            entity.is_active = payload.is_active
        if payload.timeout_seconds is not None:
            entity.timeout_seconds = payload.timeout_seconds
        if payload.custom_headers is not None:
            entity.custom_headers = payload.custom_headers
        if payload.models is not None:
            entity.models = [m.model_dump() for m in payload.models]
            flag_modified(entity, "models")
        if payload.description is not None:
            entity.description = payload.description
        if payload.sort_order is not None:
            entity.sort_order = payload.sort_order

        await db.commit()
        await db.refresh(entity)
        logger.info("已更新大模型 API 渠道: ID=%s, 名称=%s", entity.id, entity.name)

        model_items = [LLMModelItem.model_validate(m) for m in (entity.models or [])]
        public_count = sum(1 for m in model_items if m.is_public and m.is_enabled)
        return LLMProviderResponse(
            id=entity.id,
            name=entity.name,
            provider_type=entity.provider_type,
            base_url=entity.base_url,
            api_key=cls.mask_api_key(entity.api_key),
            has_api_key=bool(entity.api_key),
            is_active=entity.is_active,
            timeout_seconds=entity.timeout_seconds,
            custom_headers=entity.custom_headers or {},
            models=model_items,
            models_count=len(model_items),
            public_models_count=public_count,
            description=entity.description,
            sort_order=entity.sort_order,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @classmethod
    async def delete_provider(cls, db: AsyncSession, provider_id: uuid.UUID) -> bool:
        """删除指定大模型 API 渠道。"""
        entity = await cls.get_provider_entity(db, provider_id)
        await db.delete(entity)
        await db.commit()
        logger.info("已删除大模型 API 渠道: ID=%s", provider_id)
        return True

    @classmethod
    async def toggle_provider_active(cls, db: AsyncSession, provider_id: uuid.UUID) -> LLMProviderResponse:
        """切换渠道启用/停用状态。"""
        entity = await cls.get_provider_entity(db, provider_id)
        entity.is_active = not entity.is_active
        await db.commit()
        await db.refresh(entity)
        model_items = [LLMModelItem.model_validate(m) for m in (entity.models or [])]
        public_count = sum(1 for m in model_items if m.is_public and m.is_enabled)
        return LLMProviderResponse(
            id=entity.id,
            name=entity.name,
            provider_type=entity.provider_type,
            base_url=entity.base_url,
            api_key=cls.mask_api_key(entity.api_key),
            has_api_key=bool(entity.api_key),
            is_active=entity.is_active,
            timeout_seconds=entity.timeout_seconds,
            custom_headers=entity.custom_headers or {},
            models=model_items,
            models_count=len(model_items),
            public_models_count=public_count,
            description=entity.description,
            sort_order=entity.sort_order,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @classmethod
    async def toggle_model_public(
        cls, db: AsyncSession, provider_id: uuid.UUID, model_id: str
    ) -> LLMProviderResponse:
        """切换特定模型的客户端上架状态 (is_public)。"""
        entity = await cls.get_provider_entity(db, provider_id)
        raw_models = entity.models if isinstance(entity.models, list) else []
        new_models: list[dict[str, Any]] = []
        found = False
        for m in raw_models:
            if isinstance(m, dict):
                item = dict(m)
                if str(item.get("id")) == model_id:
                    item["is_public"] = not item.get("is_public", True)
                    found = True
                new_models.append(item)
        if not found:
            # 防御性自愈：如果当前渠道尚未持久化收录该模型标识，自动补录为一个已上架模型，杜绝 404 脱节
            logger.warning(
                "toggle_model_public: 模型 %s 未在渠道 %s 现有列表中收录，已自动补录并激活客户端上架状态",
                model_id,
                provider_id,
            )
            new_models.append({
                "id": model_id,
                "label": model_id,
                "is_enabled": True,
                "is_public": True,
                "context_window": 128000,
                "max_tokens": 4096,
                "supports_streaming": True,
                "supports_tools": True,
                "supports_vision": False,
                "pricing": {"prompt": 0.0, "completion": 0.0},
            })
        entity.models = new_models
        flag_modified(entity, "models")
        await db.commit()
        await db.refresh(entity)
        model_items = [LLMModelItem.model_validate(m) for m in (entity.models or [])]
        public_count = sum(1 for m in model_items if m.is_public and m.is_enabled)
        return LLMProviderResponse(
            id=entity.id,
            name=entity.name,
            provider_type=entity.provider_type,
            base_url=entity.base_url,
            api_key=cls.mask_api_key(entity.api_key),
            has_api_key=bool(entity.api_key),
            is_active=entity.is_active,
            timeout_seconds=entity.timeout_seconds,
            custom_headers=entity.custom_headers or {},
            models=model_items,
            models_count=len(model_items),
            public_models_count=public_count,
            description=entity.description,
            sort_order=entity.sort_order,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @classmethod
    async def test_connection(
        cls, db: AsyncSession, req: LLMTestConnectionRequest
    ) -> LLMTestConnectionResponse:
        """向目标端点发起连通性探测 (Ping 测速并解析远端可用性)。"""
        # 1. 解析真实 API Key
        real_api_key = req.api_key.strip() if req.api_key else ""
        if (not real_api_key or "****" in real_api_key) and req.provider_id:
            try:
                entity = await cls.get_provider_entity(db, req.provider_id)
                real_api_key = entity.api_key
            except Exception as e:
                logger.warning("获取数据库历史 API Key 失败: %s", e)

        base_url = req.base_url.strip().rstrip("/")
        if not base_url.startswith(("http://", "https://")):
            return LLMTestConnectionResponse(
                success=False,
                latency_ms=0,
                message="Base URL 必须以 http:// 或 https:// 开头",
            )

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": "SpikeAI-Admin/1.0",
        }
        if real_api_key:
            headers["Authorization"] = f"Bearer {real_api_key}"
        if req.custom_headers:
            headers.update(req.custom_headers)

        target_url = f"{base_url}/models"
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
                resp = await client.get(target_url, headers=headers)
                latency = round((time.time() - start_time) * 1000)

                if resp.status_code == 200:
                    model_count = 0
                    try:
                        data = resp.json()
                        if isinstance(data, dict) and isinstance(data.get("data"), list):
                            model_count = len(data["data"])
                        elif isinstance(data, list):
                            model_count = len(data)
                    except Exception:
                        pass
                    return LLMTestConnectionResponse(
                        success=True,
                        latency_ms=latency,
                        status_code=200,
                        discovered_models_count=model_count,
                        message=f"连通性测试通过！响应延迟: {latency}ms"
                        + (f"，探测到 {model_count} 个远端模型" if model_count > 0 else ""),
                    )
                else:
                    err_snippet = resp.text[:120].strip()
                    return LLMTestConnectionResponse(
                        success=False,
                        latency_ms=latency,
                        status_code=resp.status_code,
                        message=f"上游服务响应状态码 {resp.status_code}: {err_snippet}",
                    )
        except httpx.TimeoutException:
            latency = round((time.time() - start_time) * 1000)
            return LLMTestConnectionResponse(
                success=False,
                latency_ms=latency,
                message=f"请求上游 Base URL 超时 (15s 未响应)，请检查网络与代理配置",
            )
        except httpx.ConnectError as err:
            return LLMTestConnectionResponse(
                success=False,
                latency_ms=0,
                message=f"网络连接失败，无法接入目标端点: {err}",
            )
        except Exception as err:
            logger.exception("连通性测试未捕获异常: %s", err)
            return LLMTestConnectionResponse(
                success=False,
                latency_ms=0,
                message=f"连通性探测异常: {str(err)}",
            )

    @classmethod
    async def fetch_upstream_models(
        cls, db: AsyncSession, req: LLMFetchModelsRequest
    ) -> LLMFetchModelsResponse:
        """请求上游 /models 接口在线拉取该 Key 支持的全部模型列表。"""
        real_api_key = req.api_key.strip() if req.api_key else ""
        if (not real_api_key or "****" in real_api_key) and req.provider_id:
            try:
                entity = await cls.get_provider_entity(db, req.provider_id)
                real_api_key = entity.api_key
            except Exception as e:
                logger.warning("获取数据库历史 API Key 失败: %s", e)

        base_url = req.base_url.strip().rstrip("/")
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": "SpikeAI-Admin/1.0",
        }
        if real_api_key:
            headers["Authorization"] = f"Bearer {real_api_key}"
        if req.custom_headers:
            headers.update(req.custom_headers)

        target_url = f"{base_url}/models"
        try:
            async with httpx.AsyncClient(timeout=20.0, verify=False) as client:
                resp = await client.get(target_url, headers=headers)
                if resp.status_code != 200:
                    return LLMFetchModelsResponse(
                        success=False,
                        models=[],
                        message=f"拉取模型失败，HTTP 状态码 {resp.status_code}: {resp.text[:120]}",
                    )
                data = resp.json()
                model_ids: list[str] = []
                if isinstance(data, dict) and isinstance(data.get("data"), list):
                    for item in data["data"]:
                        if isinstance(item, dict) and item.get("id"):
                            model_ids.append(str(item["id"]))
                        elif isinstance(item, str):
                            model_ids.append(item)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("id"):
                            model_ids.append(str(item["id"]))
                        elif isinstance(item, str):
                            model_ids.append(item)

                # 去重并排序
                sorted_ids = sorted(list(set(model_ids)))
                return LLMFetchModelsResponse(
                    success=True,
                    models=sorted_ids,
                    message=f"成功在线拉取到 {len(sorted_ids)} 个上游可用模型",
                )
        except Exception as e:
            logger.exception("拉取模型发生异常: %s", e)
            return LLMFetchModelsResponse(
                success=False,
                models=[],
                message=f"网络请求失败: {str(e)}",
            )

    @classmethod
    async def get_public_models_for_client(cls, db: AsyncSession) -> list[ClientModelItem]:
        """获取所有已启用且上架到客户端 (is_public=True) 的可用大模型列表。

        用于 C 端聊天界面模型选择器与更多模型市场。绝对脱敏，绝不下发 API Key / Base URL。
        """
        stmt = (
            select(SystemLLMProvider)
            .where(SystemLLMProvider.is_active.is_(True))
            .order_by(SystemLLMProvider.sort_order.desc())
        )
        res = await db.execute(stmt)
        providers = res.scalars().all()

        if not providers:
            # 自动初始化基线
            providers = await cls.seed_default_providers(db)

        client_models: list[ClientModelItem] = []
        seen_ids: set[str] = set()

        for p in providers:
            raw_models = p.models if isinstance(p.models, list) else []
            for m in raw_models:
                if not isinstance(m, dict):
                    continue
                mid = str(m.get("id", "")).strip()
                if not mid or mid in seen_ids:
                    continue

                # 必须满足 is_enabled 且 is_public
                is_enabled = bool(m.get("is_enabled", True))
                is_public = bool(m.get("is_public", True))
                if not (is_enabled and is_public):
                    continue

                seen_ids.add(mid)
                display_name = m.get("display_name") or mid
                cost = int(m.get("cost", 1))
                supports_reasoning = bool(m.get("supports_reasoning", False))
                is_default = bool(m.get("is_default", False))
                family = str(m.get("family", "other")).lower()
                if not family or family == "other":
                    if "deepseek" in mid.lower():
                        family = "deepseek"
                    elif "gpt" in mid.lower() or "o1" in mid.lower():
                        family = "gpt"
                    elif "claude" in mid.lower():
                        family = "claude"
                    elif "gemini" in mid.lower():
                        family = "gemini"

                category = "advanced" if (supports_reasoning or cost >= 2) else "normal"

                client_models.append(
                    ClientModelItem(
                        id=mid,
                        name=display_name,
                        familyId=family,
                        category=category,
                        health=99 if not supports_reasoning else 98,
                        cost=cost,
                        starCost=cost,
                        moonCost=cost,
                        freeCountText=f"★ {cost} / 次",
                        isStreaming=bool(m.get("supports_streaming", True)),
                        supportsReasoning=supports_reasoning,
                        isFavorite=is_default,
                        isDefault=is_default,
                    )
                )

        # 若没有任何上架模型，兜底默认模型
        if not client_models:
            client_models = [
                ClientModelItem(
                    id="deepseek-chat",
                    name="DeepSeek-V3 旗舰大模型",
                    familyId="deepseek",
                    category="normal",
                    health=99,
                    cost=1,
                    starCost=1,
                    moonCost=1,
                    freeCountText="★ 1 / 次",
                    isStreaming=True,
                    supportsReasoning=False,
                    isFavorite=True,
                    isDefault=True,
                ),
                ClientModelItem(
                    id="deepseek-reasoner",
                    name="DeepSeek-R1 深度思考",
                    familyId="deepseek",
                    category="advanced",
                    health=98,
                    cost=2,
                    starCost=2,
                    moonCost=2,
                    freeCountText="★ 2 / 次",
                    isStreaming=True,
                    supportsReasoning=True,
                    isFavorite=False,
                    isDefault=False,
                ),
            ]
        return client_models

    @classmethod
    async def get_provider_credentials_for_model(
        cls, db: AsyncSession, model_id: str
    ) -> tuple[str, str, dict[str, str], int] | None:
        """根据 model_id 查找当前活跃的提供商 Base URL, API Key, Custom Headers, Timeout。

        若查到，返回 (base_url, api_key, custom_headers, timeout_seconds)；若未配置返回 None。
        """
        stmt = (
            select(SystemLLMProvider)
            .where(SystemLLMProvider.is_active.is_(True))
            .order_by(SystemLLMProvider.sort_order.desc())
        )
        res = await db.execute(stmt)
        providers = res.scalars().all()

        for p in providers:
            raw_models = p.models if isinstance(p.models, list) else []
            for m in raw_models:
                if isinstance(m, dict) and m.get("id") == model_id and m.get("is_enabled", True):
                    return (
                        p.base_url,
                        p.api_key,
                        p.custom_headers if isinstance(p.custom_headers, dict) else {},
                        p.timeout_seconds or 60,
                    )
        return None

    @classmethod
    async def check_model_supports_reasoning(
        cls, db: AsyncSession, model_id: str
    ) -> bool:
        """查询指定 model_id 在系统活跃渠道配置中是否开启了深度思考 (Reasoning)。

        若配置了 supports_reasoning，严格以该字段布尔值为准；
        若未配置或未找到，仅当模型 ID 明确包含 reasoner / r1 / o1 / o3 等知名推理特征时才兜底为 True，
        其余默认严格为 False (未开启深度思考)。

        Args:
            db: 异步数据库 Session
            model_id: 模型唯一标识符

        Returns:
            bool: 是否支持并启用深度思考链输出

        Usage:
            >>> is_thinking_enabled = await LLMService.check_model_supports_reasoning(db, "deepseek-v4-flash")
        """
        stmt = (
            select(SystemLLMProvider)
            .where(SystemLLMProvider.is_active.is_(True))
            .order_by(SystemLLMProvider.sort_order.desc())
        )
        res = await db.execute(stmt)
        providers = res.scalars().all()

        for p in providers:
            raw_models = p.models if isinstance(p.models, list) else []
            for m in raw_models:
                if isinstance(m, dict) and m.get("id") == model_id:
                    # 严格遵循管理员在后台配置的布尔开关
                    if "supports_reasoning" in m:
                        return bool(m.get("supports_reasoning"))

        # 回退兜底：仅限明确的纯推理大模型标识
        m_lower = model_id.lower()
        if any(keyword in m_lower for keyword in ["deepseek-reasoner", "deepseek-r1", "o1-preview", "o1-mini", "o3-mini"]):
            return True
        return False

