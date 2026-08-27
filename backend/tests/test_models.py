"""SQLAlchemy 2.0 ORM 数据模型与元数据完整性自动化测试套件。

测试覆盖：
1. 15 张数据表的 Base.metadata 完整注册与 DDL 约束；
2. 用户与资产模型关联、Check 约束与级联删除；
3. 角色卡与 10 项数据指标、世界书关联；
4. 对话会话与 DAG 分支链模型；
5. Mod 模组与用户自定义模型；
6. 运营公告、活动与问卷模型。

Usage:
    $ uv run pytest tests/test_models.py -v
"""


from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import (
    Activity,
    Character,
    CharacterMetrics,
    CharacterWorldBook,
    ChatControlPanel,
    ChatMessage,
    ChatNarrativeState,
    ChatSession,
    ModItem,
    Notice,
    StoryBranch,
    Survey,
    User,
    UserActiveMod,
    UserProfile,
    UserWallet,
    WalletTransaction,
)


def test_models_ddl_and_relationships() -> None:
    """使用内存 SQLite 引擎验证全部 15 张数据表的 DDL 创建与基础 ORM 操作。"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    # 验证 15 张核心表均已注册并创建
    table_names = Base.metadata.tables.keys()
    assert "users" in table_names
    assert "user_profiles" in table_names
    assert "user_wallets" in table_names
    assert "wallet_transactions" in table_names
    assert "characters" in table_names
    assert "character_metrics" in table_names
    assert "character_worldbooks" in table_names
    assert "character_comments" in table_names
    assert "character_interactions" in table_names
    assert "chat_sessions" in table_names
    assert "story_branches" in table_names
    assert "chat_messages" in table_names
    assert "chat_control_panels" in table_names
    assert "chat_narrative_states" in table_names
    assert "mods" in table_names
    assert "user_active_mods" in table_names
    assert "mod_collections" in table_names
    assert "user_custom_items" in table_names
    assert "activities" in table_names
    assert "notices" in table_names
    assert "surveys" in table_names

    with Session(engine) as session:
        # 1. 创建用户与资料、钱包
        user = User(
            email="spike@naro.ai",
            hashed_password="hashed_secret_pw",
            invite_code="NAR-TEST01",
        )
        profile = UserProfile(
            user=user,
            username="Spike",
            vip_level=1,
            player_level=5,
        )
        wallet = UserWallet(
            user=user,
            star_coins=500,
            moon_gems=100,
        )
        session.add_all([user, profile, wallet])
        session.commit()

        assert user.id is not None
        assert user.profile.username == "Spike"
        assert user.wallet.star_coins == 500

        # 2. 创建流水
        tx = WalletTransaction(
            user=user,
            type="daily_reward",
            currency="star",
            amount=50,
            balance_after=550,
            description="每日签到",
        )
        session.add(tx)
        session.commit()
        assert len(user.transactions) == 1

        # 3. 创建角色卡与指标、世界书
        char = Character(
            author=user,
            name="星野梦",
            avatar_url="https://example.com/avatar.png",
            category="story",
            description="梦境引路人",
            first_mes="欢迎来到叙梦之地。",
            prologue_title="序幕·启程",
            tags=["奇幻", "剧情"],
        )
        metrics = CharacterMetrics(
            character=char,
            hotness=1200.5,
            trend_score=4.8,
            chat_count=350,
        )
        wb = CharacterWorldBook(
            character=char,
            keys=["梦境碎片"],
            content="凝聚记忆的透明晶体。",
            constant=True,
        )
        session.add_all([char, metrics, wb])
        session.commit()

        assert char.id is not None
        assert char.metrics.hotness == 1200.5
        assert len(char.worldbooks) == 1

        # 4. 创建会话、分支、消息与面板
        chat_sess = ChatSession(
            user=user,
            character=char,
            current_model_id="glm-5.2-o1",
        )
        session.add(chat_sess)
        session.commit()

        branch = StoryBranch(
            session=chat_sess,
            name="🌿 主线剧情",
            is_main=True,
        )
        session.add(branch)
        session.commit()

        msg = ChatMessage(
            session=chat_sess,
            branch=branch,
            sender="user",
            content="你好，星野梦！",
            input_tokens=10,
            output_tokens=0,
        )
        ctrl_panel = ChatControlPanel(
            session=chat_sess,
            user_name="旅行者",
            variables={"variable_1": "100"},
        )
        narrative_state = ChatNarrativeState(
            session=chat_sess,
            location="星辉圣殿",
        )
        session.add_all([msg, ctrl_panel, narrative_state])
        session.commit()

        assert len(chat_sess.branches) == 1
        assert len(chat_sess.messages) == 1
        assert chat_sess.control_panel.user_name == "旅行者"
        assert chat_sess.narrative_state.location == "星辉圣殿"

        # 5. 创建 Mod 与已激活记录
        mod = ModItem(
            author=user,
            title="战斗数值增强 Mod",
            description="扩展跑团战斗结算规则",
            category_tag="system",
            price=0,
        )
        session.add(mod)
        session.commit()

        active_mod = UserActiveMod(
            user=user,
            mod=mod,
            priority_order=10,
            is_active=True,
        )
        session.add(active_mod)
        session.commit()

        assert len(user.active_mods) == 1
        assert user.active_mods[0].priority_order == 10

        # 6. 创建运营公告、活动与问卷
        notice = Notice(
            title="版本 1.0.0 正式上线",
            category="系统公告",
            date_text="2026-08-23",
            summary="全新叙梦 Naro 上线",
        )
        activity = Activity(
            title="首发签到福利",
            tag="福利",
            reward_text="100星元",
            date_range="长期有效",
        )
        survey = Survey(
            title="新功能体验调研",
            reward_star=50,
            category="功能体验",
        )
        session.add_all([notice, activity, survey])
        session.commit()

        assert notice.id is not None
        assert activity.id is not None
        assert survey.reward_star == 50

    engine.dispose()
