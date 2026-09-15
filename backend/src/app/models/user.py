"""用户与资产领域数据模型。

包含用户账户、用户资料、资产钱包（含悲观行级锁版本控制与非负 CHECK 约束）及资金流水明细。

Usage:
    >>> from app.models.user import User, UserProfile, UserWallet, WalletTransaction
    >>> from sqlalchemy import select
    >>> stmt = select(User).where(User.email == "test@example.com")
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.character import Character
    from app.models.chat import ChatSession
    from app.models.mod import ModItem, UserActiveMod


class User(Base):
    """用户核心账户表。"""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="用户全局唯一主键 UUID",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="用户注册邮箱",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt 哈希密码密文",
    )
    invite_code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
        doc="专属邀请码",
    )
    invited_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        doc="邀请人用户 ID",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        doc="用户状态 (active / banned / suspended)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="注册时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="最后更新时间",
    )

    # 关联关系
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    wallet: Mapped["UserWallet"] = relationship(
        "UserWallet",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list["WalletTransaction"]] = relationship(
        "WalletTransaction",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(WalletTransaction.created_at)",
    )
    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    mods: Mapped[list["ModItem"]] = relationship(
        "ModItem",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    active_mods: Mapped[list["UserActiveMod"]] = relationship(
        "UserActiveMod",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserProfile(Base):
    """用户资料与经验等级表。"""

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        doc="关联用户 ID",
    )
    username: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="用户显示昵称",
    )
    is_custom_username: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        doc="是否已由用户显式设置自定义昵称 (首次登录若为 False 需强制填写)",
    )
    avatar_url: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="用户头像 URL",
    )
    vip_level: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="VIP 赞助者等级 (0~5)",
    )
    player_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        doc="玩家等级",
    )
    player_xp: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        doc="玩家累计经验值",
    )
    creator_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        doc="创作者等级",
    )
    creator_xp: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        doc="创作者累计经验值",
    )
    badges: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="已佩戴与解锁的成就勋章列表",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="资料最后更新时间",
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")


class UserWallet(Base):
    """用户资产钱包表。

    支持悲观行级锁事务与版本乐观锁，并设置数据库级别 CHECK 约束防止负余额。
    """

    __tablename__ = "user_wallets"
    __table_args__ = (
        CheckConstraint("star_coins >= 0", name="chk_user_wallets_star_coins_non_negative"),
        CheckConstraint("moon_gems >= 0", name="chk_user_wallets_moon_gems_non_negative"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        doc="关联用户 ID",
    )
    star_coins: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
        doc="星元余额 ★",
    )
    moon_gems: Mapped[int] = mapped_column(
        Integer,
        default=50,
        nullable=False,
        doc="月华余额 🌙",
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="数据版本号，用于乐观并发校验",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="钱包最后变动时间",
    )

    user: Mapped["User"] = relationship("User", back_populates="wallet")


class WalletTransaction(Base):
    """钱包流水明细表 (金融级对账与审计记录)。"""

    __tablename__ = "wallet_transactions"
    __table_args__ = (
        Index("idx_wallet_tx_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="流水全局唯一 UUID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="关联用户 ID",
    )
    type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="流水类型 (recharge / chat_star / chat_moon / daily_reward / mod_buy / creator_share / reward)",
    )
    currency: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        doc="币种类型 (star / moon)",
    )
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="变动数额 (正数为增加，负数为扣减)",
    )
    balance_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="变动后该币种余额",
    )
    model_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="关联扣费模型 ID (若适用)",
    )
    target_character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        doc="关联目标角色卡 ID (若适用)",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="流水详述备注",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="流水产生时间",
    )

    user: Mapped["User"] = relationship("User", back_populates="transactions")
