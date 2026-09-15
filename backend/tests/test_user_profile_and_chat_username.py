"""用户昵称设置、开场白零 Token 与叙梦增量 JSON 净化测试套件。

覆盖：
1. extract_and_strip_narrative_delta 对各种形态增量 JSON 的解析与彻底切除；
2. PUT /api/v1/user/profile 更新昵称与 is_custom_username；
3. 会话创建默认继承真实昵称，开场白 input/output tokens 严格为 0。

Usage:
    uv run pytest tests/test_user_profile_and_chat_username.py -v
"""

import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.models.character import Character
from app.models.chat import ChatMessage
from app.services.chat_service import ChatService
from tests.conftest import TestAsyncSessionLocal


@pytest.mark.asyncio
async def test_extract_and_strip_narrative_delta_variations():
    """测试各种格式的增量状态均能被正确提取且从正文中彻底剥离。"""
    # 场景 1: 标准 <narrative_delta> 标签
    text_1 = (
        "纲手停下了脚步，警惕地看着泥水中的你。\n\n"
        "<narrative_delta>\n"
        '{"time_text": "深夜", "new_event": {"desc": "你在荒村泥水中醒来"}}\n'
        "</narrative_delta>"
    )
    cleaned_1, delta_1 = ChatService.extract_and_strip_narrative_delta(text_1)
    assert "<narrative_delta>" not in cleaned_1
    assert "{" not in cleaned_1
    assert cleaned_1 == "纲手停下了脚步，警惕地看着泥水中的你。"
    assert delta_1 is not None
    assert delta_1["time_text"] == "深夜"
    assert delta_1["new_event"]["desc"] == "你在荒村泥水中醒来"

    # 场景 2: 未闭合标签或 Markdown 代码块
    text_2 = (
        "雨水顺着屋檐滴落。\n\n"
        "```json\n"
        '{"location": "雨之国边缘", "new_event": {"desc": "雨夜相遇"}}\n'
        "```"
    )
    cleaned_2, delta_2 = ChatService.extract_and_strip_narrative_delta(text_2)
    assert "```" not in cleaned_2
    assert "{" not in cleaned_2
    assert cleaned_2 == "雨水顺着屋檐滴落。"
    assert delta_2 is not None
    assert delta_2["location"] == "雨之国边缘"

    # 场景 3: 裸 JSON 字典 (图 2 泄漏模式)
    text_3 = (
        "雨之国边缘废弃小村 - 深夜\n\n"
        "纲手示意别出声。\n\n"
        '{"new_event": {"time": "深夜", "location": "废弃小村", "desc": "纲手靠近探查"}}'
    )
    cleaned_3, delta_3 = ChatService.extract_and_strip_narrative_delta(text_3)
    assert '{"new_event"' not in cleaned_3
    assert "{" not in cleaned_3
    assert "纲手示意别出声。" in cleaned_3
    assert delta_3 is not None
    assert delta_3["new_event"]["desc"] == "纲手靠近探查"


@pytest.mark.asyncio
async def test_update_user_profile_and_session_username_flow():
    """测试用户注册(is_custom_username=False) -> PUT更新昵称 -> 创建会话继承真实昵称且开场白0 Token。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. 注册新用户
        reg_payload = {
            "email": "tester_custom_name@naro.ai",
            "password": "mypassword123",
            "code": "888888",
        }
        reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_resp.status_code == 200
        token = reg_resp.json()["data"]["access_token"]
        user_info = reg_resp.json()["data"]["user"]
        # 初始注册用户未主动设定自定义昵称
        assert user_info["is_custom_username"] is False

        headers = {"Authorization": f"Bearer {token}"}

        # 2. 校验非法长度昵称 (小于2字符)
        resp_short = await client.put(
            "/api/v1/user/profile",
            headers=headers,
            json={"username": "a"},
        )
        assert resp_short.status_code in (400, 422)

        # 3. 正常设置自定义昵称
        resp_ok = await client.put(
            "/api/v1/user/profile",
            headers=headers,
            json={"username": "星穹旅者Spike"},
        )
        assert resp_ok.status_code == 200
        data = resp_ok.json()["data"]
        assert data["username"] == "星穹旅者Spike"
        assert data["is_custom_username"] is True

        # 4. GET /profile 验证持久化
        resp_get = await client.get("/api/v1/user/profile", headers=headers)
        assert resp_get.status_code == 200
        assert resp_get.json()["data"]["username"] == "星穹旅者Spike"
        assert resp_get.json()["data"]["is_custom_username"] is True

        # 5. 创建测试角色
        char_id = uuid.uuid4()
        async with TestAsyncSessionLocal() as session:
            test_char = Character(
                id=char_id,
                author_id=uuid.UUID(user_info["id"]),
                name="纲手姬",
                avatar_url="https://example.com/tsunade.jpg",
                description="传说的三忍之一",
                first_mes="……你醒了？别乱动，伤口刚止住血。",
                scenario="雨之国边缘废弃小村",
            )
            session.add(test_char)
            await session.commit()

        # 6. 新建该角色的聊天会话
        resp_session = await client.get(
            f"/api/v1/chat/sessions/by-character/{char_id}",
            headers=headers,
        )
        assert resp_session.status_code == 200
        s_data = resp_session.json()["data"]
        s_id = s_data["id"]

        # 7. 检查主控面板用户名默认等于用户的自定义昵称 "星穹旅者Spike"
        resp_cp = await client.get(
            f"/api/v1/chat/sessions/{s_id}/control-panel",
            headers=headers,
        )
        assert resp_cp.status_code == 200
        cp_data = resp_cp.json()["data"]
        assert cp_data["user_name"] == "星穹旅者Spike"

        # 8. 检查开场白消息的 input_tokens 与 output_tokens 严格为 0
        async with TestAsyncSessionLocal() as session:
            msg_stmt = (
                select(ChatMessage)
                .where(ChatMessage.session_id == uuid.UUID(s_id), ChatMessage.sender == "ai")
                .order_by(ChatMessage.created_at.asc())
            )
            greeting_msg = (await session.execute(msg_stmt)).scalars().first()
            assert greeting_msg is not None
            assert greeting_msg.input_tokens == 0
            assert greeting_msg.output_tokens == 0
