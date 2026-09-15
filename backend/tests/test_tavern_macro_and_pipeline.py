# -*- coding: utf-8 -*-
"""SillyTavern 调音台宏变量引擎、Mod 动态插桩与多预设管理单元测试。

验证:
1. {{char}}, {{user}}, {{setvar}}, {{getvar}}, {{// 注释}} 宏替换引擎正确性;
2. Mod 锚点 (system_prefix, before_char, after_char, bottom_an, user_suffix) 动态插桩;
3. 多预设创建、列表查询与切换。
"""

import uuid
import pytest
from app.services.tavern_service import TavernService
from app.schemas.tavern import TavernPresetConfig


@pytest.mark.asyncio
async def test_macro_engine_replacement():
    """测试高级宏替换与注释剥离。"""
    test_text = (
        "你好 {{user}}，我是 {{char}}！\n"
        "{{// 这是酒馆注释，不应出现在最终提示词中}}"
        "{{setvar::mood::开心}}"
        "当前心情是：{{getvar::mood}}，当前时空：{{location}}，血量：{{player_hp}}。"
    )
    context = {
        "character_name": "爱丽丝",
        "user_name": "旅人",
        "variables": {
            "location": "星空旅馆",
            "player_hp": 100,
        },
    }
    processed = TavernService.apply_macros(test_text, context)
    assert "{{char}}" not in processed
    assert "爱丽丝" in processed
    assert "{{user}}" not in processed
    assert "旅人" in processed
    assert "这是酒馆注释" not in processed
    assert "开心" in processed
    assert "星空旅馆" in processed
    assert "100" in processed


@pytest.mark.asyncio
async def test_mod_pipeline_injection():
    """测试 Mod 动态插桩无缝融合进酒馆装配流水线。"""
    preset = TavernService.get_default_preset()
    user_id = uuid.uuid4()

    mod_patches = {
        "system_prefix": ["【MOD: 顶级世界法则】绝对遵守逻辑自洽。"],
        "before_char": ["【MOD: 画师串】masterpiece, cinematic lighting."],
        "after_char": ["【MOD: 语气强化】带有慵懒而威严的声线。"],
        "bottom_an": ["【MOD: 描写增强】重点刻画微表情与环境音。"],
        "user_suffix": ["【MOD: 用户附加要求】请用优美的修辞结尾。"],
    }

    context = {
        "character_name": "星辰守护者",
        "user_name": "指挥官",
        "character_desc": "一位守护银河的机械神明。",
        "character_personality": "冷静、寡言。",
        "history_messages": [
            {"role": "user", "content": "告诉我前方的战况"},
            {"role": "assistant", "content": "星门稳定，敌军退却。"},
            {"role": "user", "content": "下一步该如何行动？"},
        ],
        "mod_patches": mod_patches,
    }

    messages, params = TavernService.assemble_tavern_messages_and_params(preset, context)
    assert len(messages) > 0

    # 验证 Mod 注入条目存在于 LLM 消息流中
    all_system_contents = "\n".join(m["content"] for m in messages if m["role"] == "system")
    assert "【MOD: 顶级世界法则】" in all_system_contents
    assert "【MOD: 画师串】" in all_system_contents
    assert "【MOD: 语气强化】" in all_system_contents
    assert "【MOD: 描写增强】" in all_system_contents

    # 验证 user_suffix 注入在最后一条 user 消息
    last_user_msg = [m for m in messages if m["role"] == "user"][-1]
    assert "【MOD: 用户附加要求】" in last_user_msg["content"]


@pytest.mark.asyncio
async def test_multi_preset_library():
    """测试多预设管理（列表查询、另存为自定义预设、删除自定义预设）。"""
    user_id = uuid.uuid4()

    # 1. 查询默认预设列表 (包含 3 套官方预设)
    presets = await TavernService.list_user_presets(user_id)
    preset_names = [p["preset_name"] for p in presets]
    assert "仓鼠之神V2" in preset_names
    assert "文学沉浸创作版" in preset_names
    assert "高自由度脑洞版" in preset_names

    # 2. 另存为用户自定义新预设
    custom_preset = TavernService.get_default_preset()
    custom_preset.preset_name = "我的极简微小说预设"
    custom_preset.temperature = 0.65
    await TavernService.save_named_preset(user_id, custom_preset)

    updated_presets = await TavernService.list_user_presets(user_id)
    updated_names = [p["preset_name"] for p in updated_presets]
    assert "我的极简微小说预设" in updated_names

    # 3. 删除自定义预设
    deleted = await TavernService.delete_named_preset(user_id, "我的极简微小说预设")
    assert deleted is True

    final_presets = await TavernService.list_user_presets(user_id)
    final_names = [p["preset_name"] for p in final_presets]
    assert "我的极简微小说预设" not in final_names
