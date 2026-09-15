"""AI 对话会话与推理审计中心专属 API 路由。

提供全站 C 端用户 AI 聊天会话大盘检索、消息全景历史回溯、推理思维链与 Token 消耗审计、违规涉密会话清理。
所有接口均受 RequirePermission 声明式权限守卫控制。

Usage:
    GET    /api/v1/admin/chat/sessions
    GET    /api/v1/admin/chat/sessions/{session_id}/transcript
    DELETE /api/v1/admin/chat/sessions/{session_id}
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
from app.models.character import Character
from app.models.chat import ChatMessage, ChatSession
from app.models.user import User, UserProfile
from app.schemas.admin import (
    AdminChatMessageItem,
    AdminChatSessionItem,
    AdminChatSessionPageResult,
    AdminChatTranscriptResult,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["AI对话与推理审计"])


@router.get("/sessions", response_model=AdminChatSessionPageResult, summary="分页检索全站用户 AI 会话大盘")
async def list_admin_chat_sessions(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(None, description="搜索用户名称/邮箱/角色名称/备注"),
    model_id: str | None = Query(None, description="模型标识过滤 (如 glm-5.2-o1)"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:chat:view")),
) -> AdminChatSessionPageResult:
    """多维分页查询用户对话会话列表，预加载用户信息、角色卡并统计 Token 消耗。"""
    query = (
        select(ChatSession)
        .options(
            selectinload(ChatSession.user).selectinload(User.profile),
            selectinload(ChatSession.character),
        )
    )

    if model_id:
        query = query.where(ChatSession.current_model_id == model_id)

    if keyword:
        kw = f"%{keyword.strip()}%"
        query = (
            query.outerjoin(ChatSession.user)
            .outerjoin(User.profile)
            .outerjoin(ChatSession.character)
            .where(
                or_(
                    UserProfile.username.ilike(kw),
                    User.email.ilike(kw),
                    Character.name.ilike(kw),
                    ChatSession.remark.ilike(kw),
                )
            )
        )

    # 计算总条数
    count_stmt = select(func.count(ChatSession.id))
    if model_id:
        count_stmt = count_stmt.where(ChatSession.current_model_id == model_id)
    if keyword:
        kw = f"%{keyword.strip()}%"
        count_stmt = (
            count_stmt.outerjoin(ChatSession.user)
            .outerjoin(User.profile)
            .outerjoin(ChatSession.character)
            .where(
                or_(
                    UserProfile.username.ilike(kw),
                    User.email.ilike(kw),
                    Character.name.ilike(kw),
                    ChatSession.remark.ilike(kw),
                )
            )
        )

    total_count = (await db.execute(count_stmt)).scalar() or 0

    # 执行分页
    offset = (page - 1) * size
    stmt = query.order_by(desc(ChatSession.updated_at)).offset(offset).limit(size)
    sessions = (await db.execute(stmt)).scalars().all()

    # 统计会话消息数与 Token 消耗
    session_ids = [s.id for s in sessions]
    msg_stats: dict[uuid.UUID, tuple[int, int]] = {}
    if session_ids:
        stat_stmt = (
            select(
                ChatMessage.session_id,
                func.count(ChatMessage.id),
                func.coalesce(func.sum(ChatMessage.input_tokens + ChatMessage.output_tokens), 0),
            )
            .where(ChatMessage.session_id.in_(session_ids))
            .group_by(ChatMessage.session_id)
        )
        for sid, cnt, tokens in (await db.execute(stat_stmt)).all():
            msg_stats[sid] = (cnt, int(tokens))

    items: list[AdminChatSessionItem] = []
    for s in sessions:
        user = s.user
        profile = user.profile if user else None
        char = s.character
        cnt, tokens = msg_stats.get(s.id, (0, 0))

        items.append(
            AdminChatSessionItem(
                id=s.id,
                user_id=s.user_id,
                user_name=profile.username if profile else (user.email.split("@")[0] if user else "未知用户"),
                user_email=user.email if user else "",
                user_avatar=profile.avatar_url if profile else "",
                character_id=s.character_id,
                character_name=char.name if char else "未知角色",
                character_avatar=char.avatar_url if char else "",
                current_model_id=s.current_model_id,
                mode=s.mode,
                remark=s.remark or (f"与 {char.name if char else '角色'} 的对话"),
                is_pinned=s.is_pinned,
                message_count=cnt,
                total_tokens=tokens,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
        )

    return AdminChatSessionPageResult(total=total_count, page=page, size=size, list=items)


@router.get("/sessions/{session_id}/transcript", response_model=AdminChatTranscriptResult, summary="查看会话全景历史回溯与消息流水")
async def get_admin_chat_transcript(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:chat:view")),
) -> AdminChatTranscriptResult:
    """获取指定会话的完整历史聊天记录，包含用户提问、AI思维链、Markdown正文及每轮 Token 消耗。"""
    stmt = (
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .options(
            selectinload(ChatSession.user).selectinload(User.profile),
            selectinload(ChatSession.character),
            selectinload(ChatSession.messages),
        )
    )
    s = (await db.execute(stmt)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标会话不存在")

    user = s.user
    profile = user.profile if user else None
    char = s.character

    # 排序消息
    sorted_messages = sorted(s.messages, key=lambda m: m.created_at)
    total_tokens = sum(m.input_tokens + m.output_tokens for m in sorted_messages)

    session_item = AdminChatSessionItem(
        id=s.id,
        user_id=s.user_id,
        user_name=profile.username if profile else (user.email.split("@")[0] if user else "未知用户"),
        user_email=user.email if user else "",
        user_avatar=profile.avatar_url if profile else "",
        character_id=s.character_id,
        character_name=char.name if char else "未知角色",
        character_avatar=char.avatar_url if char else "",
        current_model_id=s.current_model_id,
        mode=s.mode,
        remark=s.remark or (f"与 {char.name if char else '角色'} 的对话"),
        is_pinned=s.is_pinned,
        message_count=len(sorted_messages),
        total_tokens=total_tokens,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )

    msg_items = [
        AdminChatMessageItem(
            id=m.id,
            sender=m.sender,
            character_name=m.character_name or (char.name if m.sender == "ai" and char else None),
            avatar_url=m.avatar_url or (char.avatar_url if m.sender == "ai" and char else (profile.avatar_url if profile else None)),
            content=m.content,
            thinking_content=m.thinking_content or "",
            input_tokens=m.input_tokens,
            output_tokens=m.output_tokens,
            created_at=m.created_at,
        )
        for m in sorted_messages
    ]

    return AdminChatTranscriptResult(session=session_item, messages=msg_items)


@router.delete("/sessions/{session_id}", summary="清理/归档违规涉密会话")
async def delete_admin_chat_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:chat:manage")),
) -> dict[str, Any]:
    """物理删除违规会话及其下全部消息与分支，记录安全审计留痕。"""
    s = await db.get(ChatSession, session_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标会话不存在")

    await db.delete(s)
    await db.commit()

    logger.warning(
        f"[Admin Chat Audit] 管理员 {current_admin.username} 删除了会话 {session_id} (所属用户: {s.user_id})"
    )

    return {
        "code": 200,
        "message": "会话已彻底清理删除",
        "data": {"session_id": str(session_id)},
    }
