"""大模型 API 渠道与模型上架服务自动化测试套件。

验证:
1. API Key 脱敏处理逻辑；
2. 出厂默认 API 供应商自动建表初始化 (DeepSeek + OpenAI)；
3. 新增、更新与删除供应商渠道配置；
4. 切换渠道活跃状态 (is_active)；
5. 切换特定模型的客户端公开上架状态 (is_public)；
6. 客户端安全模型列表下发聚合 (get_public_models_for_client)；
7. 动态网关凭证解析 (get_provider_credentials_for_model)。

Usage:
    pytest backend/tests/test_llm_service.py -v
"""

import uuid
import pytest

from app.schemas.llm import (
    LLMModelItem,
    LLMProviderCreate,
    LLMProviderUpdate,
    LLMTestConnectionRequest,
)
from app.services.llm_service import LLMService
from tests.conftest import TestAsyncSessionLocal


@pytest.mark.asyncio
async def test_mask_api_key() -> None:
    """测试 API 密钥安全掩码脱敏函数。"""
    assert LLMService.mask_api_key("") == ""
    assert LLMService.mask_api_key(None) == ""
    assert LLMService.mask_api_key("12345678") == "sk-****"
    assert LLMService.mask_api_key("sk-abcdefgh12345678") == "sk-a****5678"


@pytest.mark.asyncio
async def test_llm_service_crud_and_client_models() -> None:
    """测试供应商渠道完整 CRUD 流程与 C 端模型下发联动。"""
    async with TestAsyncSessionLocal() as db:
        # 1. 查询渠道列表，初始应触发自动种入默认渠道
        providers = await LLMService.list_providers(db=db)
        assert len(providers) >= 2
        provider_names = [p.name for p in providers]
        assert "DeepSeek 官方 API" in provider_names

        # 2. 新建一个自定义反代渠道
        new_payload = LLMProviderCreate(
            name="硅基流动 SiliconFlow",
            provider_type="openai",
            base_url="https://api.siliconflow.cn/v1",
            api_key="sk-siliconflow-secret-key-9999",
            is_active=True,
            timeout_seconds=45,
            custom_headers={"X-Test-Channel": "SiliconFlow"},
            models=[
                LLMModelItem(
                    id="Qwen/Qwen2.5-72B-Instruct",
                    display_name="通义千问 2.5 72B",
                    is_enabled=True,
                    is_public=True,
                    is_default=False,
                    supports_streaming=True,
                    supports_reasoning=False,
                    cost=1,
                    family="qwen",
                    context_limit=32000,
                    sort_order=60,
                )
            ],
            description="硅基流动大模型中转平台",
            sort_order=75,
        )
        created = await LLMService.create_provider(db=db, payload=new_payload)
        assert created.name == "硅基流动 SiliconFlow"
        assert created.has_api_key is True
        assert "****" in created.api_key  # 返回已脱敏
        channel_id = created.id

        # 3. 验证 C 端获取上架模型包含该新模型
        client_models = await LLMService.get_public_models_for_client(db=db)
        client_model_ids = [m.id for m in client_models]
        assert "Qwen/Qwen2.5-72B-Instruct" in client_model_ids

        # 4. 验证动态网关凭证解析
        creds = await LLMService.get_provider_credentials_for_model(db=db, model_id="Qwen/Qwen2.5-72B-Instruct")
        assert creds is not None
        base_url, api_key, headers, timeout = creds
        assert base_url == "https://api.siliconflow.cn/v1"
        assert api_key == "sk-siliconflow-secret-key-9999"  # 真实明文凭证供网关调用
        assert headers.get("X-Test-Channel") == "SiliconFlow"
        assert timeout == 45

        # 5. 切换特定模型上架状态 (下架)
        updated_provider = await LLMService.toggle_model_public(
            db=db, provider_id=channel_id, model_id="Qwen/Qwen2.5-72B-Instruct"
        )
        target_model = next(m for m in updated_provider.models if m.id == "Qwen/Qwen2.5-72B-Instruct")
        assert target_model.is_public is False

        # 再次获取 C 端模型，该模型应已被剔除
        client_models_after = await LLMService.get_public_models_for_client(db=db)
        assert "Qwen/Qwen2.5-72B-Instruct" not in [m.id for m in client_models_after]

        # 6. 切换渠道激活状态 (停用渠道)
        disabled_provider = await LLMService.toggle_provider_active(db=db, provider_id=channel_id)
        assert disabled_provider.is_active is False

        # 7. 更新渠道配置（测试带星号密钥不覆盖）
        update_payload = LLMProviderUpdate(
            name="硅基流动 SiliconFlow (更新版)",
            api_key="sk-s****9999",  # 包含星号，不应覆盖原明文密钥
            timeout_seconds=50,
        )
        updated_after_mask = await LLMService.update_provider(db=db, provider_id=channel_id, payload=update_payload)
        assert updated_after_mask.name == "硅基流动 SiliconFlow (更新版)"
        assert updated_after_mask.timeout_seconds == 50

        # 验证底层真实密钥未被破坏
        entity = await LLMService.get_provider_entity(db=db, provider_id=channel_id)
        assert entity.api_key == "sk-siliconflow-secret-key-9999"

        # 8. 删除渠道
        deleted = await LLMService.delete_provider(db=db, provider_id=channel_id)
        assert deleted is True


@pytest.mark.asyncio
async def test_llm_test_connection_invalid_url() -> None:
    """测试非法 Base URL 连通性测试防御校验。"""
    async with TestAsyncSessionLocal() as db:
        req = LLMTestConnectionRequest(
            base_url="invalid-host-without-protocol",
            api_key="sk-test",
        )
        resp = await LLMService.test_connection(db=db, req=req)
        assert resp.success is False
        assert "http://" in resp.message


@pytest.mark.asyncio
async def test_llm_toggle_unrecorded_model_self_healing() -> None:
    """测试当切换未收录/新拉取的模型状态时，后端自动自愈补录并不抛出 404。"""
    async with TestAsyncSessionLocal() as db:
        create_payload = LLMProviderCreate(
            name="自愈测试供应商",
            provider_type="openai",
            base_url="https://api.openai.com/v1",
            api_key="sk-healing-test-key",
            is_active=True,
            models=[],
        )
        provider = await LLMService.create_provider(db=db, payload=create_payload)

        # 直接切换一个库里不存在的模型上架状态
        new_model_id = "deepseek-v4-flash-vision-exp"
        healed_provider = await LLMService.toggle_model_public(
            db=db,
            provider_id=provider.id,
            model_id=new_model_id,
        )

        # 验证该模型被自愈补录并上架
        found = next((m for m in healed_provider.models if m.id == new_model_id), None)
        assert found is not None
        assert found.is_public is True
        assert found.is_enabled is True

        # 清理
        await LLMService.delete_provider(db=db, provider_id=provider.id)

