"""AI 角色卡与设定集审核及治理中心专属 API 路由。

提供全量角色卡资产分页多维检索、上下架/违规下架审核、深层提示词画像与世界书词条档案透视。
所有接口均受 RequirePermission 声明式权限守卫控制。

Usage:
    GET  /api/v1/admin/characters
    POST /api/v1/admin/characters/{char_id}/status
    GET  /api/v1/admin/characters/{char_id}/detail
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_async_db
from app.core.security import RequirePermission
from app.models.admin import AdminUser
from app.models.character import Character, CharacterWorldBook
from app.models.user import User, UserProfile
from app.schemas.admin import (
    AdminBatchCharacterIds,
    AdminCharacterDetail,
    AdminCharacterItem,
    AdminCharacterPageResult,
    AdminCharacterStatusUpdate,
    WorldBookEntryItem,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/characters", tags=["AI角色卡与设定集治理"])


@router.get("", response_model=AdminCharacterPageResult, summary="分页检索角色卡资产列表")
async def list_admin_characters(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(None, description="搜索角色名称或作者用户名"),
    category: str | None = Query(None, description="大分类 (story/nsfw/rpg)"),
    char_status: str | None = Query(None, alias="status", description="状态 (published/private/banned/draft)"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:character:view")),
) -> AdminCharacterPageResult:
    """多维分页查询平台所有角色卡，预加载创作者信息、统计指标与世界书词条数。"""
    query = (
        select(Character)
        .options(
            selectinload(Character.author).selectinload(User.profile),
            selectinload(Character.metrics),
        )
    )
    count_stmt = select(func.count(Character.id))

    if category:
        query = query.where(Character.category == category)
        count_stmt = count_stmt.where(Character.category == category)

    if char_status:
        query = query.where(Character.status == char_status)
        count_stmt = count_stmt.where(Character.status == char_status)
    else:
        # 常规列表默认排除已软删除进入回收站的角色卡
        query = query.where(Character.status != "deleted")
        count_stmt = count_stmt.where(Character.status != "deleted")
    if keyword:
        kw = f"%{keyword.strip()}%"
        count_stmt = count_stmt.outerjoin(Character.author).outerjoin(User.profile).where(
            or_(
                Character.name.ilike(kw),
                UserProfile.username.ilike(kw),
            )
        )

    total_count = (await db.execute(count_stmt)).scalar() or 0

    # 执行分页
    offset = (page - 1) * size
    stmt = query.order_by(desc(Character.created_at)).offset(offset).limit(size)
    characters = (await db.execute(stmt)).scalars().all()

    # 统计所含世界书条目数
    char_ids = [c.id for c in characters]
    wb_counts: dict[uuid.UUID, int] = {}
    if char_ids:
        wb_stmt = (
            select(CharacterWorldBook.character_id, func.count(CharacterWorldBook.id))
            .where(CharacterWorldBook.character_id.in_(char_ids))
            .group_by(CharacterWorldBook.character_id)
        )
        for cid, count in (await db.execute(wb_stmt)).all():
            wb_counts[cid] = count

    items: list[AdminCharacterItem] = []
    for c in characters:
        author = c.author
        author_profile = author.profile if author else None
        m = c.metrics

        items.append(
            AdminCharacterItem(
                id=c.id,
                name=c.name,
                avatar_url=c.avatar_url,
                banner_url=c.banner_url,
                category=c.category,
                description=c.description,
                status=c.status,
                tags=c.tags or [],
                settings_word_count=c.settings_word_count,
                version=c.version,
                author_id=c.author_id,
                author_name=author_profile.username if author_profile else (author.email.split("@")[0] if author else "官方"),
                author_email=author.email if author else "",
                chat_count=m.chat_count if m else 0,
                like_count=m.like_count if m else 0,
                favorite_count=m.favorite_count if m else 0,
                rating=m.rating if m else 5.0,
                worldbook_entry_count=wb_counts.get(c.id, 0),
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return AdminCharacterPageResult(total=total_count, page=page, size=size, list=items)


@router.post("/{char_id}/status", summary="审核或变更角色卡状态 (上架/私有/违规下架)")
async def update_character_status(
    char_id: uuid.UUID,
    body: AdminCharacterStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:character:status")),
) -> dict[str, Any]:
    """对角色卡执行上架、下架私有化或违规冻结封禁操作。"""
    if body.status not in ("published", "private", "banned"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="非法角色状态，仅限 published / private / banned",
        )

    char = await db.get(Character, char_id)
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标角色卡不存在")

    old_status = char.status
    char.status = body.status
    await db.commit()

    logger.warning(
        f"[Admin Content Audit] 管理员 {current_admin.username} 将角色卡 {char.name}({char.id}) "
        f"状态从 {old_status} 修改为 {body.status}，处置理由: {body.reason or '无'}"
    )

    return {
        "code": 200,
        "message": f"角色卡状态已变更为 {body.status}",
        "data": {"character_id": str(char.id), "status": char.status},
    }


@router.get("/{char_id}/detail", response_model=AdminCharacterDetail, summary="查看角色卡深层档案详情")
async def get_character_detail(
    char_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:character:view")),
) -> AdminCharacterDetail:
    """获取角色卡的全景提示词画像、开场白、备选问候语及世界书词条条目列表。"""
    stmt = (
        select(Character)
        .where(Character.id == char_id)
        .options(
            selectinload(Character.author).selectinload(User.profile),
            selectinload(Character.metrics),
            selectinload(Character.worldbooks),
        )
    )
    char = (await db.execute(stmt)).scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标角色卡不存在")

    author = char.author
    author_profile = author.profile if author else None
    m = char.metrics

    wb_entries = [
        WorldBookEntryItem(
            id=wb.id,
            keys=wb.keys or [],
            content=wb.content,
            constant=wb.constant,
            position=wb.position,
        )
        for wb in char.worldbooks
    ]

    return AdminCharacterDetail(
        id=char.id,
        name=char.name,
        avatar_url=char.avatar_url,
        banner_url=char.banner_url,
        category=char.category,
        description=char.description,
        status=char.status,
        tags=char.tags or [],
        settings_word_count=char.settings_word_count,
        version=char.version,
        author_id=char.author_id,
        author_name=author_profile.username if author_profile else (author.email.split("@")[0] if author else "官方"),
        author_email=author.email if author else "",
        chat_count=m.chat_count if m else 0,
        like_count=m.like_count if m else 0,
        favorite_count=m.favorite_count if m else 0,
        rating=m.rating if m else 5.0,
        worldbook_entry_count=len(wb_entries),
        created_at=char.created_at,
        updated_at=char.updated_at,
        personality=char.personality,
        scenario=char.scenario,
        first_mes=char.first_mes,
        system_prompt=char.system_prompt,
        post_history_instructions=char.post_history_instructions,
        prologue_title=char.prologue_title,
        creator_notes=char.creator_notes,
        alternate_greetings=char.alternate_greetings or [],
        worldbook_entries=wb_entries,
    )


@router.delete("/{char_id}", summary="软删除角色卡 (移入回收站)")
async def soft_delete_character(
    char_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:character:status")),
) -> dict[str, Any]:
    """将已下架角色卡逻辑软删除，移入回收站。"""
    char = await db.get(Character, char_id)
    if not char:
        raise HTTPException(status_code=404, detail="目标角色卡不存在")

    if char.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该角色卡当前处于【已上架】运营状态，请先执行【违规下架】或下架私有化后再执行删除",
        )

    char.status = "deleted"
    await db.commit()
    logger.warning(
        f"[Admin Content Audit] 管理员 {current_admin.username} 软删除了角色卡 {char.name}({char.id})"
    )
    return {"code": 200, "message": f"角色卡《{char.name}》已移入回收站"}


@router.post("/batch-delete", summary="批量软删除已下架角色卡")
async def batch_soft_delete_characters(
    body: AdminBatchCharacterIds,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:character:status")),
) -> dict[str, Any]:
    """批量将多张已下架角色卡移入回收站。"""
    stmt = select(Character).where(Character.id.in_(body.character_ids))
    chars = list((await db.execute(stmt)).scalars().all())
    if not chars:
        raise HTTPException(status_code=404, detail="未找到指定的角色卡")

    published_names = [c.name for c in chars if c.status == "published"]
    if published_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"所选角色卡中包含【已上架】卡片：{', '.join(published_names)}。请先下架后再执行批量删除",
        )

    for c in chars:
        c.status = "deleted"

    await db.commit()
    logger.warning(
        f"[Admin Content Audit] 管理员 {current_admin.username} 批量软删除了 {len(chars)} 张角色卡"
    )
    return {"code": 200, "message": f"已成功将 {len(chars)} 张角色卡移入回收站", "count": len(chars)}


@router.post("/{char_id}/restore", summary="从回收站恢复角色卡")
async def restore_character(
    char_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:character:status")),
) -> dict[str, Any]:
    """将回收站中的角色卡还原为下架私有状态。"""
    char = await db.get(Character, char_id)
    if not char:
        raise HTTPException(status_code=404, detail="目标角色卡不存在")

    if char.status != "deleted":
        raise HTTPException(status_code=400, detail="该角色卡不在回收站中，无需恢复")

    char.status = "banned"  # 恢复为违规下架状态，需重新审核才可上架
    await db.commit()
    logger.info(
        f"[Admin Content Audit] 管理员 {current_admin.username} 从回收站恢复了角色卡 {char.name}({char.id})"
    )
    return {"code": 200, "message": f"角色卡《{char.name}》已成功从回收站恢复"}


@router.delete("/{char_id}/destroy", summary="彻底粉碎角色卡 (物理删除，不可逆)")
async def hard_destroy_character(
    char_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:character:status")),
) -> dict[str, Any]:
    """物理硬删除角色卡，从数据库彻底抹除本体及其关联数据。"""
    char = await db.get(Character, char_id)
    if not char:
        raise HTTPException(status_code=404, detail="目标角色卡不存在")

    if char.status != "deleted":
        raise HTTPException(
            status_code=400,
            detail="仅限处于【回收站 (已删除)】状态的角色卡才允许执行彻底粉碎！",
        )

    char_name = char.name
    await db.delete(char)
    await db.commit()
    logger.critical(
        f"[Admin Content Audit] 管理员 {current_admin.username} 彻底物理粉碎了角色卡 {char_name}({char_id})"
    )
    return {"code": 200, "message": f"角色卡《{char_name}》已彻底物理粉碎清除"}


@router.post("/batch-destroy", summary="批量彻底粉碎回收站中的角色卡")
async def batch_hard_destroy_characters(
    body: AdminBatchCharacterIds,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:character:status")),
) -> dict[str, Any]:
    """批量物理硬删除回收站中的角色卡。"""
    stmt = select(Character).where(Character.id.in_(body.character_ids))
    chars = list((await db.execute(stmt)).scalars().all())
    if not chars:
        raise HTTPException(status_code=404, detail="未找到指定的角色卡")

    non_deleted = [c.name for c in chars if c.status != "deleted"]
    if non_deleted:
        raise HTTPException(
            status_code=400,
            detail=f"以下角色卡未进入回收站，禁止物理粉碎：{', '.join(non_deleted)}",
        )

    count = len(chars)
    for c in chars:
        await db.delete(c)

    await db.commit()
    logger.critical(
        f"[Admin Content Audit] 管理员 {current_admin.username} 批量彻底物理粉碎了 {count} 张角色卡"
    )
    return {"code": 200, "message": f"已彻底物理粉碎 {count} 张角色卡", "count": count}
