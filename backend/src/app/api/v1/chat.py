"""AI 对话、剧情流式交互与历史会话管理路由控制层。

提供 SSE 流式消息生成、历史会话检索、置顶/备注/删除管理、会话与消息历史检索、分支切换与主控面板读写接口。

Usage:
    GET  /api/v1/chat/sessions
    GET  /api/v1/chat/sessions/by-character/{character_id}
    GET  /api/v1/chat/sessions/{id}
    POST /api/v1/chat/sessions/{id}/stream
    POST /api/v1/chat/sessions/{id}/stop
    PUT  /api/v1/chat/sessions/{id}/pin
    PUT  /api/v1/chat/sessions/{id}/remark
    DELETE /api/v1/chat/sessions/{id}
    POST /api/v1/chat/sessions/{id}/clear
"""

import logging
import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatMessageDTO,
    ChatSessionListItemDTO,
    ChatSessionResponse,
    SendMessageRequest,
    UpdateRemarkRequest,
)
from app.schemas.common import ApiResponse
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["AI 对话与剧情树 (Chat & Story DAG)"])


@router.get(
    "/sessions",
    response_model=ApiResponse[list[ChatSessionListItemDTO]],
    summary="获取当前登录用户的所有历史聊天会话列表",
    description="按置顶与最近活跃时间倒序返回，包含角色卡封面、最后一条消息与消息数。",
)
async def list_user_chat_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[list[ChatSessionListItemDTO]]:
    """获取当前用户历史会话。"""
    sessions = await ChatService.get_user_chat_sessions(db=db, user_id=user.id)
    return ApiResponse(code=0, message="success", data=sessions)


@router.get(
    "/sessions/by-character/{character_id}",
    response_model=ApiResponse[ChatSessionResponse],
    summary="获取或初始化与角色的对话会话",
    description="若当前用户与该角色无活跃会话，则自动创建并返回包含开场白、分支树与主控面板的会话信息。",
)
async def get_or_create_character_session(
    character_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ChatSessionResponse]:
    """获取/初始化会话。"""
    session = await ChatService.get_or_create_session(
        db=db,
        user_id=user.id,
        character_id=character_id,
    )
    dto = await ChatService.get_session_response(db=db, session=session)
    return ApiResponse(code=0, message="success", data=dto)


@router.get(
    "/sessions/{session_id}",
    response_model=ApiResponse[ChatSessionResponse],
    summary="获取指定会话完整详情",
)
async def get_session_detail(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ChatSessionResponse]:
    """获取指定会话详情。"""
    session = await ChatService.get_session_by_id(
        db=db,
        user_id=user.id,
        session_id=session_id,
    )
    dto = await ChatService.get_session_response(db=db, session=session)
    return ApiResponse(code=0, message="success", data=dto)


@router.post(
    "/sessions/{session_id}/stream",
    summary="SSE 流式生成 AI 对话回复",
    description="标准 text/event-stream 协议，实时下发 thinking、message、usage、error、done 事件流。",
)
async def stream_chat_message(
    session_id: uuid.UUID,
    payload: SendMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> StreamingResponse:
    """SSE 流式消息生成网关。"""
    return StreamingResponse(
        ChatService.send_message_stream(
            db=db,
            user_id=user.id,
            session_id=session_id,
            payload=payload,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/sessions/{session_id}/stop",
    response_model=ApiResponse[dict[str, str]],
    summary="中止当前流式生成",
)
async def stop_generation(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
) -> ApiResponse[dict[str, str]]:
    """主动中断流式生成。"""
    logger.info("User %s requested to stop generation for session %s", user.id, session_id)
    return ApiResponse(
        code=0,
        message="success",
        data={"status": "stopped", "session_id": str(session_id)},
    )


@router.put(
    "/sessions/{session_id}/pin",
    response_model=ApiResponse[dict[str, bool]],
    summary="切换会话置顶状态",
)
async def toggle_pin_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict[str, bool]]:
    """置顶或取消置顶指定会话。"""
    is_pinned = await ChatService.toggle_pin_session(db=db, user_id=user.id, session_id=session_id)
    return ApiResponse(code=0, message="success", data={"is_pinned": is_pinned})


@router.put(
    "/sessions/{session_id}/remark",
    response_model=ApiResponse[dict[str, str]],
    summary="更新会话用户备注",
)
async def update_session_remark(
    session_id: uuid.UUID,
    payload: UpdateRemarkRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict[str, str]]:
    """更新用户备注。"""
    new_remark = await ChatService.update_session_remark(
        db=db,
        user_id=user.id,
        session_id=session_id,
        remark=payload.remark,
    )
    return ApiResponse(code=0, message="success", data={"remark": new_remark})


@router.delete(
    "/sessions/{session_id}",
    response_model=ApiResponse[dict[str, bool]],
    summary="删除指定会话",
)
async def delete_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict[str, bool]]:
    """删除会话及其历史数据。"""
    await ChatService.delete_session(db=db, user_id=user.id, session_id=session_id)
    return ApiResponse(code=0, message="success", data={"deleted": True})


@router.post(
    "/sessions/{session_id}/clear",
    response_model=ApiResponse[dict[str, bool]],
    summary="清空会话历史消息",
)
async def clear_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict[str, bool]]:
    """清空会话所有历史消息并重置为初始开场白。"""
    await ChatService.clear_session_messages(db=db, user_id=user.id, session_id=session_id)
    return ApiResponse(code=0, message="success", data={"cleared": True})
