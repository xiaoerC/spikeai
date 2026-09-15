"""初始化后台 RBAC 权限与默认超级管理员账号脚本。

创建初始部门架构、系统菜单与权限树、内置角色，并初始化超级管理员账号:
    账号: superadmin
    密码: 11111111

Usage:
    uv run python -m scripts.init_admin_rbac
"""

import asyncio
import logging
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal

from app.core.security import hash_password
from app.models.admin import (
    AdminAuditLog,
    AdminDepartment,
    AdminPermission,
    AdminRole,
    AdminUser,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_admin_rbac")


async def init_rbac_data() -> None:
    """执行 RBAC 种子数据初始化。"""
    async with AsyncSessionLocal() as session:

        # 1. 检查超级管理员是否已存在
        stmt = select(AdminUser).where(AdminUser.username == "superadmin")
        result = await session.execute(stmt)
        existing_superadmin = result.scalar_one_or_none()

        # 2. 创建组织架构部门
        dept_stmt = select(AdminDepartment).where(AdminDepartment.name == "平台运营中心")
        dept_result = await session.execute(dept_stmt)
        root_dept = dept_result.scalar_one_or_none()
        if not root_dept:
            root_dept = AdminDepartment(
                name="平台运营中心",
                leader="总负责人",
                phone="13800000000",
                sort=1,
                status="active",
            )
            session.add(root_dept)
            await session.flush()

            sub_dept1 = AdminDepartment(
                parent_id=root_dept.id,
                name="产品研发组",
                leader="技术负责人",
                sort=1,
                status="active",
            )
            sub_dept2 = AdminDepartment(
                parent_id=root_dept.id,
                name="内容审核中心",
                leader="审核负责人",
                sort=2,
                status="active",
            )
            sub_dept3 = AdminDepartment(
                parent_id=root_dept.id,
                name="用户运营中心",
                leader="运营负责人",
                sort=3,
                status="active",
            )
            session.add_all([sub_dept1, sub_dept2, sub_dept3])
            await session.flush()
            logger.info("已创建组织架构部门树")

        # 3. 创建系统菜单与权限树
        # 3.1 组织与权限目录
        perm_om_dir = (
            await session.execute(
                select(AdminPermission).where(AdminPermission.code == "system:om:dir")
            )
        ).scalar_one_or_none()
        if not perm_om_dir:
            perm_om_dir = AdminPermission(
                type="directory",
                title="组织与权限",
                name="OrganizationManagement",
                code="system:om:dir",
                path="/om",
                icon="Setting",
                sort=10,
            )
            session.add(perm_om_dir)
            await session.flush()

            # 用户管理菜单
            perm_user_menu = AdminPermission(
                parent_id=perm_om_dir.id,
                type="menu",
                title="用户管理",
                name="SystemUser",
                code="system:user:view",
                path="/om/user",
                component="views/om/user/index.vue",
                icon="User",
                sort=1,
            )
            session.add(perm_user_menu)
            await session.flush()

            # 用户按钮权限
            session.add_all([
                AdminPermission(
                    parent_id=perm_user_menu.id,
                    type="button",
                    title="新增用户",
                    code="system:user:create",
                    sort=1,
                ),
                AdminPermission(
                    parent_id=perm_user_menu.id,
                    type="button",
                    title="编辑用户",
                    code="system:user:update",
                    sort=2,
                ),
                AdminPermission(
                    parent_id=perm_user_menu.id,
                    type="button",
                    title="删除用户",
                    code="system:user:delete",
                    sort=3,
                ),
                AdminPermission(
                    parent_id=perm_user_menu.id,
                    type="button",
                    title="重置密码",
                    code="system:user:reset_pwd",
                    sort=4,
                ),
            ])

            # 角色管理菜单
            perm_role_menu = AdminPermission(
                parent_id=perm_om_dir.id,
                type="menu",
                title="角色管理",
                name="SystemRole",
                code="system:role:view",
                path="/om/role",
                component="views/om/role/index.vue",
                icon="Lock",
                sort=2,
            )
            session.add(perm_role_menu)
            await session.flush()

            # 角色按钮权限
            session.add_all([
                AdminPermission(
                    parent_id=perm_role_menu.id,
                    type="button",
                    title="新增角色",
                    code="system:role:create",
                    sort=1,
                ),
                AdminPermission(
                    parent_id=perm_role_menu.id,
                    type="button",
                    title="编辑角色",
                    code="system:role:update",
                    sort=2,
                ),
                AdminPermission(
                    parent_id=perm_role_menu.id,
                    type="button",
                    title="删除角色",
                    code="system:role:delete",
                    sort=3,
                ),
                AdminPermission(
                    parent_id=perm_role_menu.id,
                    type="button",
                    title="分配权限",
                    code="system:role:assign_perm",
                    sort=4,
                ),
            ])

            # 部门管理菜单
            perm_dept_menu = AdminPermission(
                parent_id=perm_om_dir.id,
                type="menu",
                title="部门管理",
                name="SystemDept",
                code="system:dept:view",
                path="/om/department",
                component="views/om/department/index.vue",
                icon="OfficeBuilding",
                sort=3,
            )
            session.add(perm_dept_menu)
            await session.flush()

            # 部门按钮权限
            session.add_all([
                AdminPermission(
                    parent_id=perm_dept_menu.id,
                    type="button",
                    title="新增部门",
                    code="system:dept:create",
                    sort=1,
                ),
                AdminPermission(
                    parent_id=perm_dept_menu.id,
                    type="button",
                    title="编辑部门",
                    code="system:dept:update",
                    sort=2,
                ),
                AdminPermission(
                    parent_id=perm_dept_menu.id,
                    type="button",
                    title="删除部门",
                    code="system:dept:delete",
                    sort=3,
                ),
            ])
            logger.info("已创建系统组织架构权限节点")

        # 3.2 C 端用户运营目录 (物理与逻辑严格隔离)
        perm_client_dir = (
            await session.execute(
                select(AdminPermission).where(AdminPermission.code == "client:ops:dir")
            )
        ).scalar_one_or_none()
        if not perm_client_dir:
            perm_client_dir = AdminPermission(
                type="directory",
                title="前台玩家运营",
                name="ClientUserOps",
                code="client:ops:dir",
                path="/client-user",
                icon="UserFilled",
                sort=20,
            )
            session.add(perm_client_dir)
            await session.flush()

            perm_client_menu = AdminPermission(
                parent_id=perm_client_dir.id,
                type="menu",
                title="玩家资产与监控",
                name="ClientUserList",
                code="client:user:view",
                path="/client-user/list",
                component="views/client-user/index.vue",
                icon="Wallet",
                sort=1,
            )
            session.add(perm_client_menu)
            await session.flush()

            session.add_all([
                AdminPermission(
                    parent_id=perm_client_menu.id,
                    type="button",
                    title="封禁解禁玩家",
                    code="client:user:ban",
                    sort=1,
                ),
                AdminPermission(
                    parent_id=perm_client_menu.id,
                    type="button",
                    title="月华资产调整",
                    code="client:user:adjust_wallet",
                    sort=2,
                ),
            ])
            logger.info("已创建前台玩家运营权限节点")

        # 3.3 系统审计日志目录
        perm_audit_dir = (
            await session.execute(
                select(AdminPermission).where(AdminPermission.code == "system:audit:dir")
            )
        ).scalar_one_or_none()
        if not perm_audit_dir:
            perm_audit_dir = AdminPermission(
                type="directory",
                title="系统安全审计",
                name="SystemAudit",
                code="system:audit:dir",
                path="/audit",
                icon="Document",
                sort=30,
            )
            session.add(perm_audit_dir)
            await session.flush()

            perm_audit_menu = AdminPermission(
                parent_id=perm_audit_dir.id,
                type="menu",
                title="操作日志",
                name="AuditLogList",
                code="audit:log:view",
                path="/audit/logs",
                component="views/audit/logs/index.vue",
                icon="Memo",
                sort=1,
            )
            session.add(perm_audit_menu)
            logger.info("已创建系统安全审计权限节点")

        # 4. 创建默认角色
        super_role = (
            await session.execute(
                select(AdminRole).where(AdminRole.role_key == "super_admin")
            )
        ).scalar_one_or_none()
        if not super_role:
            super_role = AdminRole(
                role_key="super_admin",
                name="超级管理员",
                description="拥有平台系统最高权限，无视一切权限控制",
                sort=1,
                status="active",
            )
            session.add(super_role)
            await session.flush()

        auditor_role = (
            await session.execute(
                select(AdminRole).where(AdminRole.role_key == "content_auditor")
            )
        ).scalar_one_or_none()
        if not auditor_role:
            auditor_role = AdminRole(
                role_key="content_auditor",
                name="内容审核员",
                description="负责角色卡、世界书、MOD 等敏感内容审核",
                sort=2,
                status="active",
            )
            session.add(auditor_role)

        ops_role = (
            await session.execute(
                select(AdminRole).where(AdminRole.role_key == "ops_specialist")
            )
        ).scalar_one_or_none()
        if not ops_role:
            ops_role = AdminRole(
                role_key="ops_specialist",
                name="运营专员",
                description="负责前台玩家服务、活动公告发布与社群运营",
                sort=3,
                status="active",
            )
            session.add(ops_role)
            logger.info("已创建内置角色列表")

        # 5. 创建超级管理员账号
        if not existing_superadmin:
            superadmin = AdminUser(
                username="superadmin",
                email="superadmin@spikeai.internal",
                real_name="超级管理员",
                hashed_password=hash_password("11111111"),
                department_id=root_dept.id if root_dept else None,
                is_super_admin=True,
                status="active",
                job_number="SA001",
            )
            superadmin.roles.append(super_role)
            session.add(superadmin)
            await session.commit()
            logger.info("=====================================================")
            logger.info("超级管理员初始化成功!")
            logger.info("账号: superadmin")
            logger.info("密码: 11111111")
            logger.info("=====================================================")
        else:
            # 如果已存在，更新密码以对齐用户要求
            existing_superadmin.hashed_password = hash_password("11111111")
            existing_superadmin.is_super_admin = True
            existing_superadmin.status = "active"
            await session.commit()
            logger.info("超级管理员账号已存在，密码已同步重置为: 11111111")


if __name__ == "__main__":
    asyncio.run(init_rbac_data())
