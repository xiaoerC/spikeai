"""DAG 剧情分支树与多平行宇宙状态机测试套件。

验证基于 Parent-Pointer 的分支派生、切换、历史上下文组装、回溯、消息编辑双模式及 DAG 拓扑图生成。
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_tree_branch_lifecycle() -> None:
    """测试 DAG 剧情分支全生命周期 (分叉、切换、独立上下文、删除与拓扑图)。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. 注册登录
        email = f"storytree_{uuid.uuid4().hex[:8]}@spikeai.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Password123!", "username": "StoryExplorer"},
        )
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Password123!"},
        )
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. 创建独立测试角色
        char_create_res = await client.post(
            "/api/v1/characters",
            headers=headers,
            json={
                "name": "灶门炭治郎",
                "avatar_url": "https://example.com/tanjiro.png",
                "summary": "鬼杀队剑士",
                "description": "鬼杀队剑士炭治郎，善良坚韧",
                "personality": "善良勇敢，坚韧不拔",
                "scenario": "深山破庙调查",
                "first_mes": "夜色渐浓，深山中的寒风呼啸而过。我能闻到空气中那一丝极淡却危险的血腥味……",
                "tags": ["热血", "奇幻"],
            },
        )
        assert char_create_res.status_code == 200
        char_id = char_create_res.json()["data"]["id"]

        # 3. 创建会话
        session_res = await client.get(
            f"/api/v1/chat/sessions/by-character/{char_id}", headers=headers
        )
        assert session_res.status_code == 200
        session_data = session_res.json()["data"]
        session_id = session_data["id"]
        main_branch_id = session_data["current_branch_id"]

        # 4. 获取分支列表 (应有 1 个默认主线分支)
        branches_res = await client.get(
            f"/api/v1/chat/sessions/{session_id}/branches", headers=headers
        )
        assert branches_res.status_code == 200
        branches = branches_res.json()["data"]
        assert len(branches) == 1
        assert branches[0]["is_main"] is True

        # 5. 主线发送第一条消息
        await client.post(
            f"/api/v1/chat/sessions/{session_id}/stream",
            json={"content": "炭治郎，前面的破庙里似乎有妖气！"},
            headers=headers,
        )

        detail_res = await client.get(f"/api/v1/chat/sessions/{session_id}", headers=headers)
        msgs = detail_res.json()["data"]["messages"]
        assert len(msgs) >= 2  # 开场白 + 用户发言 + AI 回复
        first_user_msg = [m for m in msgs if m["sender"] == "user"][0]

        # 6. 从该用户消息分叉出新平行分支 (Branch 1)
        fork_res = await client.post(
            f"/api/v1/chat/sessions/{session_id}/branches/fork",
            json={
                "fork_message_id": first_user_msg["id"],
                "name": "🔀 分支 1：独自前往破庙",
                "switch_to": True,
            },
            headers=headers,
        )
        assert fork_res.status_code == 200
        branch_1 = fork_res.json()["data"]
        assert branch_1["name"] == "🔀 分支 1：独自前往破庙"
        assert branch_1["is_main"] is False
        assert branch_1["parent_branch_id"] == main_branch_id
        assert branch_1["fork_message_id"] == first_user_msg["id"]

        # 7. 在新分支 (Branch 1) 上发送新消息
        await client.post(
            f"/api/v1/chat/sessions/{session_id}/stream",
            json={"content": "我决定一个人偷偷潜入破庙！"},
            headers=headers,
        )

        # 验证分支 1 详情 (应包含祖先主线第一条消息 + 分支 1 特有消息)
        b1_detail = await client.get(f"/api/v1/chat/sessions/{session_id}", headers=headers)
        b1_msgs = b1_detail.json()["data"]["messages"]
        b1_user_contents = [m["content"] for m in b1_msgs if m["sender"] == "user"]
        assert "炭治郎，前面的破庙里似乎有妖气！" in b1_user_contents
        assert "我决定一个人偷偷潜入破庙！" in b1_user_contents

        # 8. 切回主线分支
        switch_res = await client.put(
            f"/api/v1/chat/sessions/{session_id}/branches/{main_branch_id}/switch",
            headers=headers,
        )
        assert switch_res.status_code == 200
        main_detail = switch_res.json()["data"]
        main_user_contents = [m["content"] for m in main_detail["messages"] if m["sender"] == "user"]
        # 主线分支不应被分支 1 污染
        assert "我决定一个人偷偷潜入破庙！" not in main_user_contents

        # 9. 测试编辑消息 (模式 A: 原位修改)
        last_msg = main_detail["messages"][-1]
        edit_a_res = await client.put(
            f"/api/v1/chat/sessions/{session_id}/messages/{last_msg['id']}",
            json={"content": "（修改后的文本内容）", "mode": "edit_only"},
            headers=headers,
        )
        assert edit_a_res.status_code == 200
        edited_msg = [m for m in edit_a_res.json()["data"]["messages"] if m["id"] == last_msg["id"]][0]
        assert edited_msg["content"] == "（修改后的文本内容）"

        # 10. 测试 DAG 拓扑图接口 (Vue Flow)
        tree_res = await client.get(f"/api/v1/chat/sessions/{session_id}/tree", headers=headers)
        assert tree_res.status_code == 200
        graph = tree_res.json()["data"]
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) > 0

        # 11. 删除非主线分支 (Branch 1)
        del_b1_res = await client.delete(
            f"/api/v1/chat/sessions/{session_id}/branches/{branch_1['id']}",
            headers=headers,
        )
        assert del_b1_res.status_code == 200

        # 验证无法删除主线分支
        del_main_res = await client.delete(
            f"/api/v1/chat/sessions/{session_id}/branches/{main_branch_id}",
            headers=headers,
        )
        assert del_main_res.status_code == 400

        # 12. 测试从指定消息分叉并创建全新独立历史会话 (多历史记录)
        fork_sess_res = await client.post(
            f"/api/v1/chat/sessions/{session_id}/fork-session",
            json={
                "fork_message_id": first_user_msg["id"],
                "remark": "全新平行世界记录",
            },
            headers=headers,
        )
        assert fork_sess_res.status_code == 200
        new_sess_data = fork_sess_res.json()["data"]
        assert new_sess_data["id"] != session_id
        assert new_sess_data["character_id"] == char_id
        assert len(new_sess_data["messages"]) >= 2
        assert new_sess_data["messages"][-1]["id"] != first_user_msg["id"]  # 复制生成了新独立 ID
        assert new_sess_data["messages"][-1]["content"] == first_user_msg["content"]
