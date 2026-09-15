"""后台 RBAC 鉴权与前后台互斥隔离自动化单元测试。

验证:
1. 超管登录成功获取 aud='admin' 令牌与 /me 菜单权限树
2. C 端 Token 访问后台管理接口返回 403 严格隔离
3. RBAC 资源查询 (用户列表、角色列表、权限树、部门树)
"""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.admin import AdminDepartment, AdminPermission, AdminRole, AdminUser
from tests.conftest import TestAsyncSessionLocal


@pytest_asyncio.fixture(autouse=True)
async def seed_admin_data() -> None:
    """在测试数据库中初始化超管与基础权限数据。"""
    async with TestAsyncSessionLocal() as session:
        dept = AdminDepartment(name="平台技术部", status="active")
        session.add(dept)
        await session.flush()

        role = AdminRole(
            role_key="super_admin",
            name="超级管理员",
            status="active",
        )
        session.add(role)
        await session.flush()

        perm = AdminPermission(
            type="menu",
            title="用户管理",
            code="system:user:view",
            path="/om/user",
            status="active",
        )
        session.add(perm)
        await session.flush()

        superadmin = AdminUser(
            username="superadmin",
            email="superadmin@spikeai.internal",
            real_name="超级管理员",
            hashed_password=hash_password("11111111"),
            is_super_admin=True,
            status="active",
            department_id=dept.id,
        )
        superadmin.roles.append(role)
        session.add(superadmin)
        await session.commit()


@pytest.mark.asyncio
async def test_admin_login_and_me() -> None:
    """测试超级管理员正常登录并拉取个人动态权限与菜单树。"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 1. 登录
        login_resp = await ac.post(
            "/api/v1/admin/auth/login",
            json={"username": "superadmin", "password": "11111111"},
        )
        assert login_resp.status_code == 200, f"登录失败: {login_resp.text}"
        data = login_resp.json()
        assert "access_token" in data
        admin_token = data["access_token"]

        # 2. 拉取 me 接口
        me_resp = await ac.get(
            "/api/v1/admin/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert me_resp.status_code == 200, f"获取 me 失败: {me_resp.text}"
        me_data = me_resp.json()
        assert me_data["user_info"]["username"] == "superadmin"
        assert me_data["user_info"]["is_super_admin"] is True
        assert "super_admin" in me_data["roles"]
        assert len(me_data["permissions"]) > 0
        assert len(me_data["menus"]) > 0
        assert "system:user:view" in me_data["permissions"]


@pytest.mark.asyncio
async def test_client_token_forbidden_in_admin_api() -> None:
    """测试普通 C 端玩家 Token 绝对无法打穿后台接口 (403 Forbidden)。"""
    client_token = create_access_token(
        user_id=uuid.uuid4(),
        email="player@example.com",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get(
            "/api/v1/admin/auth/me",
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert resp.status_code == 403
        assert "非法凭证" in resp.json()["message"]



@pytest.mark.asyncio
async def test_rbac_resources_crud() -> None:
    """测试超级管理员查询管理员列表、角色、权限树、部门架构。"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        login_resp = await ac.post(
            "/api/v1/admin/auth/login",
            json={"username": "superadmin", "password": "11111111"},
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 查询用户列表
        users_resp = await ac.get("/api/v1/admin/rbac/users", headers=headers)
        assert users_resp.status_code == 200
        assert users_resp.json()["total"] >= 1

        # 查询角色列表
        roles_resp = await ac.get("/api/v1/admin/rbac/roles", headers=headers)
        assert roles_resp.status_code == 200
        assert len(roles_resp.json()) >= 1

        # 查询部门树
        dept_resp = await ac.get("/api/v1/admin/rbac/departments", headers=headers)
        assert dept_resp.status_code == 200
        assert len(dept_resp.json()) >= 1

        # 查询全量权限树
        perm_resp = await ac.get("/api/v1/admin/rbac/permissions/tree", headers=headers)
        assert perm_resp.status_code == 200
        assert len(perm_resp.json()) >= 1
