"""酒馆高级格式化 (Advanced Formatting) 单元测试套件。

涵盖:
1. TavernAdvancedFormatting 架构数据校验;
2. clean_output_text 文本清洗流水线 (换行折叠、不完整句子回退、空白修剪);
3. 历史后置指令 (Post-History Instruction) 深度插桩装配;
4. 终止词 (Stop Sequences) 动态聚合与角色名/用户名拦截;
5. 历史多轮对话中思维链 (<think>) 深度回传控制 (reasoning_history_depth)。
"""

import pytest
from app.schemas.tavern import TavernAdvancedFormatting, TavernPresetConfig, TavernPromptItem
from app.services.tavern_service import TavernService


def test_advanced_formatting_defaults():
    """验证高级格式化默认属性值。"""
    fmt = TavernAdvancedFormatting()
    assert fmt.parse_think_tags is True
    assert fmt.reasoning_history_depth == 0
    assert fmt.auto_expand_reasoning is False
    assert fmt.enable_post_history_instruction is False
    assert fmt.collapse_newlines is True
    assert fmt.trim_incomplete_sentences is False
    assert fmt.trim_whitespace is True
    assert fmt.stop_sequences == []


def test_clean_output_text_collapse_newlines():
    """验证折叠 3 个以上多余换行符。"""
    fmt = TavernAdvancedFormatting(collapse_newlines=True)
    raw = "第一段\n\n\n\n\n第二段\n\n第三段"
    cleaned = TavernService.clean_output_text(raw, fmt)
    assert cleaned == "第一段\n\n第二段\n\n第三段"


def test_clean_output_text_trim_incomplete_sentences():
    """验证修剪因截断未闭合的半句话。"""
    fmt = TavernAdvancedFormatting(
        collapse_newlines=True,
        trim_incomplete_sentences=True,
        trim_whitespace=True,
    )
    raw = "天空中飘落着微雨。他转过身看着我，轻声说道：“不要走。”随后快步"
    cleaned = TavernService.clean_output_text(raw, fmt)
    # 应截断回最后一个闭合标点
    assert cleaned == "天空中飘落着微雨。他转过身看着我，轻声说道：“不要走。”"


def test_clean_output_text_full():
    """验证综合文本清洗。"""
    fmt = TavernAdvancedFormatting(
        collapse_newlines=True,
        trim_incomplete_sentences=True,
        trim_whitespace=True,
    )
    raw = "   \n\n\n雷鸣声轰然作响！\n\n\n大地在剧烈颤抖，似乎有什么东西要破土   "
    cleaned = TavernService.clean_output_text(raw, fmt)
    assert cleaned == "雷鸣声轰然作响！"


def test_assemble_post_history_instruction_depth_zero():
    """验证在末尾（深度 0）注入历史后置强化指令。"""
    preset = TavernPresetConfig(
        preset_name="测试后置指令预设",
        prompts=[
            TavernPromptItem(identifier="main_sys", name="主设定", content="你是一只仓鼠精", role="system", enabled=True),
            TavernPromptItem(identifier="chatHistory", name="历史", content="", role="system", marker=True, enabled=True),
        ],
        advanced_formatting=TavernAdvancedFormatting(
            enable_post_history_instruction=True,
            post_history_instruction="[System: 请务必牢记 {{char}} 是一只傲娇仓鼠，严禁自说自话]",
            post_history_depth=0,
        ),
    )

    context = {
        "character_name": "皮皮",
        "user_name": "指挥官",
        "history_messages": [
            {"role": "user", "content": "你好，皮皮"},
            {"role": "assistant", "content": "哼，本仓鼠才不理你呢！"},
            {"role": "user", "content": "今天吃什么？"},
        ],
    }

    messages, params = TavernService.assemble_tavern_messages_and_params(preset, context)

    # 验证最后一条消息为注入的系统后置指令
    last_msg = messages[-1]
    assert last_msg["role"] == "system"
    assert "[System: 请务必牢记 皮皮 是一只傲娇仓鼠，严禁自说自话]" in last_msg["content"]


def test_assemble_post_history_instruction_depth_one():
    """验证在倒数第 1 条消息之前（深度 1）注入后置指令。"""
    preset = TavernPresetConfig(
        preset_name="深度1后置测试",
        prompts=[
            TavernPromptItem(identifier="main_sys", name="主设定", content="系统规则", role="system", enabled=True),
            TavernPromptItem(identifier="chatHistory", name="历史", content="", role="system", marker=True, enabled=True),
        ],
        advanced_formatting=TavernAdvancedFormatting(
            enable_post_history_instruction=True,
            post_history_instruction="[System: 强化指令]",
            post_history_depth=1,
        ),
    )

    context = {
        "character_name": "皮皮",
        "user_name": "指挥官",
        "history_messages": [
            {"role": "user", "content": "消息1"},
            {"role": "assistant", "content": "消息2"},
            {"role": "user", "content": "消息3"},
        ],
    }

    messages, params = TavernService.assemble_tavern_messages_and_params(preset, context)
    # 倒数第二条应为该注入消息
    assert messages[-2]["role"] == "system"
    assert messages[-2]["content"] == "[System: 强化指令]"
    # 最后一条为原来的消息3
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == "消息3"


def test_assemble_stop_sequences_and_names():
    """验证终止词聚合与角色名/用户名终止词。"""
    preset = TavernPresetConfig(
        preset_name="终止词测试",
        prompts=[
            TavernPromptItem(identifier="sys", name="系统", content="系统提示", role="system", enabled=True),
        ],
        advanced_formatting=TavernAdvancedFormatting(
            stop_sequences=["\n[End]", "<|eot_id|>"],
            char_name_as_stop=True,
            user_name_as_stop=True,
        ),
    )

    context = {
        "character_name": "爱丽丝",
        "user_name": "探索者",
        "history_messages": [],
    }

    _, params = TavernService.assemble_tavern_messages_and_params(preset, context)
    stop_list = params.get("stop", [])
    assert "\n[End]" in stop_list
    assert "<|eot_id|>" in stop_list
    assert "\n爱丽丝:" in stop_list
    assert "\n探索者:" in stop_list


def test_assemble_reasoning_history_depth_control():
    """验证根据 reasoning_history_depth 裁剪较早轮次的思维链。"""
    preset = TavernPresetConfig(
        preset_name="思考链深度测试",
        prompts=[
            TavernPromptItem(identifier="chatHistory", name="历史", content="", role="system", marker=True, enabled=True),
        ],
        advanced_formatting=TavernAdvancedFormatting(
            parse_think_tags=True,
            reasoning_history_depth=1,  # 仅保留最近 1 条思考
        ),
    )

    context = {
        "history_messages": [
            {"role": "user", "content": "第一问"},
            {"role": "assistant", "content": "<think>第一问的秘密深度思考</think>这是第一回回复"},
            {"role": "user", "content": "第二问"},
            {"role": "assistant", "content": "<think>第二问的深度规划思考</think>这是第二回回复"},
        ],
    }

    messages, _ = TavernService.assemble_tavern_messages_and_params(preset, context)
    # 第一回 assistant 的思维链应被剔除
    m1 = [m for m in messages if m["content"] == "这是第一回回复"]
    assert len(m1) == 1
    assert "<think>" not in m1[0]["content"]

    # 最近的一回（第二回）assistant 的思维链应被保留
    m2 = [m for m in messages if "这是第二回回复" in m["content"]]
    assert len(m2) == 1
    assert "<think>第二问的深度规划思考</think>" in m2[0]["content"]
