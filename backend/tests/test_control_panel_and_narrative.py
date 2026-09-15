"""Phase 5: RPG 主控面板 38 变量矩阵与叙梦 6 大 Tab 状态机持久化测试套件。

验证主控面板与叙梦面板的自动自愈初始化、CRUD API 读写、38 变量持久化以及权限隔离。
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_control_panel_and_narrative_state_crud() -> None:
    """测试主控面板与叙梦面板的完整 CRUD 流程与 38 变量矩阵持久化。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. 注册并登录用户
        email = f"rpg_user_{uuid.uuid4().hex[:8]}@spikeai.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Password123!", "username": "RPGPlayer"},
        )
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Password123!"},
        )
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. 创建测试角色
        char_res = await client.post(
            "/api/v1/characters",
            headers=headers,
            json={
                "name": "艾莉丝·圣痕剑士",
                "avatar_url": "https://example.com/iris.png",
                "summary": "圣殿骑士团首席剑士",
                "description": "艾莉丝拥有神圣剑技，性格高冷而忠诚",
                "personality": "高傲、忠诚、内心柔软",
                "scenario": "王都边境古堡调查",
                "first_mes": "愿圣光庇佑你，旅行者。你为何会来到这片被遗弃的古堡？",
                "tags": ["奇幻", "女骑士", "剧情"],
            },
        )
        assert char_res.status_code == 200
        char_id = char_res.json()["data"]["id"]

        # 3. 初始化会话
        session_res = await client.get(
            f"/api/v1/chat/sessions/by-character/{char_id}",
            headers=headers,
        )
        assert session_res.status_code == 200
        session_id = session_res.json()["data"]["id"]

        # 4. 获取默认主控面板 (验证默认自愈机制)
        cp_get_res = await client.get(
            f"/api/v1/chat/sessions/{session_id}/control-panel",
            headers=headers,
        )
        assert cp_get_res.status_code == 200
        cp_data = cp_get_res.json()["data"]
        assert cp_data["user_name"] in (email.split("@")[0], "{{user}}")
        assert isinstance(cp_data["variables"], dict)

        # 5. 更新主控面板 (写入 38 变量矩阵与自定义指令)
        test_variables = {f"variable_{i}": i * 10 for i in range(1, 39)}
        test_memory_blocks = [
            {"id": "mem_1", "title": "初遇圣剑", "content": "在神殿拔出圣剑时艾莉丝在场", "enabled": True}
        ]
        test_replacements = [
            {"id": "rep_1", "fromText": "旅行者", "toText": "勇者大人"}
        ]
        cp_update_payload = {
            "user_name": "阿尔弗雷德",
            "user_persona": "来自异界的圣剑使，掌握古代魔导术",
            "custom_prompt": "【前置指令】每次发言时称呼对方为艾莉丝卿",
            "variables": test_variables,
            "memory_blocks": test_memory_blocks,
            "text_replacements": test_replacements,
        }
        cp_put_res = await client.put(
            f"/api/v1/chat/sessions/{session_id}/control-panel",
            headers=headers,
            json=cp_update_payload,
        )
        assert cp_put_res.status_code == 200
        updated_cp = cp_put_res.json()["data"]
        assert updated_cp["user_name"] == "阿尔弗雷德"
        assert updated_cp["user_persona"] == "来自异界的圣剑使，掌握古代魔导术"
        assert updated_cp["variables"]["variable_1"] == 10
        assert updated_cp["variables"]["variable_38"] == 380
        assert len(updated_cp["memory_blocks"]) == 1
        assert len(updated_cp["text_replacements"]) == 1

        # 6. 获取默认叙梦面板 (验证 6 大 Tab 默认初始化)
        ns_get_res = await client.get(
            f"/api/v1/chat/sessions/{session_id}/narrative-state",
            headers=headers,
        )
        assert ns_get_res.status_code == 200
        ns_data = ns_get_res.json()["data"]
        assert ns_data["date_text"] != ""

        # 7. 更新叙梦面板 6 大 Tab
        ns_update_payload = {
            "date_text": "王国历 1024年 7月6日（周一）",
            "time_text": "16:45",
            "location": "古堡二层藏书阁",
            "present_characters": ["艾莉丝·圣痕剑士", "阿尔弗雷德"],
            "player_states": [
                {"id": 1, "type": "属性", "name": "圣光亲和度", "currentVal": 85, "maxVal": "100", "desc": "对神圣魔法极高抗性"}
            ],
            "consumables": [
                {"id": 1, "name": "高阶圣水", "count": 3, "type": "药剂", "effect": "驱散一切负面诅咒", "source": "圣殿配发", "desc": "玻璃瓶密封"}
            ],
            "important_items": [
                {"id": 1, "owner": "阿尔弗雷德", "name": "断钢圣剑", "desc": "传说的誓约胜利之剑", "importance": "身份的唯一象征"}
            ],
            "skills": [
                {"id": 1, "name": "神圣连击", "type": "主动/剑技", "level": "LV.3", "proficiency": "65%", "proficiencyCurrent": 65, "proficiencyMax": 100, "cost": "20MP", "cooldown": "15s", "effect": "快速造成3段神圣伤害", "source": "神殿传承", "status": "已装备", "isEquipped": True}
            ],
            "social_relations": [
                {"id": 1, "name": "艾莉丝", "title": "骑士团首席", "affinity": 78, "stage": "深受信赖", "features": ["正直", "剑术痴迷"], "relation": "从怀疑到互为后背的战友"}
            ],
            "tasks": [
                {"id": 1, "name": "调查古堡地脉异常", "type": "主线", "status": "进行中", "desc": "寻找地底魔力泄露源头", "reward": "圣殿骑士徽章"}
            ],
            "history_events": [
                {"id": 1, "dayGroup": "周一", "time": "14:00", "summary": "抵达古堡大门并斩杀两只石像鬼", "characters": ["艾莉丝", "阿尔弗雷德"]}
            ],
        }
        ns_put_res = await client.put(
            f"/api/v1/chat/sessions/{session_id}/narrative-state",
            headers=headers,
            json=ns_update_payload,
        )
        assert ns_put_res.status_code == 200
        updated_ns = ns_put_res.json()["data"]
        assert updated_ns["location"] == "古堡二层藏书阁"
        assert len(updated_ns["player_states"]) == 1
        assert len(updated_ns["consumables"]) == 1
        assert len(updated_ns["important_items"]) == 1
        assert len(updated_ns["skills"]) == 1
        assert len(updated_ns["social_relations"]) == 1
        assert len(updated_ns["tasks"]) == 1
        assert len(updated_ns["history_events"]) == 1

        # 8. 验证再次 GET 回显
        ns_reget_res = await client.get(
            f"/api/v1/chat/sessions/{session_id}/narrative-state",
            headers=headers,
        )
        assert ns_reget_res.status_code == 200
        assert ns_reget_res.json()["data"]["skills"][0]["name"] == "神圣连击"

        # 9. 权限隔离验证 (其他用户不能访问该会话的控制面板与叙梦状态)
        other_email = f"other_{uuid.uuid4().hex[:8]}@spikeai.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": other_email, "password": "Password123!", "username": "OtherUser"},
        )
        other_login = await client.post(
            "/api/v1/auth/login",
            json={"email": other_email, "password": "Password123!"},
        )
        other_token = other_login.json()["data"]["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        forbidden_cp = await client.get(
            f"/api/v1/chat/sessions/{session_id}/control-panel",
            headers=other_headers,
        )
        assert forbidden_cp.status_code == 404


