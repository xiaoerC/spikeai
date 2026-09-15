"""SillyTavern 酒馆调音台与提示词排版流水线单元测试。"""

import pytest
from httpx import AsyncClient
from app.schemas.tavern import TavernPresetConfig
from app.services.tavern_service import TavernService


@pytest.mark.asyncio
async def test_tavern_default_preset_loading():
    """测试默认仓鼠之神V2预设是否完整加载。"""
    preset = TavernService.get_default_preset()
    assert preset.preset_name == "仓鼠之神V2"
    assert preset.temperature == 1.0
    assert preset.openai_max_context == 2000000
    assert preset.openai_max_tokens == 32000
    assert len(preset.prompts) > 30
    assert len(preset.prompt_order) > 30


@pytest.mark.asyncio
async def test_tavern_assemble_prompt_order():
    """测试酒馆提示词动态装配逻辑。"""
    preset = TavernService.get_default_preset()
    context = {
        "character_name": "博人",
        "character_desc": "木叶忍者",
        "character_personality": "热血叛逆",
        "scenario": "火影岩上",
        "user_name": "鸣人",
        "user_persona": "七代目火影",
        "history_messages": [
            {"role": "user", "content": "你好，博人"},
            {"role": "assistant", "content": "切，老爸又来了"},
        ],
    }
    messages, params = TavernService.assemble_tavern_messages_and_params(preset, context)
    assert len(messages) > 0
    assert params["temperature"] == 1.0
    assert params["max_tokens"] <= 8192

    # 验证动态插桩内容被正确渲染
    all_content = "\n".join(m["content"] for m in messages)
    assert "木叶忍者" in all_content or "热血叛逆" in all_content or "七代目火影" in all_content
