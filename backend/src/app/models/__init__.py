"""SQLAlchemy 2.0 ORM 数据模型聚合包。

导出所有领域数据模型，确保 Base.metadata 完整注册全部 15 张表。

Usage:
    >>> from app.models import User, Character, ChatSession, ModItem, Notice
"""

from app.models.character import (
    Character,
    CharacterComment,
    CharacterInteraction,
    CharacterMetrics,
    CharacterWorldBook,
)
from app.models.chat import (
    ChatControlPanel,
    ChatMessage,
    ChatNarrativeState,
    ChatSession,
    StoryBranch,
)
from app.models.mod import (
    ModCollection,
    ModItem,
    UserActiveMod,
    UserCustomItem,
)
from app.models.ops import (
    Activity,
    Notice,
    Survey,
)
from app.models.user import (
    User,
    UserProfile,
    UserWallet,
    WalletTransaction,
)

__all__ = [
    # Ops
    "Activity",
    # Character
    "Character",
    "CharacterComment",
    "CharacterInteraction",
    "CharacterMetrics",
    "CharacterWorldBook",
    # Chat
    "ChatControlPanel",
    "ChatMessage",
    "ChatNarrativeState",
    "ChatSession",
    # Mod
    "ModCollection",
    "ModItem",
    "Notice",
    "StoryBranch",
    "Survey",
    # User
    "User",
    "UserActiveMod",
    "UserCustomItem",
    "UserProfile",
    "UserWallet",
    "WalletTransaction",
]
