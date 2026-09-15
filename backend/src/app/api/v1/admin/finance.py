"""平台财务中心与充值订单结算专属 API 路由。

提供全站充值订单与对账大盘多维分页检索、宏观指标实时汇总、金融级悲观行级锁退款冲正。
所有接口均受 RequirePermission 声明式权限守卫控制。

Usage:
    GET  /api/v1/admin/finance/orders
    POST /api/v1/admin/finance/orders/{tx_id}/refund
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_async_db
from app.core.security import RequirePermission
from app.models.admin import AdminUser
from app.models.user import User, UserProfile, UserWallet, WalletTransaction
from app.schemas.admin import (
    AdminFinanceSummary,
    AdminOrderPageResult,
    AdminOrderRefundRequest,
    AdminOrderTransactionItem,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/finance", tags=["平台财务与订单结算中心"])


@router.get("/orders", response_model=AdminOrderPageResult, summary="分页查询平台充值订单与全量对账流水")
async def list_admin_orders(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="搜索用户名称/邮箱/流水描述"),
    tx_type: str | None = Query(None, alias="type", description="流水类型 (recharge/admin_adjust/chat_star等)"),
    currency: str | None = Query(None, description="币种类型 (star/moon)"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:finance:view")),
) -> AdminOrderPageResult:
    """多维分页查询平台所有资金流水，预加载用户信息并返回全站财务大盘指标汇总。"""
    query = select(WalletTransaction).options(
        selectinload(WalletTransaction.user).selectinload(User.profile),
    )

    if tx_type:
        query = query.where(WalletTransaction.type == tx_type)
    if currency:
        query = query.where(WalletTransaction.currency == currency)

    if keyword:
        kw = f"%{keyword.strip()}%"
        query = (
            query.outerjoin(WalletTransaction.user)
            .outerjoin(User.profile)
            .where(
                or_(
                    UserProfile.username.ilike(kw),
                    User.email.ilike(kw),
                    WalletTransaction.description.ilike(kw),
                )
            )
        )

    # 1. 计算筛选后的分页条数
    count_stmt = select(func.count(WalletTransaction.id))
    if tx_type:
        count_stmt = count_stmt.where(WalletTransaction.type == tx_type)
    if currency:
        count_stmt = count_stmt.where(WalletTransaction.currency == currency)
    if keyword:
        kw = f"%{keyword.strip()}%"
        count_stmt = (
            count_stmt.outerjoin(WalletTransaction.user)
            .outerjoin(User.profile)
            .where(
                or_(
                    UserProfile.username.ilike(kw),
                    User.email.ilike(kw),
                    WalletTransaction.description.ilike(kw),
                )
            )
        )

    total_count = (await db.execute(count_stmt)).scalar() or 0

    # 2. 执行分页查询
    offset = (page - 1) * size
    stmt = query.order_by(desc(WalletTransaction.created_at)).offset(offset).limit(size)
    transactions = (await db.execute(stmt)).scalars().all()

    # 3. 统计全站财务大盘指标
    star_recharge_stmt = select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(
        WalletTransaction.type == "recharge",
        WalletTransaction.currency == "star",
    )
    moon_recharge_stmt = select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(
        WalletTransaction.type == "recharge",
        WalletTransaction.currency == "moon",
    )
    total_tx_stmt = select(func.count(WalletTransaction.id))

    # 今日流水数
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_tx_stmt = select(func.count(WalletTransaction.id)).where(WalletTransaction.created_at >= today_start)

    total_star = (await db.execute(star_recharge_stmt)).scalar() or 0
    total_moon = (await db.execute(moon_recharge_stmt)).scalar() or 0
    all_total_tx = (await db.execute(total_tx_stmt)).scalar() or 0
    today_tx = (await db.execute(today_tx_stmt)).scalar() or 0

    summary = AdminFinanceSummary(
        total_star_recharged=int(total_star),
        total_moon_recharged=int(total_moon),
        total_transactions_count=int(all_total_tx),
        today_transactions_count=int(today_tx),
    )

    items: list[AdminOrderTransactionItem] = []
    for tx in transactions:
        user = tx.user
        profile = user.profile if user else None

        items.append(
            AdminOrderTransactionItem(
                id=tx.id,
                user_id=tx.user_id,
                user_name=profile.username if profile else (user.email.split("@")[0] if user else "未知用户"),
                user_email=user.email if user else "",
                user_avatar=profile.avatar_url if profile else "",
                type=tx.type,
                currency=tx.currency,
                amount=tx.amount,
                balance_after=tx.balance_after,
                description=tx.description,
                created_at=tx.created_at,
            )
        )

    return AdminOrderPageResult(
        total=total_count,
        page=page,
        size=size,
        list=items,
        summary=summary,
    )


@router.post("/orders/{tx_id}/refund", summary="金融级悲观行级锁退款冲正处置")
async def refund_order_transaction(
    tx_id: uuid.UUID,
    body: AdminOrderRefundRequest,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(RequirePermission("ops:finance:manage")),
) -> dict[str, Any]:
    """对充值订单或异常交易执行退款冲正，悲观加锁扣减已充值余额，防透支防穿透。"""
    orig_tx = await db.get(WalletTransaction, tx_id)
    if not orig_tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="原始交易记录不存在")

    if orig_tx.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅正向入账流水支持发起退款冲正",
        )

    # 悲观行级锁锁定目标用户钱包
    wallet_stmt = select(UserWallet).where(UserWallet.user_id == orig_tx.user_id).with_for_update()
    wallet = (await db.execute(wallet_stmt)).scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户资产钱包不存在")

    refund_amount = orig_tx.amount
    if orig_tx.currency == "star":
        if wallet.star_coins < refund_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"用户星元余额不足 ({wallet.star_coins} < {refund_amount})，无法执行全额退款冲正",
            )
        wallet.star_coins -= refund_amount
        balance_after = wallet.star_coins
    elif orig_tx.currency == "moon":
        if wallet.moon_gems < refund_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"用户月华余额不足 ({wallet.moon_gems} < {refund_amount})，无法执行全额退款冲正",
            )
        wallet.moon_gems -= refund_amount
        balance_after = wallet.moon_gems
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的币种类型")

    wallet.version += 1

    # 写入一条退款冲正流水
    refund_tx = WalletTransaction(
        id=uuid.uuid4(),
        user_id=orig_tx.user_id,
        type="admin_refund",
        currency=orig_tx.currency,
        amount=-refund_amount,
        balance_after=balance_after,
        description=f"管理员 {current_admin.username} 退款冲正原始单据 ({str(orig_tx.id)[:8]}): {body.reason}",
    )
    db.add(refund_tx)
    await db.commit()

    logger.warning(
        f"[Admin Finance Audit] 管理员 {current_admin.username} 成功冲正单据 {tx_id}，"
        f"扣回用户 {orig_tx.user_id} 资产 {refund_amount} {orig_tx.currency}，理由: {body.reason}"
    )

    return {
        "code": 200,
        "message": "退款冲正处置成功",
        "data": {
            "refund_transaction_id": str(refund_tx.id),
            "amount": -refund_amount,
            "currency": orig_tx.currency,
            "balance_after": balance_after,
        },
    }
