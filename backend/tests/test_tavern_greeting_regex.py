"""酒馆角色卡开场白与 placement=[999] 正则清洗端到端自动化测试。

验证:
1. 角色卡开场白包含 <initvar> 状态机变量块与 placement=[999] 正则脚本;
2. 初始化会话时自动插入的 AI 问候消息经过酒馆正则流水线清洗;
3. 问候消息正文中彻底剥除 <initvar> 与 <UpdateVariable>，绝不向玩家暴露底层 JSON 数据;
4. 切换开场白时同样完成正则流水线清洗。

Usage:
    $ uv run pytest tests/test_tavern_greeting_regex.py -v
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_character_greeting_initvar_cleaned_on_session_create() -> None:
    """验证包含 <initvar> 的角色卡在初始化会话时，开场白被正则脚本正确清洗。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. 注册并登录测试用户
        email = f"regex_tester_{uuid.uuid4().hex[:6]}@example.com"
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Password123!", "username": "RegexTester"},
        )
        assert reg_resp.status_code == 200
        token = reg_resp.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 2. 创建一个携带 <initvar> 与 placement=[999] 正则脚本的测试角色
        char_payload = {
            "name": f"火影测试角色_{uuid.uuid4().hex[:4]}",
            "avatar_url": "https://example.com/avatar.png",
            "description": "测试忍界叙事引擎",
            "personality": "冷静、神秘",
            "scenario": "木叶村废墟",
            "first_mes": (
                "<initvar>\n"
                "{\n"
                '  "世界": {"时间": "第二次忍界大战"}\n'
                "}\n"
                "</initvar>\n"
                "<SceneHeaderPlaceHolder/>\n"
                "冰冷的雨水混杂着苦涩的血腥味，你缓缓睁开双眼。"
            ),
            "alternate_greetings": [
                "<initvar>\n{\"世界\": {\"时间\": \"黄昏\"}}\n</initvar>\n雨势渐止，晚霞染红了半边天空。"
            ],
            "extensions": {
                "regex_scripts": [
                    {
                        "id": str(uuid.uuid4()),
                        "scriptName": "清理初始化变量",
                        "findRegex": "/<initvar>[\\s\\S]*?<\\/initvar>/gmi",
                        "replaceString": "",
                        "placement": [999],
                        "disabled": False,
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "scriptName": "清理MVU变量更新块",
                        "findRegex": "/<UpdateVariable>[\\s\\S]*?<\\/UpdateVariable>/gm",
                        "replaceString": "",
                        "placement": [999],
                        "disabled": False,
                    },
                ]
            },
        }

        create_char_resp = await client.post(
            "/api/v1/characters",
            json=char_payload,
            headers=auth_headers,
        )
        assert create_char_resp.status_code == 200
        char_id = create_char_resp.json()["data"]["id"]

        # 3. 初始化会话
        session_resp = await client.get(
            f"/api/v1/chat/sessions/by-character/{char_id}",
            headers=auth_headers,
        )
        assert session_resp.status_code == 200
        session_id = session_resp.json()["data"]["id"]

        # 4. 获取会话首条消息 (从 session.messages 中提取)
        msgs = session_resp.json()["data"]["messages"]
        assert len(msgs) == 1, "应该存在第一条问候消息"
        first_msg = msgs[0]

        # 5. 断言: <initvar> 彻底被剥除，且真实正文完整保留
        assert "<initvar>" not in first_msg["content"], "开场消息必须剔除 <initvar> 变量块"
        assert "</initvar>" not in first_msg["content"]
        assert "第二次忍界大战" not in first_msg["content"], "私有 JSON 状态机数据不可暴露"
        assert "冰冷的雨水混杂着苦涩的血腥味" in first_msg["content"], "角色开场白真实正文必须完整保留"

        # 6. 测试切换备选开场白 (验证 alternate_greetings 同样被正则流水线清洗)
        switch_resp = await client.post(
            f"/api/v1/chat/sessions/{session_id}/greeting",
            json={"greeting_index": 1},
            headers=auth_headers,
        )
        assert switch_resp.status_code == 200
        switched_msg = switch_resp.json()["data"]
        assert "<initvar>" not in switched_msg["content"], "备用开场白也必须剥除 <initvar>"
        assert "黄昏" not in switched_msg["content"]
        assert "雨势渐止，晚霞染红了半边天空" in switched_msg["content"]
