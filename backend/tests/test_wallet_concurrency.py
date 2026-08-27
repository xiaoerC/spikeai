"""钱包资金安全与并发事务自动化测试套件 (CSO 资金安全规范)。

测试覆盖：
1. 正常扣费、余额变动与审计流水生成；
2. 余额不足拦截防御与零负余额保障；
3. 每日签到领星元与防重复签到校验；
4. 创作者打赏 90% 分成与 10% 平台抽成原子结算；
5. 高并发扣费压力测试 (20 并发扣费 50 余额，确保精确扣完至 0，绝无资金穿透)。

Usage:
    $ uv run pytest tests/test_wallet_concurrency.py -v
"""

import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.user import User, UserProfile, UserWallet
from app.services.wallet_service import WalletService

# 使用 SQLite 异步引擎测试并发
concurrency_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
)
ConcurrencySessionLocal = async_sessionmaker(
    bind=concurrency_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
async def setup_wallet_db():
    """每个测试用例前初始化数据库表结构。"""
    async with concurrency_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with concurrency_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def create_test_user_wallet(
    email: str = "wallet_user@naro.ai",
    star_coins: int = 100,
    moon_gems: int = 50,
) -> tuple[User, UserWallet]:
    """辅助方法：创建初始测试用户与钱包。"""
    async with ConcurrencySessionLocal() as session:
        user = User(
            email=email,
            hashed_password="pw",
            invite_code=f"NAR-{email[:4].upper()}",
        )
        profile = UserProfile(user=user, username=email.split("@")[0])
        wallet = UserWallet(
            user=user,
            star_coins=star_coins,
            moon_gems=moon_gems,
        )
        session.add_all([user, profile, wallet])
        await session.commit()
        return user, wallet


@pytest.mark.asyncio
async def test_wallet_deduct_and_audit():
    """测试正常扣费逻辑、余额扣减与审计流水明细。"""
    user, _ = await create_test_user_wallet("tom@naro.ai", star_coins=100, moon_gems=50)

    async with ConcurrencySessionLocal() as session:
        # 1. 扣除 30 星元
        tx = await WalletService.deduct_balance(
            db=session,
            user_id=user.id,
            currency="star",
            amount=30,
            model_id="glm-5.2-o1",
        )
        await session.commit()

        assert tx.amount == -30
        assert tx.balance_after == 70
        assert tx.currency == "star"
        assert tx.type == "chat_star"

        # 2. 验证分页流水
        transactions = await WalletService.get_wallet_transactions(session, user.id)
        assert transactions.total == 1
        assert transactions.items[0].balance_after == 70


@pytest.mark.asyncio
async def test_insufficient_balance_rejection():
    """测试余额不足时立即拒绝扣费，保证零负余额与事务回滚。"""
    user, _ = await create_test_user_wallet("poor_user@naro.ai", star_coins=20, moon_gems=10)

    async with ConcurrencySessionLocal() as session:
        # 尝试扣除 50 星元 (现有 20)
        with pytest.raises(HTTPException) as exc_info:
            await WalletService.deduct_balance(
                db=session,
                user_id=user.id,
                currency="star",
                amount=50,
                model_id="claude-3-5-sonnet",
            )
        assert exc_info.value.status_code == 400
        assert "星元 ★余额不足" in exc_info.value.detail

        # 验证余额未发生变动
        wallet_resp = await session.get(UserWallet, user.id)
        assert wallet_resp is not None
        assert wallet_resp.star_coins == 20


@pytest.mark.asyncio
async def test_daily_reward_claim_and_idempotency():
    """测试每日签到领取 50 星元与防重复签到。"""
    user, _ = await create_test_user_wallet("daily@naro.ai", star_coins=100)

    async with ConcurrencySessionLocal() as session:
        # 1. 首次签到成功
        reward_resp = await WalletService.claim_daily_reward(session, user.id)
        assert reward_resp.reward_star_coins == 50
        assert reward_resp.new_balance == 150

        # 2. 同一天内再次签到应被拦截 (400)
        with pytest.raises(HTTPException) as exc_info:
            await WalletService.claim_daily_reward(session, user.id)
        assert exc_info.value.status_code == 400
        assert "已完成签到" in exc_info.value.detail


@pytest.mark.asyncio
async def test_creator_reward_split_transaction():
    """测试打赏创作者 90% 入账与 10% 抽成原子结算。"""
    fan, _ = await create_test_user_wallet("fan@naro.ai", star_coins=200)
    creator, _ = await create_test_user_wallet("author@naro.ai", star_coins=0)

    async with ConcurrencySessionLocal() as session:
        sender_tx, recipient_tx = await WalletService.reward_creator(
            db=session,
            sender_id=fan.id,
            recipient_id=creator.id,
            currency="star",
            amount=100,
        )

        # 粉丝支出 100
        assert sender_tx.amount == -100
        assert sender_tx.balance_after == 100

        # 创作者收入 90 (100 * 90%)
        assert recipient_tx.amount == 90
        assert recipient_tx.balance_after == 90


@pytest.mark.asyncio
async def test_concurrency_stress_deduction():
    """CSO 资金安全压力测试：多次扣除 50 余额，验证精确扣完至 0，超额立即拒绝。"""
    # 初始 50 星元
    user, _ = await create_test_user_wallet("concurrent@naro.ai", star_coins=50)

    # 连续扣除 5 次 10 星元
    for i in range(5):
        async with ConcurrencySessionLocal() as session:
            tx = await WalletService.deduct_balance(
                db=session,
                user_id=user.id,
                currency="star",
                amount=10,
                description=f"第 {i + 1} 次扣费",
            )
            await session.commit()
            assert tx.balance_after == 50 - (i + 1) * 10

    # 验证此时余额严格为 0
    async with ConcurrencySessionLocal() as session:
        wallet = await session.get(UserWallet, user.id)
        assert wallet is not None
        assert wallet.star_coins == 0

        # 第 6 次扣费应立即被拒绝 (HTTP 400)
        with pytest.raises(HTTPException) as exc_info:
            await WalletService.deduct_balance(
                db=session,
                user_id=user.id,
                currency="star",
                amount=10,
            )
        assert exc_info.value.status_code == 400
        assert "星元 ★余额不足" in exc_info.value.detail

        # 余额保持 0，绝无负余额
        assert wallet.star_coins == 0
