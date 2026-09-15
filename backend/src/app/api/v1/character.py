"""角色市场、详情指标与用户互动路由控制层。

提供角色市场检索、详情拉取、创建上架、点赞/收藏、评论与打赏分成。

Usage:
    GET  /api/v1/characters
    POST /api/v1/characters
    GET  /api/v1/characters/{id}
    POST /api/v1/characters/{id}/like
    GET  /api/v1/characters/{id}/comments
    POST /api/v1/characters/{id}/comments
    POST /api/v1/characters/{id}/reward
"""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import decode_access_token, get_current_user
from app.models.user import User
from app.schemas.character import (
    CharacterCommentCreateRequest,
    CharacterCommentResponse,
    CharacterCreateRequest,
    CharacterDetailResponse,
    CharacterFilterParams,
    CharacterListItemResponse,
    PrologueGenerateRequest,
    PrologueGenerateResponse,
    RewardRequest,
    CharacterStatusUpdateRequest,
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.character_service import CharacterService
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/characters", tags=["角色市场与详情 (Characters & Market)"])


async def get_optional_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> uuid.UUID | None:
    """提取可选的登录用户 ID (用于公共列表/详情页读取用户个人的点赞与收藏状态)。"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    try:
        return uuid.UUID(user_id_str)
    except ValueError:
        return None


@router.get(
    "/mine",
    response_model=ApiResponse[list[CharacterDetailResponse]],
    summary="查询当前登录用户创建/上传的角色卡列表",
    description="支持按分类 (story / nsfw) 过滤，返回包含草稿与已上架状态的所有角色卡。",
)
async def list_my_characters(
    category: str | None = Query(default=None, description="分类过滤 (story / nsfw / all)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[list[CharacterDetailResponse]]:
    """查询用户自己的角色卡。"""
    items = await CharacterService.list_my_characters(
        db=db, user_id=current_user.id, category=category
    )
    return ApiResponse(code=0, message="success", data=items)


@router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[CharacterListItemResponse]],
    summary="角色市场多维分页列表与搜索",
    description="支持按分类模式 (story/nsfw)、标签、热度/趋势/推荐排序及关键词搜索。",
)
async def list_characters(
    mode: str = Query(default="story", description="分类模式 (story / nsfw)"),
    sort: str = Query(default="heat", description="排序方式 (heat / trend / recommend / favorite)"),
    tag: str | None = Query(default=None, description="标签过滤"),
    keyword: str | None = Query(default=None, description="搜索关键词"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=50, description="每页数量"),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[PaginatedResponse[CharacterListItemResponse]]:
    """查询角色市场列表。"""
    params = CharacterFilterParams(
        mode=mode,  # type: ignore[arg-type]
        sort=sort,  # type: ignore[arg-type]
        tag=tag,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    result = await CharacterService.list_characters(db=db, params=params)
    return ApiResponse(code=0, message="success", data=result)


@router.post(
    "",
    response_model=ApiResponse[CharacterDetailResponse],
    summary="创建并发布原创角色卡",
    description="支持提交角色卡全部元信息、立绘背景、开场白及内嵌世界书条目。",
)
async def create_character(
    payload: CharacterCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[CharacterDetailResponse]:
    """创建角色卡。"""
    detail = await CharacterService.create_character(
        db=db, user_id=current_user.id, req=payload
    )
    return ApiResponse(
        code=0,
        message="角色卡发布成功！",
        show_message=True,
        data=detail,
    )


@router.post(
    "/generate-prologue",
    response_model=ApiResponse[PrologueGenerateResponse],
    summary="AI 智能生成角色序幕 HTML",
    description="基于创作者填写的角色名、设定背景与问候语，调用大模型生成黑金暗黑玻璃拟物风格的序幕 HTML 片段。",
)
async def generate_prologue(
    payload: PrologueGenerateRequest,
) -> ApiResponse[PrologueGenerateResponse]:
    """生成序幕富文本 HTML。"""
    html = await CharacterService.generate_prologue(payload)
    return ApiResponse(
        code=0,
        message="序幕生成成功！",
        data=PrologueGenerateResponse(prologue_html=html),
    )


@router.patch(
    "/{character_id}/status",
    response_model=ApiResponse[CharacterDetailResponse],
    summary="修改角色卡状态 (上架/下架/设为草稿)",
    description="创作者切换角色的发布状态 (published: 上架公开 / draft: 下架私密)。",
)
async def update_character_status(
    character_id: uuid.UUID,
    payload: CharacterStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[CharacterDetailResponse]:
    """更新角色卡状态。"""
    detail = await CharacterService.update_character_status(
        db=db,
        user_id=current_user.id,
        character_id=character_id,
        status_val=payload.status,
    )
    msg = "角色卡已成功上架到社区！" if payload.status == "published" else "角色卡已成功下架（设为草稿）"
    return ApiResponse(
        code=0,
        message=msg,
        show_message=True,
        data=detail,
    )


@router.put(
    "/{character_id}",
    response_model=ApiResponse[CharacterDetailResponse],
    summary="修改/更新角色卡全量设定与世界书",
    description="创作者更新角色卡的信息、设定、问候语及世界书条目。",
)
async def update_character(
    character_id: uuid.UUID,
    payload: CharacterCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[CharacterDetailResponse]:
    """修改更新角色卡。"""
    detail = await CharacterService.update_character(
        db=db,
        user_id=current_user.id,
        character_id=character_id,
        req=payload,
    )
    return ApiResponse(
        code=0,
        message="角色卡信息已成功保存更新！",
        show_message=True,
        data=detail,
    )


@router.delete(
    "/{character_id}",
    response_model=ApiResponse[dict],
    summary="删除角色卡",
    description="创作者永久删除自己创建的角色卡及其关联的世界书与指标数据。",
)
async def delete_character(
    character_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict]:
    """删除角色卡。"""
    await CharacterService.delete_character(
        db=db, user_id=current_user.id, character_id=character_id
    )
    return ApiResponse(
        code=0,
        message="角色卡已成功删除！",
        show_message=True,
        data={"deleted_id": str(character_id)},
    )


@router.get(
    "/{character_id}",
    response_model=ApiResponse[CharacterDetailResponse],
    summary="获取角色卡全量详情与10项指标",
    description="返回立绘、大封面、开场白、创作者信息、10项雷达指标、世界书条目及当前用户的互动状态。",
)
async def get_character_detail(
    character_id: uuid.UUID,
    user_id: uuid.UUID | None = Depends(get_optional_user_id),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[CharacterDetailResponse]:
    """查询角色详情。"""
    detail = await CharacterService.get_character_detail(
        db=db, character_id=character_id, current_user_id=user_id
    )
    return ApiResponse(code=0, message="success", data=detail)


@router.post(
    "/{character_id}/like",
    response_model=ApiResponse[dict],
    summary="点赞 / 取消点赞角色卡",
    description="原子切换当前用户的点赞状态，并实时更新角色卡总点赞数与热度得分。",
)
async def toggle_like(
    character_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict]:
    """切换点赞状态。"""
    res = await CharacterService.toggle_like(
        db=db, character_id=character_id, user_id=current_user.id
    )
    msg = "点赞成功！" if res["is_liked"] else "已取消点赞"
    return ApiResponse(code=0, message=msg, show_message=True, data=res)


@router.get(
    "/{character_id}/comments",
    response_model=ApiResponse[PaginatedResponse[CharacterCommentResponse]],
    summary="获取角色卡评论列表",
    description="分页拉取用户发表的评价与留言明细。",
)
async def list_comments(
    character_id: uuid.UUID,
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=50, description="每页数量"),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[PaginatedResponse[CharacterCommentResponse]]:
    """查询评论列表。"""
    result = await CharacterService.list_comments(
        db=db, character_id=character_id, page=page, page_size=page_size
    )
    return ApiResponse(code=0, message="success", data=result)


@router.post(
    "/{character_id}/comments",
    response_model=ApiResponse[CharacterCommentResponse],
    summary="发表角色评论",
    description="用户对角色卡发表评价，发表后实时落库展示。",
)
async def add_comment(
    character_id: uuid.UUID,
    payload: CharacterCommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[CharacterCommentResponse]:
    """发表新评论。"""
    comment = await CharacterService.add_comment(
        db=db,
        character_id=character_id,
        user_id=current_user.id,
        content=payload.content,
    )
    return ApiResponse(
        code=0,
        message="评论发表成功！",
        show_message=True,
        data=comment,
    )


@router.post(
    "/{character_id}/reward",
    response_model=ApiResponse[dict],
    summary="创作者打赏与收益分成事务",
    description="消耗用户的星元/月华打赏角色，扣除 20% 平台服务费后 80% 结算给创作者，全程 CSO 行锁事务保障。",
)
async def reward_character(
    character_id: uuid.UUID,
    payload: RewardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict]:
    """打赏角色卡。"""
    char_detail = await CharacterService.get_character_detail(db, character_id)
    creator_id = char_detail.author.id

    result = await WalletService.tip_creator_with_split(
        db=db,
        tipper_user_id=current_user.id,
        creator_user_id=creator_id,
        character_id=character_id,
        amount=payload.amount,
        currency=payload.currency,
    )
    return ApiResponse(
        code=0,
        message=f"成功打赏 {payload.amount} {'星元' if payload.currency == 'star' else '月华'}！",
        show_message=True,
        data=result,
    )
