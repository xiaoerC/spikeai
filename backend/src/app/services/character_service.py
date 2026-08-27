"""角色卡领域业务逻辑服务层 (Character & Market Service)。

负责角色多维复合检索、10 项数据指标聚合、世界书关联、用户互动（点赞/收藏/评论/打分）及初始内置角色种子数据注入。

Usage:
    >>> from app.services.character_service import CharacterService
    >>> chars = await CharacterService.list_characters(db, params)
"""

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, cast, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from app.core.cache import local_cache
from app.core.exceptions import (
    AppException,
    EntityNotFoundError,
    PermissionDeniedError,
)
from app.core.redis import get_redis_client
from app.models.character import (
    Character,
    CharacterComment,
    CharacterInteraction,
    CharacterMetrics,
    CharacterWorldBook,
)
from app.models.user import User, UserProfile
from app.schemas.character import (
    CharacterAuthorDTO,
    CharacterCommentResponse,
    CharacterCreateRequest,
    CharacterDetailResponse,
    CharacterFilterParams,
    CharacterListItemResponse,
    CharacterMetricsDTO,
    CharacterUpdateRequest,
    WorldBookEntryDTO,
)
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)


class CharacterService:
    """角色卡核心领域服务。"""

    @classmethod
    async def list_characters(
        cls, db: AsyncSession, params: CharacterFilterParams
    ) -> PaginatedResponse[CharacterListItemResponse]:
        """多维条件分页查询角色市场列表（高性能 joinedload + Redis 缓存层）。"""
        # 1. 优先从内存 local_cache 读取 (微秒级响应)
        cache_key = f"market:characters:{params.mode}:{params.sort}:{params.tag or 'all'}:{params.keyword or 'none'}:{params.page}:{params.page_size}"
        cached_local = local_cache.get(cache_key)
        if cached_local is not None:
            return cached_local

        # 尝试从 Redis 读取二级缓存
        try:
            redis = get_redis_client()
            cached_data = await redis.get(cache_key)
            if cached_data:
                res_obj = PaginatedResponse[CharacterListItemResponse].model_validate_json(cached_data)
                local_cache.set(cache_key, res_obj, ttl=30)
                return res_obj
        except Exception as e:
            logger.debug("Redis 读取缓存跳过: %s", e)

        # 2. 构建主查询与条件过滤
        stmt = (
            select(Character)
            .outerjoin(Character.metrics)
            .options(
                contains_eager(Character.metrics),
                joinedload(Character.author).joinedload(User.profile),
            )
            .where(Character.status == "published")
        )

        # 分类模式过滤
        if params.mode == "nsfw":
            stmt = stmt.where(Character.category == "nsfw")
        else:
            stmt = stmt.where(Character.category != "nsfw")

        # 标签过滤
        if params.tag and params.tag != "全部":
            tag_clean = params.tag.strip()
            tag_json_escaped = json.dumps(tag_clean)[1:-1]
            tag_filter = or_(
                Character.tags.cast(Text).ilike(f"%{tag_clean}%"),
                Character.tags.cast(Text).ilike(f"%{tag_json_escaped}%"),
            )
            stmt = stmt.where(tag_filter)

        # 关键词模糊搜索
        if params.keyword and params.keyword.strip():
            kw = f"%{params.keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    Character.name.ilike(kw),
                    Character.description.ilike(kw),
                )
            )

        # 排序
        if params.sort == "heat":
            stmt = stmt.order_by(desc(CharacterMetrics.hotness), desc(Character.created_at))
        elif params.sort == "trend":
            stmt = stmt.order_by(desc(CharacterMetrics.trend_score), desc(Character.created_at))
        elif params.sort == "recommend":
            stmt = stmt.order_by(desc(CharacterMetrics.rating), desc(CharacterMetrics.like_count))
        elif params.sort == "favorite":
            stmt = stmt.order_by(desc(CharacterMetrics.favorite_count))
        else:
            stmt = stmt.order_by(desc(Character.created_at))

        # 统计总数
        count_stmt = select(func.count(Character.id)).where(Character.status == "published")
        if params.mode == "nsfw":
            count_stmt = count_stmt.where(Character.category == "nsfw")
        else:
            count_stmt = count_stmt.where(Character.category != "nsfw")
        if params.tag and params.tag != "全部":
            tag_clean = params.tag.strip()
            tag_json_escaped = json.dumps(tag_clean)[1:-1]
            count_stmt = count_stmt.where(
                or_(
                    Character.tags.cast(Text).ilike(f"%{tag_clean}%"),
                    Character.tags.cast(Text).ilike(f"%{tag_json_escaped}%"),
                )
            )
        if params.keyword and params.keyword.strip():
            kw = f"%{params.keyword.strip()}%"
            count_stmt = count_stmt.where(
                or_(
                    Character.name.ilike(kw),
                    Character.description.ilike(kw),
                )
            )

        # 分页执行 (单次网络 IO 取回全部关联模型)
        offset = (params.page - 1) * params.page_size
        stmt = stmt.offset(offset).limit(params.page_size)

        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one() or 0

        # 若当前列表为空且无搜索过滤条件，执行一次种子注入兜底
        if total == 0 and not params.tag and not params.keyword:
            await cls.ensure_seed_characters(db)
            total_res = await db.execute(count_stmt)
            total = total_res.scalar_one() or 0
            result = await db.execute(stmt)
            characters = list(result.unique().scalars().all())
        else:
            result = await db.execute(stmt)
            characters = list(result.unique().scalars().all())

        items: list[CharacterListItemResponse] = []
        for char in characters:
            metrics_dto = CharacterMetricsDTO.model_validate(char.metrics) if char.metrics else CharacterMetricsDTO()
            p = char.author.profile if char.author and char.author.profile else None
            author_dto = CharacterAuthorDTO(
                id=char.author.id,
                username=p.username if p else "叙梦创作者",
                avatar_url=(p.avatar_url if p and p.avatar_url else f"https://api.dicebear.com/7.x/bottts/svg?seed={char.author.id}"),
                creator_level=p.creator_level if p else 1,
                followers_count=12,
                is_following=False,
            )
            items.append(
                CharacterListItemResponse(
                    id=char.id,
                    name=char.name,
                    avatar_url=char.avatar_url,
                    banner_url=char.banner_url,
                    category=char.category,
                    description=char.description,
                    tags=char.tags,
                    author=author_dto,
                    metrics=metrics_dto,
                    created_at=char.created_at,
                )
            )

        total_pages = max(1, (total + params.page_size - 1) // params.page_size)
        response_obj = PaginatedResponse(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )

        local_cache.set(cache_key, response_obj, ttl=30)
        try:
            redis = get_redis_client()
            await redis.set(cache_key, response_obj.model_dump_json(), ex=30)
        except Exception:
            pass

        return response_obj

    @classmethod
    async def get_character_detail(
        cls, db: AsyncSession, character_id: uuid.UUID, current_user_id: uuid.UUID | None = None
    ) -> CharacterDetailResponse:
        """获取角色卡 100% 完整详情（高性能 joinedload，减少远程网络往返）。"""
        stmt = (
            select(Character)
            .options(
                joinedload(Character.author).joinedload(User.profile),
                joinedload(Character.metrics),
                selectinload(Character.worldbooks),
            )
            .where(Character.id == character_id)
        )
        result = await db.execute(stmt)
        char = result.unique().scalar_one_or_none()
        if not char:
            raise EntityNotFoundError("角色卡", character_id)

        metrics_dto = CharacterMetricsDTO.model_validate(char.metrics) if char.metrics else CharacterMetricsDTO()
        p = char.author.profile if char.author and char.author.profile else None
        author_dto = CharacterAuthorDTO(
            id=char.author.id,
            username=p.username if p else "叙梦创作者",
            avatar_url=(p.avatar_url if p and p.avatar_url else f"https://api.dicebear.com/7.x/bottts/svg?seed={char.author.id}"),
            creator_level=p.creator_level if p else 1,
            followers_count=12,
            is_following=False,
        )

        worldbooks_dto = [
            WorldBookEntryDTO(
                id=wb.id,
                keys=wb.keys,
                content=wb.content,
                constant=wb.constant,
                position=wb.position,
            )
            for wb in char.worldbooks
        ]

        is_liked = False
        is_favorited = False
        user_rating = None

        if current_user_id:
            interact_stmt = select(CharacterInteraction).where(
                CharacterInteraction.character_id == character_id,
                CharacterInteraction.user_id == current_user_id,
            )
            interaction = (await db.execute(interact_stmt)).scalar_one_or_none()
            if interaction:
                is_liked = interaction.is_liked
                is_favorited = interaction.is_favorited
                user_rating = interaction.user_rating

        return CharacterDetailResponse(
            id=char.id,
            name=char.name,
            avatar_url=char.avatar_url,
            banner_url=char.banner_url,
            category=char.category,
            description=char.description,
            personality=char.personality,
            scenario=char.scenario,
            first_mes=char.first_mes,
            alternate_greetings=char.alternate_greetings,
            system_prompt=char.system_prompt,
            post_history_instructions=char.post_history_instructions,
            prologue_title=char.prologue_title,
            prologue_html=char.prologue_html,
            creator_notes=getattr(char, "creator_notes", "") or "",
            tags=char.tags,
            status=char.status,
            settings_word_count=char.settings_word_count or len(char.description) + len(char.personality) + len(char.scenario),
            version=char.version,
            created_at=char.created_at,
            author=author_dto,
            metrics=metrics_dto,
            worldbooks=worldbooks_dto,
            is_liked=is_liked,
            is_favorited=is_favorited,
            user_rating=user_rating,
        )

    @classmethod
    async def create_character(
        cls, db: AsyncSession, user_id: uuid.UUID, req: CharacterCreateRequest
    ) -> CharacterDetailResponse:
        """创建并上架新的原创角色卡。"""
        char_id = uuid.uuid4()
        word_count = (
            len(req.description)
            + len(req.personality)
            + len(req.scenario)
            + len(req.first_mes)
            + len(req.creator_notes)
            + sum(len(w.content) for w in req.worldbooks)
        )

        char = Character(
            id=char_id,
            author_id=user_id,
            name=req.name,
            avatar_url=req.avatar_url,
            banner_url=req.banner_url,
            category=req.category,
            description=req.description,
            personality=req.personality,
            scenario=req.scenario,
            first_mes=req.first_mes,
            alternate_greetings=req.alternate_greetings,
            system_prompt=req.system_prompt,
            post_history_instructions=req.post_history_instructions,
            prologue_title=req.prologue_title,
            prologue_html=req.prologue_html,
            creator_notes=req.creator_notes,
            tags=req.tags,
            status=req.status,
            settings_word_count=word_count,
            version="1.0.0",
        )
        db.add(char)

        # 初始数据指标
        metrics = CharacterMetrics(
            character_id=char_id,
            hotness=10.0,
            trend_score=1.0,
            chat_count=0,
            like_count=0,
            favorite_count=0,
            import_count=0,
            rating=5.0,
            rating_count=0,
            total_tokens=0,
        )
        db.add(metrics)

        # 世界书条目
        for wb in req.worldbooks:
            worldbook_record = CharacterWorldBook(
                character_id=char_id,
                keys=wb.keys,
                content=wb.content,
                constant=wb.constant,
                position=wb.position,
            )
            db.add(worldbook_record)

        await db.commit()
        await cls._clear_market_cache()
        return await cls.get_character_detail(db, char_id, current_user_id=user_id)

    @classmethod
    async def _clear_market_cache(cls) -> None:
        """清理角色市场内存与 Redis 列表缓存。"""
        local_cache.clear_prefix("market:characters:")
        local_cache.clear_prefix("character:detail:")
        try:
            redis = get_redis_client()
            keys = await redis.keys("market:characters:*")
            if keys:
                await redis.delete(*keys)
        except Exception:
            pass

    @classmethod
    async def prewarm_market_cache(cls, db: AsyncSession) -> None:
        """服务启动时预热常用市场页面缓存，确保所有用户访问均为毫秒级响应。"""
        try:
            preset_queries = [
                CharacterFilterParams(mode="story", sort="heat", page=1, page_size=20),
                CharacterFilterParams(mode="story", sort="heat", page=1, page_size=30),
                CharacterFilterParams(mode="story", sort="trend", page=1, page_size=20),
                CharacterFilterParams(mode="story", sort="trend", page=1, page_size=30),
                CharacterFilterParams(mode="story", sort="recommend", page=1, page_size=20),
                CharacterFilterParams(mode="story", sort="recommend", page=1, page_size=30),
                CharacterFilterParams(mode="nsfw", sort="heat", page=1, page_size=20),
                CharacterFilterParams(mode="nsfw", sort="heat", page=1, page_size=30),
            ]
            for p in preset_queries:
                await cls.list_characters(db=db, params=p)
        except Exception as e:
            logger.warning("市场列表缓存预热跳过: %s", e)

    @classmethod
    async def list_my_characters(
        cls, db: AsyncSession, user_id: uuid.UUID, category: str | None = None
    ) -> list[CharacterDetailResponse]:
        """查询当前用户创建/上传的所有角色卡列表（包含草稿与已上架）。"""
        stmt = (
            select(Character)
            .options(
                joinedload(Character.author).joinedload(User.profile),
                joinedload(Character.metrics),
                selectinload(Character.worldbooks),
            )
            .where(Character.author_id == user_id)
            .order_by(desc(Character.created_at))
        )
        if category and category != "all":
            if category == "nsfw":
                stmt = stmt.where(Character.category == "nsfw")
            elif category == "story":
                stmt = stmt.where(Character.category != "nsfw")

        result = await db.execute(stmt)
        characters = list(result.unique().scalars().all())

        items: list[CharacterDetailResponse] = []
        for char in characters:
            metrics_dto = CharacterMetricsDTO.model_validate(char.metrics) if char.metrics else CharacterMetricsDTO()
            p = char.author.profile if char.author and char.author.profile else None
            author_dto = CharacterAuthorDTO(
                id=char.author.id,
                username=p.username if p else "叙梦创作者",
                avatar_url=(p.avatar_url if p and p.avatar_url else f"https://api.dicebear.com/7.x/bottts/svg?seed={char.author.id}"),
                creator_level=p.creator_level if p else 1,
                followers_count=12,
                is_following=False,
            )
            worldbooks_dto = [
                WorldBookEntryDTO(
                    id=wb.id,
                    keys=wb.keys,
                    content=wb.content,
                    constant=wb.constant,
                    position=wb.position,
                )
                for wb in char.worldbooks
            ]
            items.append(
                CharacterDetailResponse(
                    id=char.id,
                    name=char.name,
                    avatar_url=char.avatar_url,
                    banner_url=char.banner_url,
                    category=char.category,
                    description=char.description,
                    personality=char.personality,
                    scenario=char.scenario,
                    first_mes=char.first_mes,
                    alternate_greetings=char.alternate_greetings,
                    system_prompt=char.system_prompt,
                    post_history_instructions=char.post_history_instructions,
                    prologue_title=char.prologue_title,
                    prologue_html=char.prologue_html,
                    creator_notes=getattr(char, "creator_notes", "") or "",
                    tags=char.tags,
                    status=char.status,
                    settings_word_count=char.settings_word_count or len(char.description) + len(char.personality) + len(char.scenario),
                    version=char.version,
                    created_at=char.created_at,
                    author=author_dto,
                    metrics=metrics_dto,
                    worldbooks=worldbooks_dto,
                    is_liked=False,
                    is_favorited=False,
                    user_rating=None,
                )
            )
        return items

    @classmethod
    async def update_character_status(
        cls, db: AsyncSession, user_id: uuid.UUID, character_id: uuid.UUID, status_val: str
    ) -> CharacterDetailResponse:
        """更新角色卡发布状态（上架 / 下架 / 草稿）。"""
        stmt = select(Character).where(Character.id == character_id)
        char = (await db.execute(stmt)).scalar_one_or_none()
        if not char:
            raise EntityNotFoundError("角色卡", character_id)
        if char.author_id != user_id:
            raise PermissionDeniedError("无权操作此角色卡")

        char.status = status_val
        await db.commit()
        await cls._clear_market_cache()
        return await cls.get_character_detail(db, character_id, current_user_id=user_id)

    @classmethod
    async def delete_character(
        cls, db: AsyncSession, user_id: uuid.UUID, character_id: uuid.UUID
    ) -> bool:
        """删除角色卡及其全部关联记录。"""
        stmt = select(Character).where(Character.id == character_id)
        char = (await db.execute(stmt)).scalar_one_or_none()
        if not char:
            raise EntityNotFoundError("角色卡", character_id)
        if char.author_id != user_id:
            raise PermissionDeniedError("无权删除此角色卡")

        await db.delete(char)
        await db.commit()
        await cls._clear_market_cache()
        return True

    @classmethod
    async def update_character(
        cls, db: AsyncSession, user_id: uuid.UUID, character_id: uuid.UUID, req: CharacterCreateRequest
    ) -> CharacterDetailResponse:
        """更新角色卡全量字段及世界书条目。"""
        stmt = (
            select(Character)
            .options(selectinload(Character.worldbooks))
            .where(Character.id == character_id)
        )
        char = (await db.execute(stmt)).scalar_one_or_none()
        if not char:
            raise EntityNotFoundError("角色卡", character_id)
        if char.author_id != user_id:
            raise PermissionDeniedError("无权修改此角色卡")

        word_count = (
            len(req.description)
            + len(req.personality)
            + len(req.scenario)
            + len(req.first_mes)
            + len(req.creator_notes)
            + sum(len(w.content) for w in req.worldbooks)
        )

        char.name = req.name
        char.avatar_url = req.avatar_url
        char.banner_url = req.banner_url
        char.category = req.category
        char.description = req.description
        char.personality = req.personality
        char.scenario = req.scenario
        char.first_mes = req.first_mes
        char.alternate_greetings = req.alternate_greetings
        char.system_prompt = req.system_prompt
        char.post_history_instructions = req.post_history_instructions
        char.prologue_title = req.prologue_title
        char.prologue_html = req.prologue_html
        char.creator_notes = req.creator_notes
        char.tags = req.tags
        char.status = req.status
        char.settings_word_count = word_count

        # 更新世界书条目：删除旧条目并写入新条目
        for wb in list(char.worldbooks):
            await db.delete(wb)

        for wb in req.worldbooks:
            worldbook_record = CharacterWorldBook(
                character_id=character_id,
                keys=wb.keys,
                content=wb.content,
                constant=wb.constant,
                position=wb.position,
            )
            db.add(worldbook_record)

        await db.commit()
        await cls._clear_market_cache()
        return await cls.get_character_detail(db, character_id, current_user_id=user_id)

    @classmethod
    async def toggle_like(
        cls, db: AsyncSession, character_id: uuid.UUID, user_id: uuid.UUID
    ) -> dict[str, bool | int]:
        """点赞/取消点赞角色卡。"""
        stmt = select(CharacterInteraction).where(
            CharacterInteraction.character_id == character_id,
            CharacterInteraction.user_id == user_id,
        )
        interaction = (await db.execute(stmt)).scalar_one_or_none()

        metrics_stmt = select(CharacterMetrics).where(CharacterMetrics.character_id == character_id)
        metrics = (await db.execute(metrics_stmt)).scalar_one_or_none()

        if not interaction:
            interaction = CharacterInteraction(
                character_id=character_id,
                user_id=user_id,
                is_liked=True,
            )
            db.add(interaction)
            if metrics:
                metrics.like_count += 1
                metrics.hotness += 5.0
            is_liked = True
        else:
            interaction.is_liked = not interaction.is_liked
            is_liked = interaction.is_liked
            if metrics:
                if is_liked:
                    metrics.like_count += 1
                    metrics.hotness += 5.0
                else:
                    metrics.like_count = max(0, metrics.like_count - 1)
                    metrics.hotness = max(0.0, metrics.hotness - 5.0)

        await db.commit()
        return {"is_liked": is_liked, "like_count": metrics.like_count if metrics else 0}

    @classmethod
    async def add_comment(
        cls, db: AsyncSession, character_id: uuid.UUID, user_id: uuid.UUID, content: str
    ) -> CharacterCommentResponse:
        """发表角色评论。"""
        user_stmt = (
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == user_id)
        )
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        if not user:
            raise AppException(message="用户不存在", code=40402)

        comment = CharacterComment(
            character_id=character_id,
            user_id=user_id,
            content=content,
            likes=0,
        )
        db.add(comment)

        # 增加角色热度
        metrics_stmt = select(CharacterMetrics).where(CharacterMetrics.character_id == character_id)
        metrics = (await db.execute(metrics_stmt)).scalar_one_or_none()
        if metrics:
            metrics.hotness += 3.0

        await db.commit()
        await db.refresh(comment)

        p = user.profile
        username = p.username if p else "旅人"
        avatar_url = p.avatar_url if p and p.avatar_url else f"https://api.dicebear.com/7.x/bottts/svg?seed={user.id}"

        return CharacterCommentResponse(
            id=comment.id,
            character_id=character_id,
            user_id=user_id,
            username=username,
            avatar_url=avatar_url,
            content=comment.content,
            likes=comment.likes,
            created_at=comment.created_at,
        )

    @classmethod
    async def list_comments(
        cls, db: AsyncSession, character_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[CharacterCommentResponse]:
        """获取角色评论列表。"""
        cache_key = f"char_comments:{character_id}:{page}:{page_size}"
        cached = local_cache.get(cache_key)
        if cached:
            return cached

        count_stmt = select(func.count(CharacterComment.id)).where(CharacterComment.character_id == character_id)
        total = (await db.execute(count_stmt)).scalar_one() or 0

        offset = (page - 1) * page_size
        stmt = (
            select(CharacterComment)
            .options(joinedload(CharacterComment.user).joinedload(User.profile))
            .where(CharacterComment.character_id == character_id)
            .order_by(desc(CharacterComment.created_at))
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        comments = list(result.unique().scalars().all())

        items = []
        for c in comments:
            p = c.user.profile if c.user and c.user.profile else None
            username = p.username if p else "匿名旅人"
            avatar_url = p.avatar_url if p and p.avatar_url else f"https://api.dicebear.com/7.x/bottts/svg?seed={c.user_id}"
            items.append(
                CharacterCommentResponse(
                    id=c.id,
                    character_id=c.character_id,
                    user_id=c.user_id,
                    username=username,
                    avatar_url=avatar_url,
                    content=c.content,
                    likes=c.likes,
                    created_at=c.created_at,
                )
            )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        resp = PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
        local_cache.set(cache_key, resp, ttl=30)
        return resp

    @classmethod
    async def ensure_seed_characters(cls, db: AsyncSession) -> None:
        """数据库空时自动种子化注入 4 位高质感黑金角色卡（带完整立绘、10项指标与世界书）。"""
        check_stmt = select(func.count(Character.id))
        count = (await db.execute(check_stmt)).scalar_one() or 0
        if count > 0:
            return

        # 获取或创建默认系统创作者用户
        admin_stmt = select(User).where(User.email == "official@naro.ai")
        author = (await db.execute(admin_stmt)).scalar_one_or_none()
        if not author:
            author_id = uuid.uuid4()
            author = User(
                id=author_id,
                email="official@naro.ai",
                hashed_password="seeded_password_hash",
                invite_code="NAR-OFFICIAL",
            )
            db.add(author)
            profile = UserProfile(
                user_id=author_id,
                username="叙梦官方馆长",
                avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=official",
                creator_level=10,
            )
            db.add(profile)
            await db.commit()
            await db.refresh(author)

        seed_data = [
            {
                "name": "Dolce Notte · 梦境守护者",
                "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&auto=format&fit=crop&q=80",
                "banner_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1200&auto=format&fit=crop&q=80",
                "category": "story",
                "tags": ["梦境", "治愈", "魔法", "奇幻"],
                "description": "漫步在黑曜星河之畔的梦境领路人。她手持金色提灯，能看穿旅人内心最深处的欲望与记忆碎片。",
                "personality": "优雅、温和、富有同理心，但在面对梦魇入侵时展现出绝对的决断力与星光魔力。",
                "scenario": "叙梦世界中央梦境浮岛『星穹之舟』的午夜会客厅，窗外是缓缓流淌的星河瀑布。",
                "first_mes": "欢迎来到 Dolce Notte，远道而来的旅人。今晚你想与我分享哪一段尚未落下的梦境呢？",
                "prologue_title": "序幕 · 星辰坠落之夜",
                "prologue_html": "<div class='naro-prologue'><h1>Dolce Notte</h1><p>当最后一道星辉隐没在黑曜石阶梯尽头，她悄然点亮了手中的琉璃提灯……</p></div>",
                "hotness": 98.6,
                "trend_score": 5.41,
                "chat_count": 12850,
                "like_count": 3420,
                "rating": 4.95,
                "worldbooks": [
                    {
                        "keys": ["提灯", "琉璃提灯", "星火"],
                        "content": "【琉璃提灯】：由初代梦境筑造师以陨星核心打造，能驱散四级以下的所有潜意识梦魇，并在持有者周围展开直径三米的绝对清醒领域。",
                        "constant": True,
                        "position": "after_char",
                    },
                    {
                        "keys": ["星穹之舟", "浮岛"],
                        "content": "【星穹之舟】：悬浮于叙梦中枢上空的古代遗迹，唯有持有星元印记的旅人方可登船。",
                        "constant": False,
                        "position": "after_char",
                    },
                ],
            },
            {
                "name": "夜巡警姬 · 蕾娅",
                "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500&auto=format&fit=crop&q=80",
                "banner_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1200&auto=format&fit=crop&q=80",
                "category": "story",
                "tags": ["赛博朋克", "机娘", "警探", "动作"],
                "description": "新东京第七治安区的机械执行官，装备高频粒子光刃与战术义体，性格外冷内热。",
                "personality": "恪尽职守、沉着冷静、言简意赅，对违法分子绝不留情。",
                "scenario": "雨夜中闪烁着全息霓虹广告的新东京高架桥下，警用飞行器的红蓝警灯在积水中闪烁。",
                "first_mes": "公民，停下你的动作。根据治安法典第 104 条，请出示你的神经义体序列号。",
                "prologue_title": "序幕 · 霓虹雨夜",
                "prologue_html": "<div class='naro-prologue'><h1>Cyber Patrol</h1><p>酸雨打在机械护甲上滋滋作响，她的机械眼泛起冰冷的淡蓝光芒……</p></div>",
                "hotness": 88.2,
                "trend_score": 4.12,
                "chat_count": 8920,
                "like_count": 2150,
                "rating": 4.88,
                "worldbooks": [
                    {
                        "keys": ["神经义体", "义体"],
                        "content": "【神经义体】：2099年普及的脑机接口增强设备，所有公民均需在第七治安区进行合法认证注册。",
                        "constant": False,
                        "position": "after_char",
                    }
                ],
            },
            {
                "name": "落霞剑宗 · 苏清漪",
                "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500&auto=format&fit=crop&q=80",
                "banner_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1200&auto=format&fit=crop&q=80",
                "category": "story",
                "tags": ["修仙", "剑修", "高岭之花", "古风"],
                "description": "落霞宗首席大师姐，执掌灵剑『霜华』，天生冰灵根，剑道造诣冠绝同辈。",
                "personality": "清冷孤傲、不善言辞，却在师弟师妹遇险时毫不犹豫拔剑相护。",
                "scenario": "落霞峰顶问剑坪，云海翻涌，万丈晚霞染红了千年寒铁铸造的试剑台。",
                "first_mes": "师弟，今日晨课你迟了半柱香。拔剑吧，让我看看你的落霞十三式练得如何了。",
                "prologue_title": "序幕 · 问剑云海",
                "prologue_html": "<div class='naro-prologue'><h1>霜华映落霞</h1><p>风吹动白衣胜雪的裙摆，长剑出鞘，清越龙吟回荡九峰之上……</p></div>",
                "hotness": 92.4,
                "trend_score": 4.88,
                "chat_count": 10450,
                "like_count": 2890,
                "rating": 4.92,
                "worldbooks": [
                    {
                        "keys": ["霜华", "灵剑"],
                        "content": "【灵剑·霜华】：落霞宗开山老祖取九幽玄冰与天外陨铁合炼而成，剑气所及之处万物皆凝玄冰。",
                        "constant": True,
                        "position": "after_char",
                    }
                ],
            },
            {
                "name": "星际领航员 · 卡尔",
                "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&auto=format&fit=crop&q=80",
                "banner_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&auto=format&fit=crop&q=80",
                "category": "story",
                "tags": ["科幻", "星际", "探索", "幽默"],
                "description": "跃迁舰『漫游者号』的资深领航员，穿梭于未被标记的超空间虫洞之间，收藏着无数异星唱片。",
                "personality": "幽默风趣、玩世不恭，但在跃迁引擎过载的关键时刻从不手抖。",
                "scenario": "漫游者号舰桥驾驶室，全景视窗外是一颗正在坍缩的超新星爆发出的瑰丽光环。",
                "first_mes": "嘿，系好安全带！前面就是猎户座悬臂未探索区，祝我们的反物质引擎今天也别掉链子！",
                "prologue_title": "序幕 · 跃迁倒计时",
                "prologue_html": "<div class='naro-prologue'><h1>Wanderer Beyond</h1><p>“3、2、1，曲率引擎启动！”视窗外的星光拉伸为无限延长的璀璨光束……</p></div>",
                "hotness": 76.5,
                "trend_score": 3.25,
                "chat_count": 5420,
                "like_count": 1340,
                "rating": 4.81,
                "worldbooks": [],
            },
        ]

        for s in seed_data:
            c_id = uuid.uuid4()
            char = Character(
                id=c_id,
                author_id=author.id,
                name=s["name"],
                avatar_url=s["avatar_url"],
                banner_url=s["banner_url"],
                category=s["category"],
                tags=s["tags"],
                description=s["description"],
                personality=s["personality"],
                scenario=s["scenario"],
                first_mes=s["first_mes"],
                prologue_title=s["prologue_title"],
                prologue_html=s["prologue_html"],
                status="published",
                settings_word_count=len(s["description"]) + len(s["personality"]),
                version="1.0.0",
            )
            db.add(char)

            metrics = CharacterMetrics(
                character_id=c_id,
                hotness=s["hotness"],
                trend_score=s["trend_score"],
                chat_count=s["chat_count"],
                like_count=s["like_count"],
                favorite_count=s["like_count"] // 2,
                import_count=s["like_count"] // 3,
                rating=s["rating"],
                rating_count=s["like_count"] // 4,
                total_tokens=s["chat_count"] * 120,
            )
            db.add(metrics)

            for wb in s.get("worldbooks", []):
                worldbook_record = CharacterWorldBook(
                    character_id=c_id,
                    keys=wb["keys"],
                    content=wb["content"],
                    constant=wb["constant"],
                    position=wb["position"],
                )
                db.add(worldbook_record)

        await db.commit()
        logger.info("4 位初始高质感角色卡种子数据已成功初始化！")
