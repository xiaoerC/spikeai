"""C 端用户与资产治理中心专属 API 路由。

包含 C 端用户画像分页检索、账号状态封禁/解冻、钱包资金流水审计及金融级悲观行级锁调账。
所有接口均经由 RequirePermission 权限拦截器保护。

Usage:
    GET  /api/v1/admin/c-users
    POST /api/v1/admin/c-users/{user_id}/status
    GET  /api/v1/admin/c-users/{user_id}/wallet-transactions
    POST /api/v1/admin/c-users/{user_id}/wallet/adjust
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
from app.models.chat import ChatSession
from app.models.user import User, UserProfile, UserWallet, WalletTransaction
from app.schemas.admin import (
    CUserItem,
    CUserPageResult,
    CUserStatusUpdate,
    WalletAdjustRequest,
    WalletTransactionItem,
    WalletTransactionPageResult,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/c-users", tags=["C端用户与资产治理"])


@router.get("", response_model=CUserPageResult, summary="分页查询 C 端用户列表")
async def list_c_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(None, description="搜索用户名或邮箱"),
    status_filter: str | None = Query(None, alias="status", description="状态筛选 (active/banned/suspended)"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:cuser:view")),
) -> CUserPageResult:
    """按关键词与状态筛选 C 端用户列表，聚合展示钱包余额与基础统计。"""
    query = (
        select(User)
        .options(
            selectinload(User.profile),
            selectinload(User.wallet),
        )
    )

    if status_filter:
        query = query.where(User.status == status_filter)

    if keyword:
        keyword_like = f"%{keyword.strip()}%"
        query = query.outerjoin(User.profile).where(
            or_(
                User.email.ilike(keyword_like),
                UserProfile.username.ilike(keyword_like),
            )
        )

    # 计算总数
    count_stmt = select(func.count(User.id))
    if status_filter:
        count_stmt = count_stmt.where(User.status == status_filter)
    if keyword:
        keyword_like = f"%{keyword.strip()}%"
        count_stmt = count_stmt.outerjoin(User.profile).where(
            or_(
                User.email.ilike(keyword_like),
                UserProfile.username.ilike(keyword_like),
            )
        )

    total_count = (await db.execute(count_stmt)).scalar() or 0

    # 分页查询
    offset = (page - 1) * size
    stmt = query.order_by(desc(User.created_at)).offset(offset).limit(size)
    users = (await db.execute(stmt)).scalars().all()

    # 查询角色卡数与会话数聚合
    user_ids = [u.id for u in users]
    char_counts: dict[uuid.UUID, int] = {}
    chat_counts: dict[uuid.UUID, int] = {}

    if user_ids:
        # 统计角色卡数
        char_stmt = (
            select(Character.author_id, func.count(Character.id))
            .where(Character.author_id.in_(user_ids))
            .group_by(Character.author_id)
        )
        for author_id, c in (await db.execute(char_stmt)).all():
            char_counts[author_id] = c

        # 统计对话会话数
        chat_stmt = (
            select(ChatSession.user_id, func.count(ChatSession.id))
            .where(ChatSession.user_id.in_(user_ids))
            .group_by(ChatSession.user_id)
        )
        for uid, c in (await db.execute(chat_stmt)).all():
            chat_counts[uid] = c

    items: list[CUserItem] = []
    for u in users:
        p = u.profile
        w = u.wallet
        items.append(
            CUserItem(
                id=u.id,
                email=u.email,
                username=p.username if p else u.email.split("@")[0],
                avatar_url=p.avatar_url if p else "",
                status=u.status,
                invite_code=u.invite_code,
                vip_level=p.vip_level if p else 0,
                player_level=p.player_level if p else 1,
                player_xp=p.player_xp if p else 0,
                creator_level=p.creator_level if p else 1,
                creator_xp=p.creator_xp if p else 0,
                star_coins=w.star_coins if w else 0,
                moon_gems=w.moon_gems if w else 0,
                character_count=char_counts.get(u.id, 0),
                chat_session_count=chat_counts.get(u.id, 0),
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
        )

    return CUserPageResult(total=total_count, page=page, size=size, list=items)


@router.post("/{user_id}/status", summary="变更 C 端用户状态 (封禁/解冻)")
async def update_c_user_status(
    user_id: uuid.UUID,
    body: CUserStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:cuser:status")),
) -> dict[str, Any]:
    """对违规 C 端用户执行封禁或解冻，记录安全处置审计日志。"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标 C 端用户不存在")

    old_status = user.status
    user.status = body.status
    await db.commit()

    logger.warning(
        f"[Admin Security] 管理员 {current_admin.username} 将 C 端用户 {user.email}({user.id}) "
        f"状态从 {old_status} 修改为 {body.status}，处置原因: {body.reason or '无'}"
    )

    return {
        "code": 200,
        "message": f"用户状态已成功变更为 {body.status}",
        "data": {"user_id": str(user.id), "status": user.status},
    }


