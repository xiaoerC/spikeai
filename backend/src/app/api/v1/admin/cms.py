"""系统公告与运营活动管理专属 API 路由 (CMS)。

提供平台系统公告 (Notice) 与运营活动 (Activity) 的全生命周期发布、编辑、状态切换与下架删除。
所有接口均受 RequirePermission 声明式权限守卫控制。

Usage:
    GET    /api/v1/admin/cms/notices
    POST   /api/v1/admin/cms/notices
    PUT    /api/v1/admin/cms/notices/{notice_id}
    DELETE /api/v1/admin/cms/notices/{notice_id}

    GET    /api/v1/admin/cms/activities
    POST   /api/v1/admin/cms/activities
    PUT    /api/v1/admin/cms/activities/{activity_id}
    DELETE /api/v1/admin/cms/activities/{activity_id}
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import RequirePermission
from app.models.admin import AdminUser
from app.models.ops import Activity, Notice
from app.schemas.admin import (
    AdminActivityCreate,
    AdminActivityItem,
    AdminActivityPageResult,
    AdminActivityUpdate,
    AdminNoticeCreate,
    AdminNoticeItem,
    AdminNoticePageResult,
    AdminNoticeUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cms", tags=["系统公告与运营活动管理"])


# ===================== 系统公告管理 =====================

@router.get("/notices", response_model=AdminNoticePageResult, summary="分页查询系统公告列表")
async def list_admin_notices(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(None, description="搜索公告标题或摘要"),
    category: str | None = Query(None, description="分类 (系统公告/更新日志/活动公告)"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:notice:view")),
) -> AdminNoticePageResult:
    """多维分页查询系统公告与更新日志。"""
    query = select(Notice)
    if category:
        query = query.where(Notice.category == category)
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.where((Notice.title.ilike(kw)) | (Notice.summary.ilike(kw)))

    count_stmt = select(func.count(Notice.id))
    if category:
        count_stmt = count_stmt.where(Notice.category == category)
    if keyword:
        kw = f"%{keyword.strip()}%"
        count_stmt = count_stmt.where((Notice.title.ilike(kw)) | (Notice.summary.ilike(kw)))

    total = (await db.execute(count_stmt)).scalar() or 0
    offset = (page - 1) * size
    stmt = query.order_by(desc(Notice.created_at)).offset(offset).limit(size)
    notices = (await db.execute(stmt)).scalars().all()

    items = [
        AdminNoticeItem(
            id=n.id,
            title=n.title,
            category=n.category,
            date_text=n.date_text,
            badge_type=n.badge_type,
            summary=n.summary,
            content_html=n.content_html,
            created_at=n.created_at,
        )
        for n in notices
    ]

    return AdminNoticePageResult(total=total, page=page, size=size, list=items)


@router.post("/notices", response_model=AdminNoticeItem, status_code=status.HTTP_201_CREATED, summary="新建系统公告")
async def create_admin_notice(
    body: AdminNoticeCreate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:notice:manage")),
) -> AdminNoticeItem:
    """创建并即刻全站发布一条系统公告或更新日志。"""
    notice = Notice(
        id=uuid.uuid4(),
        title=body.title,
        category=body.category,
        date_text=body.date_text,
        badge_type=body.badge_type,
        summary=body.summary,
        content_html=body.content_html,
    )
    db.add(notice)
    await db.commit()
    await db.refresh(notice)

    logger.info(f"[Admin Notice] 管理员 {current_admin.username} 发布了新公告: {notice.title} ({notice.id})")
    return AdminNoticeItem.model_validate(notice)


@router.put("/notices/{notice_id}", response_model=AdminNoticeItem, summary="编辑更新系统公告")
async def update_admin_notice(
    notice_id: uuid.UUID,
    body: AdminNoticeUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:notice:manage")),
) -> AdminNoticeItem:
    """修改既有系统公告的标题、分类、内容或摘要。"""
    notice = await db.get(Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notice, field, value)

    await db.commit()
    await db.refresh(notice)

    logger.info(f"[Admin Notice] 管理员 {current_admin.username} 更新了公告: {notice.title} ({notice.id})")
    return AdminNoticeItem.model_validate(notice)


@router.delete("/notices/{notice_id}", summary="删除系统公告")
async def delete_admin_notice(
    notice_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:notice:manage")),
) -> dict[str, Any]:
    """物理下架并删除公告。"""
    notice = await db.get(Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    await db.delete(notice)
    await db.commit()

    logger.warning(f"[Admin Notice] 管理员 {current_admin.username} 删除了公告: {notice.title} ({notice.id})")
    return {"code": 200, "message": "公告已删除", "data": {"notice_id": str(notice_id)}}


# ===================== 运营活动管理 =====================

@router.get("/activities", response_model=AdminActivityPageResult, summary="分页查询运营活动列表")
async def list_admin_activities(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(None, description="搜索活动标题或奖励描述"),
    status_filter: str | None = Query(None, alias="status", description="状态 (active/ended)"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:activity:view")),
) -> AdminActivityPageResult:
    """多维分页查询平台运营活动列表。"""
    query = select(Activity)
    if status_filter:
        query = query.where(Activity.status == status_filter)
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.where((Activity.title.ilike(kw)) | (Activity.reward_text.ilike(kw)))

    count_stmt = select(func.count(Activity.id))
    if status_filter:
        count_stmt = count_stmt.where(Activity.status == status_filter)
    if keyword:
        kw = f"%{keyword.strip()}%"
        count_stmt = count_stmt.where((Activity.title.ilike(kw)) | (Activity.reward_text.ilike(kw)))

    total = (await db.execute(count_stmt)).scalar() or 0
    offset = (page - 1) * size
    stmt = query.order_by(desc(Activity.created_at)).offset(offset).limit(size)
    activities = (await db.execute(stmt)).scalars().all()

    items = [
        AdminActivityItem(
            id=a.id,
            title=a.title,
            tag=a.tag,
            reward_text=a.reward_text,
            date_range=a.date_range,
            status=a.status,
            rules=a.rules or [],
            created_at=a.created_at,
        )
        for a in activities
    ]

    return AdminActivityPageResult(total=total, page=page, size=size, list=items)


@router.post("/activities", response_model=AdminActivityItem, status_code=status.HTTP_201_CREATED, summary="新建运营活动")
async def create_admin_activity(
    body: AdminActivityCreate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:activity:manage")),
) -> AdminActivityItem:
    """创建并上线新的平台运营活动。"""
    activity = Activity(
        id=uuid.uuid4(),
        title=body.title,
        tag=body.tag,
        reward_text=body.reward_text,
        date_range=body.date_range,
        status=body.status,
        rules=body.rules,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    logger.info(f"[Admin Activity] 管理员 {current_admin.username} 发布了新活动: {activity.title} ({activity.id})")
    return AdminActivityItem.model_validate(activity)


@router.put("/activities/{activity_id}", response_model=AdminActivityItem, summary="编辑更新运营活动")
async def update_admin_activity(
    activity_id: uuid.UUID,
    body: AdminActivityUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:activity:manage")),
) -> AdminActivityItem:
    """更新运营活动的标题、奖励、规则或开启/结束状态。"""
    activity = await db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="活动不存在")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)

    await db.commit()
    await db.refresh(activity)

    logger.info(f"[Admin Activity] 管理员 {current_admin.username} 更新了活动: {activity.title} ({activity.id})")
    return AdminActivityItem.model_validate(activity)


@router.delete("/activities/{activity_id}", summary="删除运营活动")
async def delete_admin_activity(
    activity_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:activity:manage")),
) -> dict[str, Any]:
    """删除指定的运营活动。"""
    activity = await db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="活动不存在")

    await db.delete(activity)
    await db.commit()

    logger.warning(f"[Admin Activity] 管理员 {current_admin.username} 删除了活动: {activity.title} ({activity.id})")
    return {"code": 200, "message": "活动已删除", "data": {"activity_id": str(activity_id)}}
