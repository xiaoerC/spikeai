"""001 初始化全量数据表结构

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-23 23:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("invite_code", sa.String(32), nullable=False),
        sa.Column("invited_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_users_email", "users", ["email"], unique=True)
    op.create_index("idx_users_invite_code", "users", ["invite_code"], unique=True)

    # 2. user_profiles
    op.create_table(
        "user_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("avatar_url", sa.Text(), server_default="", nullable=False),
        sa.Column("vip_level", sa.Integer(), server_default="0", nullable=False),
        sa.Column("player_level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("player_xp", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("creator_level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("creator_xp", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("badges", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 3. user_wallets
    op.create_table(
        "user_wallets",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("star_coins", sa.Integer(), server_default="100", nullable=False),
        sa.Column("moon_gems", sa.Integer(), server_default="50", nullable=False),
        sa.Column("version", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("star_coins >= 0", name="chk_user_wallets_star_coins_non_negative"),
        sa.CheckConstraint("moon_gems >= 0", name="chk_user_wallets_moon_gems_non_negative"),
    )

    # 4. wallet_transactions
    op.create_table(
        "wallet_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("currency", sa.String(16), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("model_id", sa.String(64), nullable=True),
        sa.Column("target_character_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_wallet_tx_user_created", "wallet_transactions", ["user_id", "created_at"])

    # 5. characters
    op.create_table(
        "characters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=False),
        sa.Column("banner_url", sa.Text(), nullable=True),
        sa.Column("category", sa.String(32), server_default="story", nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("personality", sa.Text(), server_default="", nullable=False),
        sa.Column("scenario", sa.Text(), server_default="", nullable=False),
        sa.Column("first_mes", sa.Text(), nullable=False),
        sa.Column("alternate_greetings", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("system_prompt", sa.Text(), server_default="", nullable=False),
        sa.Column("post_history_instructions", sa.Text(), server_default="", nullable=False),
        sa.Column("prologue_title", sa.String(128), server_default="序幕", nullable=False),
        sa.Column("prologue_html", sa.Text(), server_default="", nullable=False),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("status", sa.String(32), server_default="published", nullable=False),
        sa.Column("settings_word_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("version", sa.String(32), server_default="1.0.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_characters_category_status", "characters", ["category", "status"])

    # 6. character_metrics
    op.create_table(
        "character_metrics",
        sa.Column("character_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("hotness", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("trend_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("chat_count", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("like_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("favorite_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("import_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rating", sa.Float(), server_default="5.0", nullable=False),
        sa.Column("rating_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_tokens", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_character_metrics_hotness", "character_metrics", ["hotness"])
    op.create_index("idx_character_metrics_trend", "character_metrics", ["trend_score"])

    # 7. character_worldbooks
    op.create_table(
        "character_worldbooks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("keys", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("constant", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("position", sa.String(32), server_default="after_char", nullable=False),
        sa.Column("embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_worldbooks_char", "character_worldbooks", ["character_id"])

    # 8. character_comments
    op.create_table(
        "character_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("likes", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 9. character_interactions
    op.create_table(
        "character_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_liked", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_favorited", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("user_rating", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_char_user_interact", "character_interactions", ["character_id", "user_id"], unique=True)

    # 10. chat_sessions
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("current_branch_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("current_model_id", sa.String(64), server_default="glm-5.2-o1", nullable=False),
        sa.Column("mode", sa.String(32), server_default="story", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_chat_sessions_user", "chat_sessions", ["user_id", "updated_at"])

    # 11. story_branches
    op.create_table(
        "story_branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("parent_branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("story_branches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("fork_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_main", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_story_branches_session", "story_branches", ["session_id"])

    # 12. chat_messages
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("story_branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender", sa.String(16), nullable=False),
        sa.Column("character_name", sa.String(128), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("thinking_content", sa.Text(), server_default="", nullable=False),
        sa.Column("input_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.Column("output_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.Column("parent_message_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_chat_messages_session_branch", "chat_messages", ["session_id", "branch_id", "created_at"])

    # 13. chat_control_panels
    op.create_table(
        "chat_control_panels",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_name", sa.String(64), server_default="{{user}}", nullable=False),
        sa.Column("user_persona", sa.Text(), server_default="", nullable=False),
        sa.Column("custom_prompt", sa.Text(), server_default="", nullable=False),
        sa.Column("variables", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("memory_blocks", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("text_replacements", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 14. chat_narrative_states
    op.create_table(
        "chat_narrative_states",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("date_text", sa.String(64), server_default="", nullable=False),
        sa.Column("time_text", sa.String(32), server_default="", nullable=False),
        sa.Column("location", sa.String(128), server_default="", nullable=False),
        sa.Column("present_characters", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("player_states", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("consumables", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("important_items", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("social_relations", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("tasks", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("history_events", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 15. mods
    op.create_table(
        "mods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category_tag", sa.String(32), nullable=False),
        sa.Column("price", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(32), server_default="published", nullable=False),
        sa.Column("entries", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("downloads", sa.Integer(), server_default="0", nullable=False),
        sa.Column("likes", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rating", sa.Float(), server_default="5.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_mods_category_status", "mods", ["category_tag", "status"])

    # 16. user_active_mods
    op.create_table(
        "user_active_mods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mod_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mods.id", ondelete="CASCADE"), nullable=False),
        sa.Column("priority_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "mod_id", name="uq_user_mod"),
    )
    op.create_index("idx_user_active_mods_order", "user_active_mods", ["user_id", "priority_order"])

    # 17. mod_collections
    op.create_table(
        "mod_collections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("cover_url", sa.Text(), nullable=True),
        sa.Column("mod_ids", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 18. user_custom_items
    op.create_table(
        "user_custom_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_user_custom_type", "user_custom_items", ["user_id", "type"])

    # 19. activities
    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("tag", sa.String(32), nullable=False),
        sa.Column("reward_text", sa.String(64), nullable=False),
        sa.Column("date_range", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), server_default="active", nullable=False),
        sa.Column("rules", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 20. notices
    op.create_table(
        "notices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("date_text", sa.String(32), nullable=False),
        sa.Column("badge_type", sa.String(32), server_default="notice", nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("content_html", sa.Text(), server_default="", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 21. surveys
    op.create_table(
        "surveys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("reward_star", sa.Integer(), server_default="50", nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("duration_text", sa.String(32), server_default="约3分钟", nullable=False),
        sa.Column("status", sa.String(32), server_default="active", nullable=False),
        sa.Column("questions", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("surveys")
    op.drop_table("notices")
    op.drop_table("activities")
    op.drop_table("user_custom_items")
    op.drop_table("mod_collections")
    op.drop_table("user_active_mods")
    op.drop_table("mods")
    op.drop_table("chat_narrative_states")
    op.drop_table("chat_control_panels")
    op.drop_table("chat_messages")
    op.drop_table("story_branches")
    op.drop_table("chat_sessions")
    op.drop_table("character_interactions")
    op.drop_table("character_comments")
    op.drop_table("character_worldbooks")
    op.drop_table("character_metrics")
    op.drop_table("characters")
    op.drop_table("wallet_transactions")
    op.drop_table("user_wallets")
    op.drop_table("user_profiles")
    op.drop_table("users")
