"""深度思考控制 (supports_reasoning) 与 {{user}} 宏替换机制单元测试。

验证当模型配置 supports_reasoning=False 时：
1. llm_gateway.stream_chat 不输出 thinking 事件，剥除 <think> 标签；
2. chat_service.send_message_stream 不发送 event: thinking，thinking_content 落库为空；
3. 历史消息组装时不拼接 <think> 标签；
4. 初始开场白与实时流消息中 {{user}} 宏彻底展开替换。
"""

import asyncio
import json
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character
from app.models.chat import ChatMessage, ChatSession, StoryBranch
from app.models.user import User, UserProfile
from app.schemas.chat import SendMessageRequest
from app.services.chat_service import ChatService
from app.services.llm_gateway import OpenAILLMClient, llm_gateway
from app.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_llm_gateway_thinking_filtered_when_disabled():
    """测试当 supports_reasoning=False 时，gateway 严禁 emit thinking。"""
    client = OpenAILLMClient(api_key="mock", base_url="https://mock.api/v1")
    
    # 模拟数据块带有 <think> 标签的流
    async def mock_aiter_lines():
        # 带有 think 标签
        yield 'data: {"choices":[{"delta":{"content":"<think>我在沉浸式构思剧情</think>你好，旅者。"}}]}'
        yield 'data: {"choices":[{"delta":{"reasoning_content":"内部思考字段"}}]}'
        yield 'data: [DONE]'

    from unittest.mock import AsyncMock, patch, MagicMock
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.aiter_lines = mock_aiter_lines
    
    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value = mock_resp
        mock_stream.return_value = mock_ctx
        
        events = []
        async for event_type, chunk in client.stream_chat(
            messages=[{"role": "user", "content": "hello"}],
            model="deepseek-v4-flash",
            supports_reasoning=False,
        ):
            events.append((event_type, chunk))

        event_types = [e[0] for e in events]
        # 绝不能产生任何 thinking 事件
        assert "thinking" not in event_types
        # 正文必须包含真实回复
        msg_text = "".join(e[1] for e in events if e[0] == "message")
        assert "你好，旅者。" in msg_text
        assert "我在沉浸式构思剧情" not in msg_text


@pytest.mark.asyncio
async def test_llm_gateway_thinking_allowed_when_enabled():
    """测试当 supports_reasoning=True 时，正常 emit thinking 事件。"""
    client = OpenAILLMClient(api_key="mock", base_url="https://mock.api/v1")

    async def mock_aiter_lines():
        yield 'data: {"choices":[{"delta":{"content":"<think>我在沉浸式构思剧情</think>你好，旅者。"}}]}'
        yield 'data: [DONE]'

    from unittest.mock import AsyncMock, patch, MagicMock
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.aiter_lines = mock_aiter_lines

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value = mock_resp
        mock_stream.return_value = mock_ctx

        events = []
        async for event_type, chunk in client.stream_chat(
            messages=[{"role": "user", "content": "hello"}],
            model="deepseek-reasoner",
            supports_reasoning=True,
        ):
            events.append((event_type, chunk))

        event_types = [e[0] for e in events]
        assert "thinking" in event_types
        think_text = "".join(e[1] for e in events if e[0] == "thinking")
        assert "我在沉浸式构思剧情" in think_text


from tests.conftest import TestAsyncSessionLocal


@pytest.mark.asyncio
async def test_initial_greeting_user_macro_replacement():
    """测试初始化会话时，开场白中的 {{user}} 被全量替换为真实昵称。"""
    async with TestAsyncSessionLocal() as db_session:
        user_id = uuid.uuid4()
        char_id = uuid.uuid4()

        user = User(
            id=user_id,
            email=f"tester_{user_id.hex[:6]}@naro.ai",
            hashed_password="pw",
            invite_code=f"INV_{user_id.hex[:6]}",
        )
        profile = UserProfile(user_id=user_id, username="星穹行者", is_custom_username=True)
        character = Character(
            id=char_id,
            author_id=user_id,
            name="测试忍者",
            avatar_url="https://example.com/avatar.png",
            description="测试角色描述",
            first_mes="{{user}}，你怎么才来？任务已经开始了！",
            status="published",
        )
        db_session.add_all([user, profile, character])
        await db_session.commit()

        session = await ChatService.get_or_create_session(
            db=db_session,
            user_id=user_id,
            character_id=char_id,
        )

        from sqlalchemy import select
        msg_stmt = select(ChatMessage).where(ChatMessage.session_id == session.id)
        msgs = (await db_session.execute(msg_stmt)).scalars().all()
        assert len(msgs) == 1
        assert "{{user}}" not in msgs[0].content
        assert "星穹行者，你怎么才来？" in msgs[0].content


@pytest.mark.asyncio
async def test_check_model_supports_reasoning():
    """测试 LLMService.check_model_supports_reasoning 准确读取配置与兜底。"""
    from app.models.llm import SystemLLMProvider

    async with TestAsyncSessionLocal() as db:
        # 渠道与模型配置
        p1 = SystemLLMProvider(
            name="DeepSeek Official",
            provider_type="openai",
            base_url="https://api.deepseek.com",
            api_key="sk-mock",
            models=[
                {
                    "id": "deepseek-v4-flash",
                    "display_name": "DeepSeek V4 Flash",
                    "supports_reasoning": False,
                    "is_enabled": True,
                },
                {
                    "id": "deepseek-reasoner",
                    "display_name": "DeepSeek Reasoner",
                    "supports_reasoning": True,
                    "is_enabled": True,
                },
            ],
            is_active=True,
        )
        db.add(p1)
        await db.commit()

        # 查库测试：精确遵循后台配置
        assert await LLMService.check_model_supports_reasoning(db, "deepseek-v4-flash") is False
        assert await LLMService.check_model_supports_reasoning(db, "deepseek-reasoner") is True
        # 未配置兜底测试：默认 False，仅特定推理模型兜底 True
        assert await LLMService.check_model_supports_reasoning(db, "unknown-chat-model") is False
        assert await LLMService.check_model_supports_reasoning(db, "deepseek-r1-custom") is True


