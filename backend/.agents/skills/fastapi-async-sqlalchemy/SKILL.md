---
name: fastapi-async-sqlalchemy
description: FastAPI + SQLAlchemy 2.0 Async + asyncpg + Pydantic v2 后端工程化开发规范。仅限在 backend/ 目录下编写 Python 异步路由、ORM 模型与数据库事务时调用。
license: MIT
file_patterns:
  - "backend/**/*.py"
  - "backend/alembic/**/*"
triggers:
  - "FastAPI endpoint"
  - "SQLAlchemy 2.0 async"
  - "Database migration"
  - "Row locking"
---

# FastAPI + SQLAlchemy 2.0 异步高并发后端开发规范

本项目后端严格基于 Python 3.12、`uv` 虚拟环境、FastAPI 与 SQLAlchemy 2.0 Async 架构。编写或修改后端代码必须遵循本规范。

---

## 一、 异步 ORM 建模与声明式规范 (DeclarativeBase)

### 1. 强类型模型声明
必须使用 SQLAlchemy 2.0 的 `Mapped` 与 `mapped_column` 强类型语法：
```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """所有 ORM 模型的基类"""

    pass


class Wallet(Base):
    """用户钱包模型 (双币资产)"""

    __tablename__ = "wallets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    star_coins: Mapped[int] = mapped_column(BigInteger, default=0, comment="星元★ (付费货币)")
    moon_essence: Mapped[int] = mapped_column(
        BigInteger, default=0, comment="月华🌙 (免费/活动货币)"
    )
    version: Mapped[int] = mapped_column(default=1, comment="乐观锁版本号")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 关联关系
    user: Mapped["User"] = relationship(back_populates="wallet")
```

---

## 二、 异步事务与防并发死锁（行级锁）

涉及双币扣费、充值流水或 DAG 节点剪枝时，必须显式开启悲观行级锁 `with_for_update`，防止并发扣费产生负数余额：

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def deduct_wallet_balance(
    session: AsyncSession, user_id: UUID, star_amount: int, moon_amount: int
) -> Wallet:
    """扣除用户钱包余额 (带行级悲观锁)

    Args:
        session: 异步数据库 Session
        user_id: 用户唯一标识
        star_amount: 扣除的星元数量
        moon_amount: 扣除的月华数量

    Returns:
        扣费成功后的 Wallet ORM 实例

    Raises:
        ValueError: 余额不足时抛出
    """
    stmt = (
        select(Wallet)
        .where(Wallet.user_id == user_id)
        .with_for_update()  # 👈 锁定当前行，防止并发脏写
    )
    result = await session.execute(stmt)
    wallet = result.scalar_one_or_none()

    if not wallet:
        raise ValueError("钱包账户不存在")

    if wallet.star_coins < star_amount or wallet.moon_essence < moon_amount:
        raise ValueError(f"余额不足: 需星元 {star_amount}, 月华 {moon_amount}")

    wallet.star_coins -= star_amount
    wallet.moon_essence -= moon_amount

    # 无需显式 commit，由外层 Session 上下文管理器统一提交
    return wallet
```

---

## 三、 防止 N+1 查询与异步加载

严禁在异步代码中使用隐式懒加载（Lazy Loading，在 async 下会抛出 `MissingGreenlet` 异常）。必须显式使用 `selectinload` 或 `joinedload`：

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload


async def get_character_with_dialogues(session: AsyncSession, character_id: UUID) -> Character:
    stmt = (
        select(Character)
        .where(Character.id == character_id)
        .options(selectinload(Character.worldbook_entries), selectinload(Character.greetings))
    )
    result = await session.execute(stmt)
    return result.scalar_one()
```

---

## 四、 统一异常防御规范

所有路由必须通过全局异常处理器或标准 HTTPException 抛出：
```python
from fastapi import HTTPException, status


class InsufficientBalanceException(HTTPException):
    def __init__(self, message: str = "账户余额不足"):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"code": "INSUFFICIENT_BALANCE", "message": message},
        )
```
