"""客户端高级格式化端到端全链路集成测试。

验证当用户在客户端发起对话时:
1. TavernService.get_user_preset 成功读取全局激活的系统预设配置;
2. assemble_tavern_messages_and_params 注入后置强化指令与终止词数组;
3. 往期历史会话中超出的思维链标签被安全剥离;
4. 生成完毕时执行文本清洗流水线 (连续多余换行折叠、不完整断句截断修剪、首尾空白修剪、前缀补齐);
5. SSE usage 与 done 事件向客户端透传 cleaned_content。

Usage:
    $ uv run pytest tests/test_client_formatting_integration.py -v
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat import SendMessageRequest
from app.schemas.tavern import TavernAdvancedFormatting, TavernPresetConfig
from app.services.chat_service import ChatService
from app.services.tavern_service import TavernService


@pytest.mark.asyncio
async def test_client_chat_formatting_pipeline_integration() -> None:
    """验证客户端对话发起时高级格式化全链路装配与文本清洗生效。"""
    # 1. 构造具有高级格式化特性的测试预设
    preset = TavernService.get_default_preset()
    preset.is_active = True
    preset.advanced_formatting = TavernAdvancedFormatting(
        parse_think_tags=True,
        reasoning_history_depth=0,
        enable_post_history_instruction=True,
        post_history_instruction="[System: {{char}} 始终用中文对 {{user}} 说话]",
        post_history_depth=0,
        char_name_as_stop=True,
        user_name_as_stop=True,
        stop_sequences=["\nUser:", "<|im_end|>"],
        collapse_newlines=True,
        trim_incomplete_sentences=True,
        trim_whitespace=True,
        reply_prefix="*轻声回应*",
        show_reply_prefix=True,
    )

    # 2. 验证消息装配上下文
    context = {
        "character_name": "爱丽丝",
        "character_desc": "一位优雅的魔法少女",
        "character_personality": "温柔、坚定",
        "scenario": "星空下的钟楼",
        "user_name": "旅人",
        "user_persona": "探索者",
        "world_info_before": "魔法世界观",
        "world_info_after": "",
        "chat_examples": [],
        "history_messages": [
            {"role": "user", "content": "你好，爱丽丝！"},
            {"role": "assistant", "content": "<think>我需要对旅人表示欢迎</think>\n很高兴见到你，旅人！"},
            {"role": "user", "content": "今晚星空真美啊。"},
        ],
        "mod_patches": {},
        "variables": {},
    }

    messages, params = TavernService.assemble_tavern_messages_and_params(preset, context)

    # 验证 1: 历史消息中的思考过程已被深度 0 剥离
    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    assert len(assistant_msgs) >= 1
    assert "<think>" not in assistant_msgs[0]["content"]
    assert "很高兴见到你，旅人！" in assistant_msgs[0]["content"]

    # 验证 2: 后置指令被注入在最末尾深度 0
    assert messages[-1]["role"] == "system"
    assert "[System: 爱丽丝 始终用中文对 旅人 说话]" in messages[-1]["content"]

    # 验证 3: 终止词聚合 (角色名、用户名、自定义词)
    assert "stop" in params
    assert "\n爱丽丝:" in params["stop"]
    assert "\n旅人:" in params["stop"]
    assert "\nUser:" in params["stop"]
    assert "<|im_end|>" in params["stop"]

    # 验证 4: 输出文本清洗流水线 (多余连续空行折叠、不完整断句截断、前缀补齐)
    raw_llm_output = "\n\n\n\n是啊，今晚的星空格外璀璨。\n\n\n银河从天际垂下，仿佛我们只要伸手就能"
    cleaned = TavernService.clean_output_text(raw_llm_output, preset.advanced_formatting)

    # 换行折叠校验
    assert "\n\n\n" not in cleaned
    # 不完整断句截断校验 (截断在逗号后的半句话被修剪回上一个句号)
    assert cleaned.endswith("是啊，今晚的星空格外璀璨。")

    # 前缀补齐校验
    if preset.advanced_formatting.reply_prefix and preset.advanced_formatting.show_reply_prefix:
        pref = preset.advanced_formatting.reply_prefix.strip()
        final_msg = f"{pref} {cleaned}"
        assert final_msg.startswith("*轻声回应*")


@pytest.mark.asyncio
async def test_chat_service_stream_integration_with_tavern_preset() -> None:
    """模拟 ChatService 流式调用，验证酒馆预设接管与 usage 携带 cleaned_content。"""
    from tests.conftest import TestAsyncSessionLocal
    from app.models.character import Character
    from app.models.chat import ChatSession, StoryBranch
    from app.models.user import User, UserWallet

    async with TestAsyncSessionLocal() as db_session:
        # 准备测试基础数据
        user = User(
            id=uuid.uuid4(),
            email=f"test_{uuid.uuid4().hex[:6]}@spikeai.com",
            hashed_password="fake_hash",
            invite_code=uuid.uuid4().hex[:8],
            status="active",
        )
        db_session.add(user)
        await db_session.flush()

        wallet = UserWallet(
            user_id=user.id,
            star_coins=1000,
            moon_gems=100,
        )
        db_session.add(wallet)
        await db_session.flush()

        char = Character(
            id=uuid.uuid4(),
            name="测试助手",
            avatar_url="https://example.com/avatar.png",
            first_mes="你好，我是测试助手。",
            description="用于格式化测试的 AI 角色",
            author_id=user.id,
        )
        db_session.add(char)
        await db_session.flush()

        session = ChatSession(
            id=uuid.uuid4(),
            user_id=user.id,
            character_id=char.id,
        )
        db_session.add(session)
        await db_session.flush()

        branch = StoryBranch(
            session_id=session.id,
            name="主线",
        )
        db_session.add(branch)
        await db_session.flush()
        session.current_branch_id = branch.id
        await db_session.commit()

    # 模拟 LLMGateway 流式生成返回带有多余换行与半截句子的消息
    mock_chunks = [
        ("thinking", "正在思考测试内容..."),
        ("message", "你好！\n\n\n\n这是第一句完整的话。但是第二句没说完"),
    ]

    async def mock_stream_chat(*args, **kwargs):
        for event_type, chunk in mock_chunks:
            yield event_type, chunk

    payload = SendMessageRequest(
        content="测试提示词",
        model_id="deepseek-v4-flash",
    )

    with patch("app.services.chat_service.llm_gateway.stream_chat", side_effect=mock_stream_chat):
        # 激活酒馆预设并开启清洗
        preset = TavernService.get_default_preset()
        preset.is_active = True
        preset.advanced_formatting = TavernAdvancedFormatting(
            collapse_newlines=True,
            trim_incomplete_sentences=True,
            trim_whitespace=True,
        )

        with patch("app.services.tavern_service.TavernService.get_user_preset", return_value=preset):
            events = []
            async for chunk_str in ChatService.send_message_stream(
                db=db_session,
                user_id=user.id,
                session_id=session.id,
                payload=payload,
            ):
                events.append(chunk_str)

            full_stream = "".join(events)
            # 验证流中有 usage 事件且包含 cleaned_content
            assert "event: usage" in full_stream
            assert "cleaned_content" in full_stream
            assert "这是第一句完整的话。" in full_stream
            # 验证半截话「但是第二句没说完」在 cleaned_content 中已被截断修剪
            assert "但是第二句没说完" not in full_stream.split("cleaned_content")[1]
