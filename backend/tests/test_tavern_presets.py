"""SillyTavern 预设库 CRUD 自动化单元测试。

验证预设库列表、按 ID 详情查询、新建导入、更新、激活与删除等全流程。
"""

import uuid
import pytest
from fastapi import HTTPException

from app.services.tavern_service import TavernService
from tests.conftest import TestAsyncSessionLocal


@pytest.mark.asyncio
async def test_preset_crud_flow():
    async with TestAsyncSessionLocal() as session:
        # 1. 列表查询（冷启动若为空则初始化）
        presets = await TavernService.list_presets(session)
        assert len(presets) >= 1
        first = presets[0]
        first_id = first["id"]

        # 2. 按 ID 获取
        loaded = await TavernService.get_preset_by_id(session, uuid.UUID(first_id))
        assert loaded.preset_name == first["preset_name"]

        # 3. 创建新预设 (非激活)
        new_cfg = loaded.model_copy(deep=True)
        new_cfg.preset_name = "测试自定义预设"
        new_cfg.is_active = False
        new_cfg.temperature = 0.88
        created = await TavernService.create_preset(
            session,
            new_cfg,
            admin_user="tester",
            is_active=False,
            description="单元测试创建预设",
        )
        new_id = uuid.UUID(created["id"])
        assert created["preset_name"] == "测试自定义预设"

        # 4. 重命名
        renamed = await TavernService.rename_preset(session, new_id, "更名后的自定义预设", "tester")
        assert renamed["preset_name"] == "更名后的自定义预设"

        # 5. 更新配置
        new_cfg.preset_name = "更名后的自定义预设"
        new_cfg.is_active = False
        new_cfg.top_p = 0.95
        updated = await TavernService.update_preset_by_id(session, new_id, new_cfg, "tester")
        assert updated["preset_name"] == "更名后的自定义预设"

        # 6. 删除该非激活预设
        deleted = await TavernService.delete_preset(session, new_id)
        assert deleted is True

        # 7. 验证删除后 404
        with pytest.raises(HTTPException) as exc_info:
            await TavernService.get_preset_by_id(session, new_id)
        assert exc_info.value.status_code == 404

        # 8. 验证删除生效中的预设会被拒绝 (400)
        with pytest.raises(HTTPException) as active_exc:
            await TavernService.delete_preset(session, uuid.UUID(first_id))
        assert active_exc.value.status_code == 400


@pytest.mark.asyncio
async def test_preset_prompt_order_normalization():
    """验证方案 A：prompts 包含备选提示词时，自动补齐至 prompt_order 末尾且默认 enabled=False。"""
    from app.schemas.tavern import TavernPresetConfig, TavernPromptItem, TavernPromptOrderItem

    async with TestAsyncSessionLocal() as session:
        prompts = [
            TavernPromptItem(identifier="p1", name="提示词1", content="内容1", enabled=True),
            TavernPromptItem(identifier="p2", name="提示词2", content="内容2", enabled=True),
            TavernPromptItem(identifier="p3", name="备选3", content="备选内容3", enabled=False),
            TavernPromptItem(identifier="p4", name="备选4", content="备选内容4", enabled=False),
        ]
        prompt_order = [
            TavernPromptOrderItem(identifier="p1", enabled=True),
            TavernPromptOrderItem(identifier="p2", enabled=True),
        ]
        cfg = TavernPresetConfig(
            preset_name="多备选提示词测试预设",
            is_active=False,
            prompts=prompts,
            prompt_order=prompt_order,
        )

        # 验证 normalize_prompt_order
        normalized = TavernService.normalize_prompt_order(cfg)
        assert len(normalized.prompt_order) == 4
        assert normalized.prompt_order[0].identifier == "p1"
        assert normalized.prompt_order[0].enabled is True
        assert normalized.prompt_order[0].is_unordered_backup is False
        assert normalized.prompt_order[2].identifier == "p3"
        assert normalized.prompt_order[2].enabled is False
        assert normalized.prompt_order[2].is_unordered_backup is True
        assert normalized.prompt_order[3].identifier == "p4"
        assert normalized.prompt_order[3].enabled is False
        assert normalized.prompt_order[3].is_unordered_backup is True

        # 验证持久化和读取
        created = await TavernService.create_preset(session, cfg, admin_user="tester")
        created_id = uuid.UUID(created["id"])
        loaded = await TavernService.get_preset_by_id(session, created_id)
        assert len(loaded.prompt_order) == 4
        assert loaded.prompt_order[2].is_unordered_backup is True
        assert loaded.prompt_order[2].enabled is False

        # 清理
        await TavernService.delete_preset(session, created_id)
