"""后台 RBAC 权限管理核心 API 路由。

包含用户管理、角色管理、权限菜单树查询与部门组织架构管理。
各接口严格经由 RequirePermission 细粒度权限守卫进行拦截。

Usage:
    GET/POST/PUT/DELETE /api/v1/admin/rbac/users
    GET/POST/PUT/DELETE /api/v1/admin/rbac/roles
    GET/POST/PUT/DELETE /api/v1/admin/rbac/departments
    GET                 /api/v1/admin/rbac/permissions/tree
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_async_db
from app.core.security import RequirePermission, get_current_admin_user, hash_password
from app.models.admin import (
    AdminDepartment,
    AdminPermission,
    AdminRole,
    AdminUser,
)
from app.schemas.admin import (
    AdminDepartmentCreate,
    AdminDepartmentNode,
    AdminDepartmentUpdate,
    AdminRoleCreate,
    AdminRoleItem,
    AdminRoleUpdate,
    AdminUserCreate,
    AdminUserItem,
    AdminUserPageResult,
    AdminUserResetPwd,
    AdminUserUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rbac", tags=["后台组织与权限管理"])


# ---------------- 1. 后台用户管理 (Admin Users) ----------------

@router.get("/users", response_model=AdminUserPageResult, summary="分页查询管理员列表")
async def list_admin_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(None, description="搜索用户名/姓名/邮箱"),
    department_id: uuid.UUID | None = Query(None, description="部门筛选"),
    status: str | None = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:user:view")),
) -> AdminUserPageResult:
    """按条件分页检索后台管理员列表。"""
    query = select(AdminUser).options(
        selectinload(AdminUser.department),
        selectinload(AdminUser.roles).selectinload(AdminRole.permissions),
    )

    if keyword:
        query = query.where(
            or_(
                AdminUser.username.ilike(f"%{keyword}%"),
                AdminUser.real_name.ilike(f"%{keyword}%"),
                AdminUser.email.ilike(f"%{keyword}%"),
            )
        )
    if department_id:
        query = query.where(AdminUser.department_id == department_id)
    if status:
        query = query.where(AdminUser.status == status)

    # 统计总数
    count_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # 分页排序
    items_stmt = query.order_by(AdminUser.created_at.desc()).offset((page - 1) * size).limit(size)
    items = (await db.execute(items_stmt)).scalars().all()

    user_list: list[AdminUserItem] = []
    for u in items:
        role_items = [
            AdminRoleItem(
                id=r.id,
                role_key=r.role_key,
                name=r.name,
                description=r.description,
                sort=r.sort,
                status=r.status,
                created_at=r.created_at,
                permission_ids=[p.id for p in r.permissions],
            )
            for r in u.roles
        ]
        user_list.append(
            AdminUserItem(
                id=u.id,
                username=u.username,
                email=u.email,
                real_name=u.real_name,
                avatar=u.avatar,
                phone=u.phone,
                job_number=u.job_number,
                department_id=u.department_id,
                department_name=u.department.name if u.department else None,
                is_super_admin=u.is_super_admin,
                status=u.status,
                roles=role_items,
                role_names="、".join([r.name for r in u.roles]),
                created_at=u.created_at,
                last_login_at=u.last_login_at,
                last_login_ip=u.last_login_ip,
            )
        )

    return AdminUserPageResult(total=total, page=page, size=size, list=user_list)


@router.post("/users", response_model=dict[str, Any], summary="创建管理员")
async def create_admin_user(
    body: AdminUserCreate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:user:create")),
) -> dict[str, Any]:
    """新增后台管理员并分配角色。"""
    # 唯一性检查
    exist_check = await db.execute(
        select(AdminUser).where(
            or_(AdminUser.username == body.username, AdminUser.email == body.email)
        )
    )
    if exist_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已被注册",
        )

    new_user = AdminUser(
        username=body.username,
        email=body.email,
        real_name=body.real_name,
        hashed_password=hash_password(body.password),
        phone=body.phone,
        job_number=body.job_number,
        department_id=body.department_id,
        status=body.status,
    )

    if body.role_ids:
        roles_stmt = select(AdminRole).where(AdminRole.id.in_(body.role_ids))
        roles = (await db.execute(roles_stmt)).scalars().all()
        new_user.roles = list(roles)

    db.add(new_user)
    await db.commit()
    logger.info("管理员 %s 创建了新管理员: %s", current_admin.username, new_user.username)
    return {"message": "创建成功", "id": str(new_user.id)}


@router.put("/users/{user_id}", response_model=dict[str, Any], summary="修改管理员信息")
async def update_admin_user(
    user_id: uuid.UUID,
    body: AdminUserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:user:update")),
) -> dict[str, Any]:
    """修改管理员资料与角色分配。"""
    stmt = (
        select(AdminUser)
        .where(AdminUser.id == user_id)
        .options(selectinload(AdminUser.roles))
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="管理员不存在")

    if body.email is not None:
        user.email = body.email
    if body.real_name is not None:
        user.real_name = body.real_name
    if body.phone is not None:
        user.phone = body.phone
    if body.job_number is not None:
        user.job_number = body.job_number
    if body.department_id is not None:
        user.department_id = body.department_id
    is_super = user.is_super_admin or user.username == "superadmin"

    if body.status is not None:
        if is_super and body.status != "active":
            raise HTTPException(status_code=400, detail="禁止禁用超级管理员账号")
        user.status = body.status

    if body.role_ids is not None:
        roles_stmt = select(AdminRole).where(AdminRole.id.in_(body.role_ids))
        roles = list((await db.execute(roles_stmt)).scalars().all())
        if is_super and not any(r.role_key == "super_admin" for r in roles):
            raise HTTPException(status_code=400, detail="超级管理员账号必须分配超级管理员角色 (super_admin)")
        user.roles = roles

    await db.commit()
    logger.info("管理员 %s 更新了用户 %s 的信息", current_admin.username, user.username)
    return {"message": "更新成功"}


@router.put("/users/{user_id}/reset-password", summary="重置管理员密码")
async def reset_admin_user_password(
    user_id: uuid.UUID,
    body: AdminUserResetPwd,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:user:reset_pwd")),
) -> dict[str, Any]:
    """重置管理员密码。"""
    user = (await db.execute(select(AdminUser).where(AdminUser.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="管理员不存在")

    user.hashed_password = hash_password(body.new_password)
    await db.commit()
    logger.info("管理员 %s 重置了用户 %s 的密码", current_admin.username, user.username)
    return {"message": "密码重置成功"}


@router.delete("/users/{user_id}", summary="删除管理员")
async def delete_admin_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:user:delete")),
) -> dict[str, Any]:
    """删除管理员账号（超级管理员不能删除自身）。"""
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录账号")

    user = (await db.execute(select(AdminUser).where(AdminUser.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="管理员不存在")
    if user.is_super_admin:
        raise HTTPException(status_code=400, detail="禁止删除超级管理员账号")

    await db.delete(user)
    await db.commit()
    logger.info("管理员 %s 删除了管理员: %s", current_admin.username, user.username)
    return {"message": "删除成功"}


# ---------------- 2. 后台角色管理 (Admin Roles) ----------------

@router.get("/roles", response_model=list[AdminRoleItem], summary="查询所有角色列表")
async def list_admin_roles(
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:role:view")),
) -> list[AdminRoleItem]:
    """获取所有角色列表及其绑定的权限 ID 清单。"""
    stmt = select(AdminRole).options(selectinload(AdminRole.permissions)).order_by(AdminRole.sort.asc())
    roles = (await db.execute(stmt)).scalars().all()

    return [
        AdminRoleItem(
            id=r.id,
            role_key=r.role_key,
            name=r.name,
            description=r.description,
            sort=r.sort,
            status=r.status,
            created_at=r.created_at,
            permission_ids=[p.id for p in r.permissions],
        )
        for r in roles
    ]


@router.post("/roles", response_model=dict[str, Any], summary="创建角色")
async def create_admin_role(
    body: AdminRoleCreate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:role:create")),
) -> dict[str, Any]:
    """新增角色并分配权限。"""
    exist_check = await db.execute(
        select(AdminRole).where(AdminRole.role_key == body.role_key)
    )
    if exist_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="角色标识已存在")

    new_role = AdminRole(
        role_key=body.role_key,
        name=body.name,
        description=body.description,
        sort=body.sort,
        status=body.status,
    )

    if body.permission_ids:
        perms_stmt = select(AdminPermission).where(AdminPermission.id.in_(body.permission_ids))
        perms = (await db.execute(perms_stmt)).scalars().all()
        new_role.permissions = list(perms)

    db.add(new_role)
    await db.commit()
    return {"message": "角色创建成功", "id": str(new_role.id)}


@router.put("/roles/{role_id}", response_model=dict[str, Any], summary="更新角色及权限")
async def update_admin_role(
    role_id: uuid.UUID,
    body: AdminRoleUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:role:update")),
) -> dict[str, Any]:
    """修改角色信息及重新分配权限。"""
    stmt = (
        select(AdminRole)
        .where(AdminRole.id == role_id)
        .options(selectinload(AdminRole.permissions))
    )
    role = (await db.execute(stmt)).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if body.name is not None:
        role.name = body.name
    if body.description is not None:
        role.description = body.description
    if body.sort is not None:
        role.sort = body.sort
    if body.status is not None:
        role.status = body.status

    if body.permission_ids is not None:
        perms_stmt = select(AdminPermission).where(AdminPermission.id.in_(body.permission_ids))
        perms = (await db.execute(perms_stmt)).scalars().all()
        role.permissions = list(perms)

    await db.commit()
    return {"message": "角色更新成功"}


@router.delete("/roles/{role_id}", summary="删除角色")
async def delete_admin_role(
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:role:delete")),
) -> dict[str, Any]:
    """删除指定角色（超级管理员角色不可删除）。"""
    role = (await db.execute(select(AdminRole).where(AdminRole.id == role_id))).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.role_key == "super_admin":
        raise HTTPException(status_code=400, detail="禁止删除超级管理员角色")

    await db.delete(role)
    await db.commit()
    return {"message": "角色删除成功"}


# ---------------- 3. 组织部门管理 (Admin Departments) ----------------

def build_dept_tree(depts: list[AdminDepartment], parent_id: Any = None) -> list[AdminDepartmentNode]:
    """递归生成部门树结构。"""
    nodes: list[AdminDepartmentNode] = []
    curr_items = [d for d in depts if d.parent_id == parent_id]
    curr_items.sort(key=lambda x: x.sort)

    for d in curr_items:
        node = AdminDepartmentNode(
            id=d.id,
            parent_id=d.parent_id,
            name=d.name,
            leader=d.leader,
            phone=d.phone,
            sort=d.sort,
            status=d.status,
            created_at=d.created_at,
            children=build_dept_tree(depts, d.id),
        )
        nodes.append(node)
    return nodes


@router.get("/departments", response_model=list[AdminDepartmentNode], summary="获取部门架构树")
async def get_departments_tree(
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:dept:view")),
) -> list[AdminDepartmentNode]:
    """获取完整的部门架构树形结构。"""
    stmt = select(AdminDepartment).order_by(AdminDepartment.sort.asc())
    depts = list((await db.execute(stmt)).scalars().all())
    return build_dept_tree(depts, None)


@router.post("/departments", response_model=dict[str, Any], summary="新增部门")
async def create_department(
    body: AdminDepartmentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:dept:create")),
) -> dict[str, Any]:
    """新增组织架构部门。"""
    new_dept = AdminDepartment(
        parent_id=body.parent_id,
        name=body.name,
        leader=body.leader,
        phone=body.phone,
        sort=body.sort,
        status=body.status,
    )
    db.add(new_dept)
    await db.commit()
    return {"message": "部门创建成功", "id": str(new_dept.id)}


@router.put("/departments/{dept_id}", response_model=dict[str, Any], summary="修改部门")
async def update_department(
    dept_id: uuid.UUID,
    body: AdminDepartmentUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:dept:update")),
) -> dict[str, Any]:
    """更新组织架构部门信息。"""
    dept = (await db.execute(select(AdminDepartment).where(AdminDepartment.id == dept_id))).scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")

    if body.name is not None:
        dept.name = body.name
    if body.leader is not None:
        dept.leader = body.leader
    if body.phone is not None:
        dept.phone = body.phone
    if body.sort is not None:
        dept.sort = body.sort
    if body.status is not None:
        dept.status = body.status
    if body.parent_id is not None:
        if body.parent_id == dept_id:
            raise HTTPException(status_code=400, detail="上级部门不能为自身")
        dept.parent_id = body.parent_id

    await db.commit()
    return {"message": "部门更新成功"}


@router.delete("/departments/{dept_id}", summary="删除部门")
async def delete_department(
    dept_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:dept:delete")),
) -> dict[str, Any]:
    """删除部门。"""
    dept = (await db.execute(select(AdminDepartment).where(AdminDepartment.id == dept_id))).scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")

    # 检查是否有子部门
    sub_count = (
        await db.execute(
            select(func.count()).where(AdminDepartment.parent_id == dept_id)
        )
    ).scalar() or 0
    if sub_count > 0:
        raise HTTPException(status_code=400, detail="存在子部门，请先删除或移动子部门")

    await db.delete(dept)
    await db.commit()
    return {"message": "部门删除成功"}


# ---------------- 4. 权限与菜单树查询 (Permissions Tree) ----------------

def build_all_perms_tree(perms: list[AdminPermission], parent_id: Any = None) -> list[dict[str, Any]]:
    """递归生成全量权限树（包含目录、菜单、按钮）。"""
    nodes: list[dict[str, Any]] = []
    curr_items = [p for p in perms if p.parent_id == parent_id]
    curr_items.sort(key=lambda x: x.sort)

    for p in curr_items:
        node: dict[str, Any] = {
            "id": str(p.id),
            "parent_id": str(p.parent_id) if p.parent_id else None,
            "type": p.type,
            "title": p.title,
            "code": p.code,
            "path": p.path,
            "icon": p.icon,
            "sort": p.sort,
            "status": p.status,
            "children": build_all_perms_tree(perms, p.id),
        }
        nodes.append(node)
    return nodes


@router.get("/permissions/tree", summary="获取系统完整权限与菜单树")
async def get_permissions_tree(
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("system:role:view")),
) -> list[dict[str, Any]]:
    """获取包含目录、菜单与按钮动作的全量权限树，供角色分配权限时勾选使用。"""
    stmt = select(AdminPermission).order_by(AdminPermission.sort.asc())
    all_perms = list((await db.execute(stmt)).scalars().all())
    return build_all_perms_tree(all_perms, None)
