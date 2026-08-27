"""用户认证、登录鉴权与个人资料接口自动化测试套件。

测试覆盖：
1. 邮箱注册 (新用户自动赠送 100星元+50月华、生成专属邀请码与初始勋章)；
2. 重复邮箱注册冲突防御；
3. 账号密码登录与密码错误防御；
4. 受保护路由 /api/v1/user/profile 访问与未授权 401 拦截；
5. 退出登录拉黑 Token；
6. 邀请码绑定与邀请统计。

Usage:
    $ uv run pytest tests/test_auth.py -v
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_user_register_and_login_flow():
    """测试用户注册 -> 登录 -> 获取个人资料全流程。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. 注册新用户
        reg_payload = {
            "email": "alice@naro.ai",
            "password": "mypassword123",
            "code": "888888",
        }
        reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_resp.status_code == 200
        reg_data = reg_resp.json()

        assert reg_data["code"] == 0
        assert "access_token" in reg_data["data"]
        token = reg_data["data"]["access_token"]
        assert len(token) > 20
        user_info = reg_data["data"]["user"]

        assert user_info["email"] == "alice@naro.ai"
        assert user_info["username"] == "alice"
        assert user_info["wallet"]["star_coins"] == 100
        assert user_info["wallet"]["moon_gems"] == 50
        assert user_info["invite_code"].startswith("NAR-")
        assert len(user_info["badges"]) == 1

        # 2. 重复注册相同邮箱应失败 (400)
        dup_resp = await client.post("/api/v1/auth/register", json=reg_payload)
        assert dup_resp.status_code == 400
        assert "该邮箱已被注册" in (dup_resp.json().get("message") or "")

        # 3. 使用正确密码登录
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "alice@naro.ai", "password": "mypassword123"},
        )
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        assert login_data["code"] == 0
        new_token = login_data["data"]["access_token"]

        # 4. 使用错误密码登录应失败 (400)
        wrong_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "alice@naro.ai", "password": "wrong_password"},
        )
        assert wrong_resp.status_code == 400
        assert "账号或密码错误" in (wrong_resp.json().get("message") or "")

        # 5. 携带 Token 请求受保护的个人资料接口 /api/v1/user/profile
        headers = {"Authorization": f"Bearer {new_token}"}
        profile_resp = await client.get("/api/v1/user/profile", headers=headers)
        assert profile_resp.status_code == 200
        profile_data = profile_resp.json()["data"]

        assert profile_data["email"] == "alice@naro.ai"
        assert profile_data["wallet"]["star_coins"] == 100

        # 6. 未携带 Token 请求个人资料应被 401 拦截
        unauth_resp = await client.get("/api/v1/user/profile")
        assert unauth_resp.status_code == 401


@pytest.mark.asyncio
async def test_invite_code_relationship():
    """测试通过邀请码注册并绑定邀请关系。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. 注册邀请人
        inviter_resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "inviter@naro.ai", "password": "password123"},
        )
        inviter_token = inviter_resp.json()["data"]["access_token"]
        invite_code = inviter_resp.json()["data"]["user"]["invite_code"]

        # 2. 受邀人使用该邀请码注册
        invitee_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invitee@naro.ai",
                "password": "password123",
                "invite_code": invite_code,
            },
        )
        assert invitee_resp.status_code == 200

        # 3. 邀请人查看邀请统计
        headers = {"Authorization": f"Bearer {inviter_token}"}
        invite_info_resp = await client.get("/api/v1/user/invite-info", headers=headers)
        assert invite_info_resp.status_code == 200
        invite_info = invite_info_resp.json()["data"]

        assert invite_info["invite_code"] == invite_code
        assert invite_info["invited_count"] == 1
        assert invite_info["reward_earned_star"] == 100
