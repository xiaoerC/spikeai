"""钱包资金与资产结算领域服务 (CSO 金融级安全规范)。

严格采用 PostgreSQL 行级排他锁 (with_for_update) 与原子事务，
实现高并发下的零穿透扣费、每日签到领星元、创作者打赏与审计流水。

Usage:
    >>> from app.services.wallet_service import WalletService
    >>> tx = await WalletService.deduct_balance(db, user_id, "star", 30, model_id="glm-5.2-o1")
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserProfile, UserWallet, WalletTransaction
from app.schemas.common import PaginatedResponse
from app.schemas.user import DailyRewardResponse, WalletTransactionResponse

logger = logging.getLogger(__name__)


class WalletService:
    """金融级钱包资金管理与结算服务。"""

    @classmethod
    async def deduct_balance(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        currency: Literal["star", "moon"],
        amount: int,
        model_id: str | None = None,
        target_character_id: uuid.UUID | None = None,
        description: str = "",
    ) -> WalletTransaction:
        """悲观行级锁并发安全扣费。

        Args:
            db: 异步数据库会话。
            user_id: 扣费用户 ID。
            currency: 扣除币种 ("star" 为星元，"moon" 为月华)。
            amount: 扣除数值 (必须为正整数)。
            model_id: 消耗模型 ID。
            target_character_id: 目标角色卡 ID。
            description: 流水描述。

        Returns:
            WalletTransaction: 生成的审计流水记录。

        Raises:
            HTTPException: 余额不足或钱包不存在时抛出 400 错误。
        """
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="扣费金额必须大于 0",
            )

        # 1. 使用 with_for_update() 行级排他锁，防止并发穿透
        stmt = select(UserWallet).where(UserWallet.user_id == user_id).with_for_update()
        result = await db.execute(stmt)
        wallet = result.scalar_one_or_none()

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户钱包账户不存在",
            )

        current_balance = wallet.star_coins if currency == "star" else wallet.moon_gems
        currency_name = "星元 ★" if currency == "star" else "月华 🌙"

        if current_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{currency_name}余额不足 (当前: {current_balance}, 所需: {amount})，请前往个人中心充值",
            )

        # 2. 执行扣减与版本递增
        if currency == "star":
            wallet.star_coins -= amount
            balance_after = wallet.star_coins
        else:
            wallet.moon_gems -= amount
            balance_after = wallet.moon_gems

        wallet.version += 1

        # 3. 记录扣费流水
        tx_type = f"chat_{currency}" if model_id else "consume"
        desc = description or f"使用 {model_id or '模型'} 对话消耗 {amount} {currency_name}"

        tx = WalletTransaction(
            user_id=user_id,
            type=tx_type,
            currency=currency,
            amount=-amount,
            balance_after=balance_after,
            model_id=model_id,
            target_character_id=target_character_id,
            description=desc,
        )
        db.add(tx)

        # 4. 同步累加玩家经验值 (1 星元 = 1 经验, 1 月华 = 10 经验)
        profile_stmt = select(UserProfile).where(UserProfile.user_id == user_id).with_for_update()
        profile = (await db.execute(profile_stmt)).scalar_one_or_none()
        if profile:
            xp_gain = amount if currency == "star" else amount * 10
            profile.player_xp += xp_gain
            # 每 500 经验升级一次
            calculated_level = max(1, int(profile.player_xp // 500) + 1)
            profile.player_level = max(profile.player_level, calculated_level)

        await db.flush()
        return tx

    @classmethod
    async def add_balance(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        currency: Literal["star", "moon"],
        amount: int,
        tx_type: str = "recharge",
        description: str = "",
    ) -> WalletTransaction:
        """悲观行级锁充值或系统赠送入账。

        Args:
            db: 异步数据库会话。
            user_id: 入账用户 ID。
            currency: 入账币种。
            amount: 增加数值 (必须为正整数)。
            tx_type: 流水类型 (recharge / daily_reward / creator_share / admin_grant)。
            description: 说明。

        Returns:
            WalletTransaction: 流水记录。
        """
        if amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="入账金额必须大于 0")

        stmt = select(UserWallet).where(UserWallet.user_id == user_id).with_for_update()
        wallet = (await db.execute(stmt)).scalar_one_or_none()
        if not wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户钱包账户不存在")

        if currency == "star":
            wallet.star_coins += amount
            balance_after = wallet.star_coins
        else:
            wallet.moon_gems += amount
            balance_after = wallet.moon_gems

        wallet.version += 1

        tx = WalletTransaction(
            user_id=user_id,
            type=tx_type,
            currency=currency,
            amount=amount,
            balance_after=balance_after,
            description=description or f"充值/奖励获得 {amount} {'星元' if currency == 'star' else '月华'}",
        )
        db.add(tx)
        await db.flush()
        return tx

    @classmethod
    async def claim_daily_reward(cls, db: AsyncSession, user_id: uuid.UUID) -> DailyRewardResponse:
        """每日签到领取星元奖励 (防重复签到与经验累加)。

        Args:
            db: 异步数据库会话。
            user_id: 签到用户 ID。

        Returns:
            DailyRewardResponse: 签到成功响应体。

        Raises:
            HTTPException: 今日已签到时抛出。
        """
        now = datetime.now(UTC)
        today_start = datetime(now.year, now.month, now.day, tzinfo=UTC)

        # 1. 检查今日是否已存在 daily_reward 记录
        check_stmt = (
            select(WalletTransaction)
            .where(
                WalletTransaction.user_id == user_id,
                WalletTransaction.type == "daily_reward",
                WalletTransaction.created_at >= today_start,
            )
            .limit(1)
        )
        existing_checkin = (await db.execute(check_stmt)).scalar_one_or_none()
        if existing_checkin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您今日已完成签到，明天再来吧！",
            )

        # 2. 赠送 50 星元并记录
        reward_amount = 50
        tx = await cls.add_balance(
            db=db,
            user_id=user_id,
            currency="star",
            amount=reward_amount,
            tx_type="daily_reward",
            description="每日签到奖励 (+50 星元)",
        )

        # 3. 增加玩家经验
        profile_stmt = select(UserProfile).where(UserProfile.user_id == user_id).with_for_update()
        profile = (await db.execute(profile_stmt)).scalar_one_or_none()
        if profile:
            profile.player_xp += 50

        await db.commit()

        return DailyRewardResponse(
            reward_star_coins=reward_amount,
            new_balance=tx.balance_after,
            consecutive_days=1,
            message="每日签到成功，已获得 50 星元 ★",
        )

    @classmethod
    async def reward_creator(
        cls,
        db: AsyncSession,
        sender_id: uuid.UUID,
        recipient_id: uuid.UUID,
        currency: Literal["star", "moon"],
        amount: int,
        target_character_id: uuid.UUID | None = None,
    ) -> tuple[WalletTransaction, WalletTransaction]:
        """打赏创作者原子结算事务 (平台 10% 服务费，创作者 90% 入账)。

        Args:
            db: 异步数据库会话。
            sender_id: 打赏者 UID。
            recipient_id: 创作者 UID。
            currency: 打赏币种。
            amount: 打赏数额。
            target_character_id: 目标角色卡 ID。

        Returns:
            tuple[WalletTransaction, WalletTransaction]: (打赏者支出流水, 创作者收入流水)。
        """
        if sender_id == recipient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能打赏给自己哦",
            )

        # 1. 扣除打赏者金额 (已带 with_for_update)
        sender_tx = await cls.deduct_balance(
            db=db,
            user_id=sender_id,
            currency=currency,
            amount=amount,
            target_character_id=target_character_id,
            description=f"打赏创作者角色卡 ({amount} {'星元' if currency == 'star' else '月华'})",
        )

        # 2. 计算 90% 创作者分成 (平台抽成 10%)
        creator_amount = max(1, int(amount * 0.9))
        recipient_tx = await cls.add_balance(
            db=db,
            user_id=recipient_id,
            currency=currency,
            amount=creator_amount,
            tx_type="creator_share",
            description=f"收到玩家打赏分成 (+{creator_amount} {'星元' if currency == 'star' else '月华'})",
        )

        # 3. 增加创作者经验
        creator_profile_stmt = (
            select(UserProfile).where(UserProfile.user_id == recipient_id).with_for_update()
        )
        creator_profile = (await db.execute(creator_profile_stmt)).scalar_one_or_none()
        if creator_profile:
            creator_profile.creator_xp += creator_amount
            creator_level = max(1, int(creator_profile.creator_xp // 200) + 1)
            creator_profile.creator_level = creator_level

        await db.commit()
        return sender_tx, recipient_tx

    @classmethod
    async def get_wallet_transactions(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[WalletTransactionResponse]:
        """分页获取用户资产变动流水明细。"""
        # 总数统计
        count_stmt = select(func.count(WalletTransaction.id)).where(
            WalletTransaction.user_id == user_id
        )
        total = (await db.execute(count_stmt)).scalar_one() or 0

        # 分页查询
        offset = (page - 1) * page_size
        stmt = (
            select(WalletTransaction)
            .where(WalletTransaction.user_id == user_id)
            .order_by(WalletTransaction.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        records = (await db.execute(stmt)).scalars().all()

        dtos = [WalletTransactionResponse.model_validate(rec) for rec in records]
        total_pages = max(1, (total + page_size - 1) // page_size)

        return PaginatedResponse[WalletTransactionResponse](
            items=dtos,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