@router.get("/{user_id}/wallet-transactions", response_model=WalletTransactionPageResult, summary="查询用户钱包流水明细")
async def list_user_wallet_transactions(
    user_id: uuid.UUID,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    currency: str | None = Query(None, description="币种筛选 (star/moon)"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:cuser:view")),
) -> WalletTransactionPageResult:
    """查询指定 C 端用户的充值、消耗与调账流水记录。"""
    query = select(WalletTransaction).where(WalletTransaction.user_id == user_id)
    count_query = select(func.count(WalletTransaction.id)).where(WalletTransaction.user_id == user_id)

    if currency:
        query = query.where(WalletTransaction.currency == currency)
        count_query = count_query.where(WalletTransaction.currency == currency)

    total = (await db.execute(count_query)).scalar() or 0

    offset = (page - 1) * size
    stmt = query.order_by(desc(WalletTransaction.created_at)).offset(offset).limit(size)
    records = (await db.execute(stmt)).scalars().all()

    items = [
        WalletTransactionItem(
            id=r.id,
            user_id=r.user_id,
            type=r.type,
            currency=r.currency,
            amount=r.amount,
            balance_after=r.balance_after,
            description=r.description,
            created_at=r.created_at,
        )
        for r in records
    ]

    return WalletTransactionPageResult(total=total, page=page, size=size, list=items)


@router.post("/{user_id}/wallet/adjust", summary="管理员人工调账 (增扣代币)")
async def adjust_user_wallet(
    user_id: uuid.UUID,
    body: WalletAdjustRequest,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:cuser:adjust")),
) -> dict[str, Any]:
    """使用悲观行级锁 (with_for_update) 安全调整用户资产，防范高并发对账穿透。"""
    if body.currency not in ("star", "moon"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的币种类型，仅限 star 或 moon")

    if body.action not in ("add", "sub"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的调账操作，仅限 add 或 sub")

    # 使用悲观行级锁排他锁定该用户的钱包行
    lock_stmt = select(UserWallet).where(UserWallet.user_id == user_id).with_for_update()
    wallet = (await db.execute(lock_stmt)).scalar_one_or_none()

    if not wallet:
        # 如果未初始化钱包，先创建初始化
        wallet = UserWallet(user_id=user_id, star_coins=100, moon_gems=50, version=0)
        db.add(wallet)
        await db.flush()

    delta = body.amount if body.action == "add" else -body.amount

    if body.currency == "star":
        current_balance = wallet.star_coins
        new_balance = current_balance + delta
        if new_balance < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"扣减失败：当前星元余额 ({current_balance}) 不足扣减 {body.amount}",
            )
        wallet.star_coins = new_balance
    else:
        current_balance = wallet.moon_gems
        new_balance = current_balance + delta
        if new_balance < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"扣减失败：当前月华余额 ({current_balance}) 不足扣减 {body.amount}",
            )
        wallet.moon_gems = new_balance

    wallet.version += 1

    # 写入金融级审计流水
    tx = WalletTransaction(
        user_id=user_id,
        type="admin_adjust",
        currency=body.currency,
        amount=delta,
        balance_after=new_balance,
        description=f"[管理员调账] 操作人: {current_admin.username}, 理由: {body.reason}",
    )
    db.add(tx)
    await db.commit()

    logger.info(
        f"[Admin Finance] 管理员 {current_admin.username} 为用户 {user_id} 调账: "
        f"{body.currency} {delta:+d}, 变动后余额: {new_balance}, 原因: {body.reason}"
    )

    return {
        "code": 200,
        "message": "调账成功",
        "data": {
            "user_id": str(user_id),
            "currency": body.currency,
            "delta": delta,
            "balance_after": new_balance,
        },
    }
