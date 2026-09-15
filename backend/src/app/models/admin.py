"""后台管理系统 RBAC 权限与审计领域数据模型。

包含后台用户账户 (AdminUser)、组织部门 (AdminDepartment)、角色 (AdminRole)、
树形权限/菜单 (AdminPermission) 以及操作审计日志 (AdminAuditLog)。

严格物理隔离于前台 C 端用户体系。

Usage:
    >>> from app.models.admin import AdminUser, AdminRole, AdminPermission
    >>> from sqlalchemy import select
    >>> stmt = select(AdminUser).where(AdminUser.username == "superadmin")
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base

# 多对多关联表: 后台用户 <-> 角色
admin_user_roles = Table(
    "admin_user_roles",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("admin_users.id", ondelete="CASCADE"),
        primary_key=True,
        doc="后台用户 ID",
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("admin_roles.id", ondelete="CASCADE"),
        primary_key=True,
        doc="角色 ID",
    ),
)

# 多对多关联表: 角色 <-> 权限
admin_role_permissions = Table(
    "admin_role_permissions",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("admin_roles.id", ondelete="CASCADE"),
        primary_key=True,
        doc="角色 ID",
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("admin_permissions.id", ondelete="CASCADE"),
        primary_key=True,
        doc="权限/菜单 ID",
    ),
)


class AdminDepartment(Base):
    """组织架构与部门数据模型（树形自引用）。"""

    __tablename__ = "admin_departments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="部门唯一 UUID",
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="上级父部门 ID",
    )
    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="部门名称",
    )
    leader: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="部门负责人姓名",
    )
    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        doc="联系电话",
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="显示排序权重 (越小越靠前)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        doc="状态 (active / disabled)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="更新时间",
    )

    # 关联关系
    children: Mapped[list["AdminDepartment"]] = relationship(
        "AdminDepartment",
        backref="parent",
        remote_side=[id],
        cascade="all, delete-orphan",
        single_parent=True,
    )
    users: Mapped[list["AdminUser"]] = relationship(
        "AdminUser",
        back_populates="department",
        lazy="selectin",
    )


class AdminRole(Base):
    """后台角色数据模型。"""

    __tablename__ = "admin_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="角色唯一 UUID",
    )
    role_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        doc="角色唯一英文键名 (如 super_admin, auditor, ops)",
    )
    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="角色中文显示名称",
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="角色职责与权限描述",
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="排序权重",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        doc="状态 (active / disabled)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="更新时间",
    )

    # 关联关系
    users: Mapped[list["AdminUser"]] = relationship(
        "AdminUser",
        secondary=admin_user_roles,
        back_populates="roles",
        lazy="selectin",
    )
    permissions: Mapped[list["AdminPermission"]] = relationship(
        "AdminPermission",
        secondary=admin_role_permissions,
        back_populates="roles",
        lazy="selectin",
    )


class AdminPermission(Base):
    """后台权限与菜单资源模型（树形自引用）。

    分为三类:
    - directory: 折叠目录
    - menu: 页面路由组件
    - button: 页面内操作按钮/接口细粒度权限 (如 system:user:add)
    """

    __tablename__ = "admin_permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="权限节点唯一 UUID",
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_permissions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="上级父权限 ID (顶级为 None)",
    )
    type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        doc="节点类型: directory(目录) / menu(菜单) / button(按钮)",
    )
    title: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="菜单显示标题 (如 '用户管理', '创建角色')",
    )
    name: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="前端路由名称 (如 'SystemUser')",
    )
    code: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        doc="权限唯一识别码 (如 'system:user:view', 'system:user:add')",
    )
    path: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="路由路径 (如 '/om/user')",
    )
    component: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="前端 SFC 组件路径 (如 'views/om/user/index.vue')",
    )
    icon: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="菜单图标名称 (如 'User', 'Lock', 'Setting')",
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="排序权重",
    )
    is_hidden: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="是否在侧边栏中隐藏",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        doc="状态 (active / disabled)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="更新时间",
    )

    # 关联关系
    children: Mapped[list["AdminPermission"]] = relationship(
        "AdminPermission",
        backref="parent",
        remote_side=[id],
        cascade="all, delete-orphan",
        single_parent=True,
    )
    roles: Mapped[list["AdminRole"]] = relationship(
        "AdminRole",
        secondary=admin_role_permissions,
        back_populates="permissions",
        lazy="selectin",
    )


class AdminUser(Base):
    """后台运营与系统管理员用户表。"""

    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="管理员唯一主键 UUID",
    )
    username: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        doc="登录用户名",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="管理员工作邮箱",
    )
    real_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="真实姓名",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt 密码哈希",
    )
    avatar: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        doc="管理员头像 URL",
    )
    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        doc="手机联系方式",
    )
    job_number: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        doc="员工工号",
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="所属部门 ID",
    )
    is_super_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="是否超级管理员 (True 跳过任何权限校验)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        doc="状态 (active / disabled)",
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="最后成功登录时间",
    )
    last_login_ip: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="最后登录 IP 地址",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="更新时间",
    )

    # 关联关系
    department: Mapped["AdminDepartment | None"] = relationship(
        "AdminDepartment",
        back_populates="users",
        lazy="selectin",
    )
    roles: Mapped[list["AdminRole"]] = relationship(
        "AdminRole",
        secondary=admin_user_roles,
        back_populates="users",
        lazy="selectin",
    )


class AdminAuditLog(Base):
    """后台敏感与关键操作审计日志表。"""

    __tablename__ = "admin_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="审计记录 UUID",
    )
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        doc="操作管理员 UUID",
    )
    operator_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="操作人员账号或姓名",
    )
    module: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="操作所属系统模块 (如 '系统用户', '角色权限')",
    )
    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="具体动作说明 (如 '创建管理员', '修改权限')",
    )
    method: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        doc="HTTP 请求方法 (GET, POST, PUT, DELETE)",
    )
    api_endpoint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="请求接口路径",
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="客户端 IP",
    )
    request_params: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        doc="脱敏后的请求参数",
    )
    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="HTTP 响应状态码",
    )
    cost_ms: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="执行耗时 (毫秒)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="操作时间",
    )
