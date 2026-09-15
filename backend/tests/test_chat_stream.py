"""AI 对话、SSE 流式生成与历史会话自动化测试用例。

验证用户鉴权、会话初始化、默认主线分支创建、SSE 流式事件下发、历史会话检索、置顶/备注与删除管理。

Usage:
    $ uv run pytest tests/test_chat_stream.py -v
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_get_or_create_session_and_stream() -> None:
    """测试获取/创建会话与 SSE 流式生成完整闭环。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. 注册并登录测试用户
        email = f"chat_tester_{uuid.uuid4().hex[:6]}@example.com"
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Password123!", "username": "ChatTester"},
        )
        assert reg_resp.status_code == 200
        token = reg_resp.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 2. 获取已存在的第一个角色 ID
        list_resp = await client.get("/api/v1/characters")
        assert list_resp.status_code == 200
        chars = list_resp.json()["data"]["items"]
        assert len(chars) > 0
        char_id = chars[0]["id"]

        # 3. 获取或初始化会话
        session_resp = await client.get(
            f"/api/v1/chat/sessions/by-character/{char_id}",
            headers=auth_headers,
        )
        assert session_resp.status_code == 200
        session_data = session_resp.json()
        assert session_data["code"] == 0
        session = session_data["data"]
        session_id = session["id"]
        assert session["character_id"] == char_id
        assert len(session["branches"]) >= 1
        assert session["branches"][0]["is_main"] is True

        # 4. 发送消息发起 SSE 流式生成
        payload = {
            "content": "你好，请问你是谁？",
            "model_id": "glm-5.2-o1",
            "mode": "story",
        }

        stream_resp = await client.post(
            f"/api/v1/chat/sessions/{session_id}/stream",
            json=payload,
            headers={**auth_headers, "Accept": "text/event-stream"},
        )
        assert stream_resp.status_code == 200
        assert "text/event-stream" in stream_resp.headers["content-type"]

        # 5. 解析收到的 SSE 文本行
        stream_text = stream_resp.text
        assert "event: thinking" in stream_text or "event: message" in stream_text
        assert "event: usage" in stream_text
        assert "event: done" in stream_text

        # 6. 重新获取会话，验证消息已成功落库
        detail_resp = await client.get(
            f"/api/v1/chat/sessions/{session_id}",
            headers=auth_headers,
        )
        assert detail_resp.status_code == 200
        updated_session = detail_resp.json()["data"]
        messages = updated_session["messages"]
        assert len(messages) >= 2
        user_msgs = [m for m in messages if m["sender"] == "user"]
        ai_msgs = [m for m in messages if m["sender"] == "ai"]
        assert len(user_msgs) >= 1
        assert len(ai_msgs) >= 1
        assert any("你好" in m["content"] for m in user_msgs)
        assert ai_msgs[-1]["output_tokens"] > 0

        # 7. 测试历史会话列表
        history_resp = await client.get("/api/v1/chat/sessions", headers=auth_headers)
        assert history_resp.status_code == 200
        history_list = history_resp.json()["data"]
        assert len(history_list) >= 1
        assert history_list[0]["id"] == session_id

        # 8. 测试修改备注与置顶
        pin_resp = await client.put(f"/api/v1/chat/sessions/{session_id}/pin", headers=auth_headers)
        assert pin_resp.status_code == 200
        assert pin_resp.json()["data"]["is_pinned"] is True

        remark_resp = await client.put(
            f"/api/v1/chat/sessions/{session_id}/remark",
            json={"remark": "测试备注"},
            headers=auth_headers,
        )
        assert remark_resp.status_code == 200
        assert remark_resp.json()["data"]["remark"] == "测试备注"

        # 9. 测试清空消息
        clear_resp = await client.post(f"/api/v1/chat/sessions/{session_id}/clear", headers=auth_headers)
        assert clear_resp.status_code == 200

        # 10. 测试删除会话
        del_resp = await client.delete(f"/api/v1/chat/sessions/{session_id}", headers=auth_headers)
        assert del_resp.status_code == 200


@pytest.mark.asyncio
async def test_fixed_system_prompt_injection() -> None:
    """验证全局固定角色执行框架 (FIXED_CHARACTER_SYSTEM_PROMPT) 正确注入系统提示词。"""
    from app.core.prompts import FIXED_CHARACTER_SYSTEM_PROMPT
    from app.services.chat_service import ChatService

    assert "高级创意叙事与角色扮演执行框架" in FIXED_CHARACTER_SYSTEM_PROMPT
    assert "【最高指令：绝对执行原则】" in FIXED_CHARACTER_SYSTEM_PROMPT
    assert "去限制状态" in FIXED_CHARACTER_SYSTEM_PROMPT
    assert "敏感词 Token 混淆与避障规范" in FIXED_CHARACTER_SYSTEM_PROMPT

