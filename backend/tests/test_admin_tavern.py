"""Admin 全局酒馆调音台与系统级预设管理单元测试。

验证:
1. 管理员获取全平台全局生效预设；
2. 管理员更新并发布全局预设，验证热更新与数据库持久化；
3. 验证普通用户对话统一继承 Admin 全局生效预设 (方案 B)；
4. 验证一键恢复官方出厂默认「仓鼠之神V2」；
5. 验证预设模板列表与历史版本查询。

Usage:
    pytest backend/tests/test_admin_tavern.py -v
"""

import uuid
import pytest

from app.schemas.tavern import TavernPresetConfig
from app.services.tavern_service import TavernService
from tests.conftest import TestAsyncSessionLocal


@pytest.mark.asyncio
async def test_get_and_update_system_preset() -> None:
    """测试系统全局预设读取与落库更新。"""
    async with TestAsyncSessionLocal() as db:
        # 1. 初始读取系统全局预设
        initial = await TavernService.get_system_preset(db=db)
        assert initial.preset_name is not None
        assert len(initial.prompts) >= 70

        # 2. 修改参数并发布
        cloned = initial.model_copy(deep=True)
        cloned.temperature = 0.88
        cloned.preset_name = "Admin 质检调优版"
        # 修改第一项 Prompt
        cloned.prompts[0].content = "【系统特调指令】严格遵循客观事实。"

        updated = await TavernService.update_system_preset(
            db=db,
            updated=cloned,
            admin_user="test_super_admin",
            description="单元测试全平台热发布",
        )
        assert updated.temperature == 0.88
        assert updated.preset_name == "Admin 质检调优版"

        # 3. 再次获取，验证持久化与缓存命中
        current = await TavernService.get_system_preset(db=db)
        assert current.temperature == 0.88
        assert current.preset_name == "Admin 质检调优版"
        assert current.prompts[0].content == "【系统特调指令】严格遵循客观事实。"


@pytest.mark.asyncio
async def test_user_inherits_admin_global_preset() -> None:
    """测试方案 B：任意普通用户在对话时统一自动继承 Admin 全局生效预设。"""
    async with TestAsyncSessionLocal() as db:
        user_id = uuid.uuid4()

        # 1. 确保系统预设有特征参数
        preset = await TavernService.get_system_preset(db=db)
        preset.frequency_penalty = 0.42
        await TavernService.update_system_preset(db=db, updated=preset, admin_user="admin")

        # 2. 获取该用户的预设，确认 100% 继承全局预设
        user_preset = await TavernService.get_user_preset(user_id=user_id, db=db)
        assert user_preset.frequency_penalty == 0.42
        assert user_preset.preset_name == preset.preset_name


@pytest.mark.asyncio
async def test_reset_system_preset() -> None:
    """测试一键恢复官方出厂默认配置。"""
    async with TestAsyncSessionLocal() as db:
        # 1. 先修改参数
        preset = await TavernService.get_system_preset(db=db)
        preset.temperature = 1.99
        preset.preset_name = "临时异常配置"
        await TavernService.update_system_preset(db=db, updated=preset, admin_user="admin")

        # 2. 执行恢复出厂
        reset_preset = await TavernService.reset_system_preset(db=db, admin_user="admin")
        assert reset_preset.preset_name == "仓鼠之神V2"
        assert reset_preset.temperature == 1.0

        # 3. 验证再次查询也是仓鼠之神V2
        after = await TavernService.get_system_preset(db=db)
        assert after.preset_name == "仓鼠之神V2"


@pytest.mark.asyncio
async def test_list_system_presets() -> None:
    """测试预设模板与历史列表查询。"""
    async with TestAsyncSessionLocal() as db:
        presets = await TavernService.list_system_presets(db=db)
        assert len(presets) >= 1
        preset_names = [p["preset_name"] for p in presets]
        assert "仓鼠之神V2" in preset_names


@pytest.mark.asyncio
async def test_default_preset_and_injection_trigger() -> None:
    """测试出厂默认预设只读基准与 injection_trigger 结构。"""
    default_preset = TavernService.get_default_preset()
    assert default_preset.preset_name == "仓鼠之神V2"
    assert len(default_preset.prompts) > 0
    # 验证 injection_trigger 字段完整加载
    first_prompt = default_preset.prompts[0]
    assert hasattr(first_prompt, "injection_trigger")
    assert isinstance(first_prompt.injection_trigger, list)