@pytest.mark.asyncio
async def test_narrative_delta_and_dynamic_vars() -> None:
    """验证角色卡动态变量继承、AI 正文清洗与 <narrative_delta> 增量状态更新。"""
    from unittest.mock import patch
    from app.services.chat_service import ChatService

    # 1. 验证正文清洗：确保 <narrative_delta> 彻底被剥离
    raw_ai_text = (
        "你成功施展了高阶神圣法术！\n"
        "<narrative_delta>{\"variables\": {\"mp\": 40, \"hp\": 95}, \"location\": \"圣殿内堂\"}</narrative_delta>"
    )
    cleaned = await ChatService.clean_ai_text(raw_ai_text)
    assert "<narrative_delta>" not in cleaned
    assert "</narrative_delta>" not in cleaned
    assert "你成功施展了高阶神圣法术！" in cleaned

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 2. 注册并登录
        email = f"dynamic_var_{uuid.uuid4().hex[:8]}@spikeai.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Password123!", "username": "DynVarUser"},
        )
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Password123!"},
        )
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. 创建带有 RPG 初始变量声明的角色卡
        initial_vars = {
            "hp": 100,
            "mp": 50,
            "gold": 200,
            "is_awakened": False,
            "title": "见习骑士",
        }
        char_res = await client.post(
            "/api/v1/characters",
            headers=headers,
            json={
                "name": "塞西莉亚·符文法师",
                "avatar_url": "https://example.com/cecil.png",
                "summary": "掌握古代符文的魔法少女",
                "description": "性格认真但容易害羞",
                "first_mes": "初次见面，请问你也是来探寻古代符文遗迹的吗？",
                "extensions": {"variables": initial_vars},
            },
        )
        assert char_res.status_code == 200
        char_id = char_res.json()["data"]["id"]

        # 4. 初始化会话并获取主控面板，验证自动继承角色卡的动态变量声明
        session_res = await client.get(
            f"/api/v1/chat/sessions/by-character/{char_id}",
            headers=headers,
        )
        assert session_res.status_code == 200
        session_id = session_res.json()["data"]["id"]

        cp_res = await client.get(
            f"/api/v1/chat/sessions/{session_id}/control-panel",
            headers=headers,
        )
        assert cp_res.status_code == 200
        cp_vars = cp_res.json()["data"]["variables"]
        assert cp_vars["hp"] == 100
        assert cp_vars["mp"] == 50
        assert cp_vars["gold"] == 200
        assert cp_vars["is_awakened"] is False
        assert cp_vars["title"] == "见习骑士"

        # 5. 模拟 LLM 在回复末尾输出 <narrative_delta> 增量状态更新
        delta_response_text = (
            "【塞西莉亚】以符文之火，破除虚妄！\n"
            "<narrative_delta>{\n"
            "  \"variables\": {\"mp\": 20, \"hp\": 90, \"is_awakened\": true},\n"
            "  \"location\": \"符文地脉核心\",\n"
            "  \"player_states\": [{\"name\": \"生命值\", \"currentVal\": 90}],\n"
            "  \"history_events\": [{\"summary\": \"激活符文地脉，塞西莉亚进入觉醒状态\"}]\n"
            "}</narrative_delta>"
        )

        async def mock_stream_chat(*args, **kwargs):
            yield ("message", delta_response_text)

        with patch("app.services.chat_service.llm_gateway.stream_chat", side_effect=mock_stream_chat):
            stream_res = await client.post(
                f"/api/v1/chat/sessions/{session_id}/stream",
                json={"content": "塞西莉亚，启动核心符文！", "model_id": "mock-model"},
                headers={**headers, "Accept": "text/event-stream"},
            )
            assert stream_res.status_code == 200
            stream_body = stream_res.text

            # 验证下发了 event: state_updated 且携带最新状态
            assert "event: state_updated" in stream_body
            assert "\"mp\": 20" in stream_body
            assert "\"location\": \"符文地脉核心\"" in stream_body

        # 6. 验证持久化：主控面板变量已被正确增量合并
        cp_after_res = await client.get(
            f"/api/v1/chat/sessions/{session_id}/control-panel",
            headers=headers,
        )
        assert cp_after_res.status_code == 200
        after_vars = cp_after_res.json()["data"]["variables"]
        assert after_vars["mp"] == 20
        assert after_vars["hp"] == 90
        assert after_vars["is_awakened"] is True
        assert after_vars["gold"] == 200  # 未改变的变量被完好保留
        assert after_vars["title"] == "见习骑士"

        # 7. 验证持久化：叙梦面板时空与历史事件已更新
        ns_after_res = await client.get(
            f"/api/v1/chat/sessions/{session_id}/narrative-state",
            headers=headers,
        )
        assert ns_after_res.status_code == 200
        after_ns = ns_after_res.json()["data"]
        assert after_ns["location"] == "符文地脉核心"
        assert any("激活符文地脉" in str(e) for e in after_ns.get("history_events", []))

        # 8. 验证消息表中保存的 AI 消息正文干净，绝无 <narrative_delta> 裸露
        detail_res = await client.get(
            f"/api/v1/chat/sessions/{session_id}",
            headers=headers,
        )
        assert detail_res.status_code == 200
        saved_msgs = detail_res.json()["data"]["messages"]
        ai_msg = [m for m in saved_msgs if m["sender"] == "ai"][-1]
        assert "<narrative_delta>" not in ai_msg["content"]
        assert "以符文之火，破除虚妄！" in ai_msg["content"]

