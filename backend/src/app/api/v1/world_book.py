"""世界书 (World Book) RESTful API 路由模块。

支持世界书及条目的 CRUD、SillyTavern JSON 格式双向导入导出以及条目启停管理。

Usage:
    >>> from fastapi import APIRouter
    >>> router = APIRouter(prefix="/world-books", tags=["WorldBook"])
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.world_book import (
    SillyTavernWorldBookImportDTO,
    WorldBookCreate,
    WorldBookDetailDTO,
    WorldBookDTO,
    WorldBookEntryCreate,
    WorldBookEntryDTO,
    WorldBookEntryUpdate,
    WorldBookUpdate,
)
from app.services.world_book_service import WorldBookService

router = APIRouter(prefix="/world-books", tags=["WorldBook 世界书"])


@router.post(
    "",
    response_model=WorldBookDetailDTO,
    status_code=status.HTTP_201_CREATED,
    summary="创建新世界书",
)
async def create_world_book(
    payload: WorldBookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> WorldBookDetailDTO:
    """创建一本全新的世界书及其初始条目。"""
    return await WorldBookService.create_world_book(db=db, user_id=current_user.id, payload=payload)


@router.get(
    "",
    response_model=list[WorldBookDTO],
    summary="获取世界书列表",
)
async def list_world_books(
    character_id: uuid.UUID | None = Query(None, description="按关联角色筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> list[WorldBookDTO]:
    """获取当前用户所有世界书以及公共世界书列表。"""
    return await WorldBookService.list_world_books(
        db=db, user_id=current_user.id, character_id=character_id
    )


@router.get(
    "/{world_book_id}",
    response_model=WorldBookDetailDTO,
    summary="获取世界书详情及全部条目",
)
async def get_world_book_detail(
    world_book_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> WorldBookDetailDTO:
    """获取指定世界书的详细信息与条目列表。"""
    return await WorldBookService.get_world_book_detail(
        db=db, user_id=current_user.id, world_book_id=world_book_id
    )


@router.put(
    "/{world_book_id}",
    response_model=WorldBookDTO,
    summary="更新世界书元数据",
)
async def update_world_book(
    world_book_id: uuid.UUID,
    payload: WorldBookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> WorldBookDTO:
    """更新世界书的名称、描述、扫描深度及 Token 预算等元数据。"""
    return await WorldBookService.update_world_book(
        db=db, user_id=current_user.id, world_book_id=world_book_id, payload=payload
    )


@router.delete(
    "/{world_book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除世界书",
)
async def delete_world_book(
    world_book_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    """删除指定世界书及其所有条目。"""
    await WorldBookService.delete_world_book(
        db=db, user_id=current_user.id, world_book_id=world_book_id
    )


@router.post(
    "/{world_book_id}/entries",
    response_model=WorldBookEntryDTO,
    status_code=status.HTTP_201_CREATED,
    summary="向世界书添加条目",
)
async def add_entry(
    world_book_id: uuid.UUID,
    payload: WorldBookEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> WorldBookEntryDTO:
    """为指定世界书新增一个关键词设定条目。"""
    return await WorldBookService.add_entry(
        db=db, user_id=current_user.id, world_book_id=world_book_id, payload=payload
    )


@router.put(
    "/entries/{entry_id}",
    response_model=WorldBookEntryDTO,
    summary="更新世界书条目",
)
async def update_entry(
    entry_id: uuid.UUID,
    payload: WorldBookEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> WorldBookEntryDTO:
    """更新条目的关键词、设定文本、常驻开关或优先级。"""
    return await WorldBookService.update_entry(
        db=db, user_id=current_user.id, entry_id=entry_id, payload=payload
    )


@router.delete(
    "/entries/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除世界书条目",
)
async def delete_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    """删除单条世界书条目。"""
    await WorldBookService.delete_entry(
        db=db, user_id=current_user.id, entry_id=entry_id
    )


@router.post(
    "/import-sillytavern",
    response_model=WorldBookDetailDTO,
    status_code=status.HTTP_201_CREATED,
    summary="导入 SillyTavern JSON 世界书",
)
async def import_sillytavern(
    payload: SillyTavernWorldBookImportDTO,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> WorldBookDetailDTO:
    """从 SillyTavern 导出的 JSON 字典一键解析并创建世界书。"""
    return await WorldBookService.import_sillytavern_json(
        db=db, user_id=current_user.id, payload=payload
    )


@router.get(
    "/{world_book_id}/export-sillytavern",
    response_model=dict[str, Any],
    summary="导出为 SillyTavern JSON 格式",
)
async def export_sillytavern(
    world_book_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> dict[str, Any]:
    """导出指定世界书为 100% 兼容 SillyTavern 的 JSON 数据结构。"""
    return await WorldBookService.export_sillytavern_json(
        db=db, user_id=current_user.id, world_book_id=world_book_id
    )
