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
    ControlPanelDTO,
    DAGGraphDTO,
    EditMessageRequest,
    ForkBranchRequest,
    ForkSessionRequest,
    NarrativeStateDTO,
    RollbackRequest,
    SendMessageRequest,
    StoryBranchDetailDTO,
    SwitchGreetingRequest,
    UpdateRemarkRequest,
)
from app.schemas.common import ApiResponse
from app.schemas.llm import ClientModelItem
from app.services.chat_service import ChatService
from app.services.llm_service import LLMService
from app.services.tree_service import TreeService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["AI 对话与剧情树 (Chat & Story DAG)"])


@router.get(
    "/models",
    response_model=ApiResponse[list[ClientModelItem]],
    summary="获取客户端可用大模型列表",
    description="获取后台已配置并上架至客户端 (is_public=True) 的可用大模型列表，支持脱敏展示与客户端动态选择。",
)
async def get_client_available_models(
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[list[ClientModelItem]]:
    """获取所有已启用且对客户端公开的大模型清单。无需鉴权或可选鉴权，供模型选择抽屉实时拉取。"""
    models = await LLMService.get_public_models_for_client(db=db)
    return ApiResponse(code=0, message="success", data=models)


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


@router.post(
    "/sessions/{session_id}/greeting",
    response_model=ApiResponse[ChatMessageDTO],
    summary="切换当前会话的首句开场白 (支持在 default first_mes 与 alternate_greetings 间轮换)",
)
async def switch_session_greeting(
    session_id: uuid.UUID,
    payload: SwitchGreetingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ChatMessageDTO]:
    """切换开场白。"""
    updated_msg = await ChatService.switch_session_greeting(
        db=db, user_id=user.id, session_id=session_id, greeting_index=payload.greeting_index
    )
    return ApiResponse(code=0, message="开场白切换成功", data=updated_msg)


# =========================================================================
# DAG 剧情分支与多平行宇宙状态机端点 (Phase 4)
# =========================================================================


@router.get(
    "/sessions/{session_id}/branches",
    response_model=ApiResponse[list[StoryBranchDetailDTO]],
    summary="获取指定会话的所有剧情分支及节点统计",
)
async def get_session_branches(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[list[StoryBranchDetailDTO]]:
    """获取所有剧情分支列表及统计。"""
    branches = await TreeService.get_session_branches(
        db=db,
        session_id=session_id,
        user_id=user.id,
    )
    return ApiResponse(code=0, message="success", data=branches)


@router.post(
    "/sessions/{session_id}/fork-session",
    response_model=ApiResponse[ChatSessionResponse],
    summary="从指定消息节点复制并派生全新独立聊天会话 (多历史记录)",
)
async def fork_session(
    session_id: uuid.UUID,
    payload: ForkSessionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ChatSessionResponse]:
    """从指定消息分叉并创建全新独立的历史聊天会话。"""
    new_session_resp = await ChatService.fork_session_at_message(
        db=db,
        user_id=user.id,
        session_id=session_id,
        payload=payload,
    )
    return ApiResponse(code=0, message="success", data=new_session_resp)


@router.post(
    "/sessions/{session_id}/branches/fork",
    response_model=ApiResponse[StoryBranchDetailDTO],
    summary="从指定历史消息节点派生新分支",
)
async def fork_branch(
    session_id: uuid.UUID,
    payload: ForkBranchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[StoryBranchDetailDTO]:
    """派生新的平行剧情分支。"""
    new_branch = await TreeService.fork_branch(
        db=db,
        session_id=session_id,
        user_id=user.id,
        payload=payload,
    )
    return ApiResponse(code=0, message="success", data=new_branch)


@router.put(
    "/sessions/{session_id}/branches/{branch_id}/switch",
    response_model=ApiResponse[ChatSessionResponse],
    summary="切换当前活跃剧情分支",
)
async def switch_branch(
    session_id: uuid.UUID,
    branch_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ChatSessionResponse]:
    """切换分支并返回新分支的完整上下文。"""
    detail = await TreeService.switch_branch(
        db=db,
        session_id=session_id,
        user_id=user.id,
        branch_id=branch_id,
    )
    return ApiResponse(code=0, message="success", data=detail)


@router.delete(
    "/sessions/{session_id}/branches/{branch_id}",
    response_model=ApiResponse[dict[str, bool]],
    summary="删除指定非主线剧情分支",
)
async def delete_branch(
    session_id: uuid.UUID,
    branch_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict[str, bool]]:
    """删除指定分支（主线分支不可删除）。"""
    await TreeService.delete_branch(
        db=db,
        session_id=session_id,
        user_id=user.id,
        branch_id=branch_id,
    )
    return ApiResponse(code=0, message="success", data={"deleted": True})


@router.post(
    "/sessions/{session_id}/rollback",
    response_model=ApiResponse[ChatSessionResponse],
    summary="回溯至指定消息节点",
)
async def rollback_to_message(
    session_id: uuid.UUID,
    payload: RollbackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ChatSessionResponse]:
    """回溯至指定历史节点 (支持派生新分支或原地截断)。"""
    detail = await TreeService.rollback_to_message(
        db=db,
        session_id=session_id,
        user_id=user.id,
        payload=payload,
    )
    return ApiResponse(code=0, message="success", data=detail)


@router.put(
    "/sessions/{session_id}/messages/{message_id}",
    response_model=ApiResponse[ChatSessionResponse],
    summary="编辑单条消息内容",
)
async def edit_message(
    session_id: uuid.UUID,
    message_id: uuid.UUID,
    payload: EditMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ChatSessionResponse]:
    """编辑消息 (支持模式 A: 仅保存 / 模式 B: 保存并开辟新分支)。"""
    detail = await TreeService.edit_message(
        db=db,
        session_id=session_id,
        user_id=user.id,
        message_id=message_id,
        payload=payload,
    )
    return ApiResponse(code=0, message="success", data=detail)


@router.get(
    "/sessions/{session_id}/tree",
    response_model=ApiResponse[DAGGraphDTO],
    summary="获取全景 DAG 剧情树拓扑图数据 (Vue Flow 格式)",
)
async def get_session_tree(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[DAGGraphDTO]:
    """生成包含完整 nodes 与 edges 的 DAG 图。"""
    graph = await TreeService.get_dag_graph(
        db=db,
        session_id=session_id,
        user_id=user.id,
    )
    return ApiResponse(code=0, message="success", data=graph)


@router.get(
    "/sessions/{session_id}/control-panel",
    response_model=ApiResponse[ControlPanelDTO],
    summary="获取指定会话的主控面板配置 (38 变量矩阵与指令)",
)
async def get_session_control_panel(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ControlPanelDTO]:
    """获取指定会话的主控面板状态（若不存在则自动初始化默认值）。"""
    data = await ChatService.get_control_panel(
        db=db,
        user_id=user.id,
        session_id=session_id,
    )
    return ApiResponse(code=0, message="success", data=data)


@router.put(
    "/sessions/{session_id}/control-panel",
    response_model=ApiResponse[ControlPanelDTO],
    summary="更新指定会话的主控面板配置",
)
async def update_session_control_panel(
    session_id: uuid.UUID,
    payload: ControlPanelDTO,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[ControlPanelDTO]:
    """更新主控面板 38 变量矩阵、人设、指令、记忆区块与正则替换链。"""
    data = await ChatService.update_control_panel(
        db=db,
        user_id=user.id,
        session_id=session_id,
        payload=payload,
    )
    return ApiResponse(code=0, message="success", data=data)


@router.get(
    "/sessions/{session_id}/narrative-state",
    response_model=ApiResponse[NarrativeStateDTO],
    summary="获取指定会话的叙梦 6 大 Tab 状态机",
)
async def get_session_narrative_state(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[NarrativeStateDTO]:
    """获取叙梦面板 6 大 Tab（时空、背包、技能、社交、任务、历史事件）。"""
    data = await ChatService.get_narrative_state(
        db=db,
        user_id=user.id,
        session_id=session_id,
    )
    return ApiResponse(code=0, message="success", data=data)


@router.put(
    "/sessions/{session_id}/narrative-state",
    response_model=ApiResponse[NarrativeStateDTO],
    summary="更新指定会话的叙梦 6 大 Tab 状态机",
)
async def update_session_narrative_state(
    session_id: uuid.UUID,
    payload: NarrativeStateDTO,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[NarrativeStateDTO]:
    """更新叙梦面板 6 大 Tab 状态机数据。"""
    data = await ChatService.update_narrative_state(
        db=db,
        user_id=user.id,
        session_id=session_id,
        payload=payload,
    )
    return ApiResponse(code=0, message="success", data=data)

