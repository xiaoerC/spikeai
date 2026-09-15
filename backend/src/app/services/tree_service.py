"""DAG 剧情分支树与多平行宇宙状态机核心领域服务。

实现基于 Parent-Pointer 的有向无环图分支树算法、只追加 (Append-Only) 历史版本控制、
分支分叉 (Fork)、节点回溯 (Rollback)、消息编辑双模式策略以及 Vue Flow 拓扑图生成。

Usage:
    >>> from app.services.tree_service import TreeService
    >>> from app.schemas.chat import ForkBranchRequest
    >>> branch = await TreeService.fork_branch(db, session_id, user_id, ForkBranchRequest(fork_message_id=msg_id))
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatMessage, ChatSession, StoryBranch
from app.schemas.chat import (
    ChatSessionResponse,
    DAGEdgeDTO,
    DAGGraphDTO,
    DAGNodeDTO,
    EditMessageRequest,
    ForkBranchRequest,
    RollbackRequest,
    StoryBranchDetailDTO,
)
from app.services.chat_service import ChatService

logger = logging.getLogger("spikeai.tree")


class TreeService:
    """DAG 剧情分支与平行宇宙状态机服务。"""

    @classmethod
    async def get_session_branches(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[StoryBranchDetailDTO]:
        """获取指定会话的所有剧情分支及其节点统计。

        Args:
            db: 数据库异步会话
            session_id: 会话 UUID
            user_id: 当前用户 UUID

        Returns:
            list[StoryBranchDetailDTO]: 分支列表
        """
        # 1. 验证会话归属
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权访问",
            )

        # 2. 查询所有分支
        stmt = (
            select(StoryBranch)
            .where(StoryBranch.session_id == session_id)
            .order_by(StoryBranch.is_main.desc(), StoryBranch.created_at.asc())
        )
        result = await db.execute(stmt)
        branches = list(result.scalars().all())

        # 3. 统计每个分支独立节点数
        count_stmt = (
            select(ChatMessage.branch_id, func.count(ChatMessage.id))
            .where(ChatMessage.session_id == session_id)
            .group_by(ChatMessage.branch_id)
        )
        count_res = await db.execute(count_stmt)
        node_counts: dict[uuid.UUID, int] = dict(count_res.all())  # type: ignore[arg-type]

        # 4. 构建 DTO 列表
        detail_list: list[StoryBranchDetailDTO] = []
        for b in branches:
            # 计算总路径长度 (递归祖先 + 自身)
            path_msgs = await cls.get_branch_active_messages(db, session_id, b.id)
            detail_list.append(
                StoryBranchDetailDTO(
                    id=b.id,
                    session_id=b.session_id,
                    name=b.name,
                    parent_branch_id=b.parent_branch_id,
                    fork_message_id=b.fork_message_id,
                    is_main=b.is_main,
                    node_count=node_counts.get(b.id, 0),
                    total_path_count=len(path_msgs),
                    created_at=b.created_at,
                )
            )

        return detail_list

    @classmethod
    async def get_branch_active_messages(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        branch_id: uuid.UUID,
    ) -> list[ChatMessage]:
        """递归追溯并组装指定分支的完整历史消息链 (Active Path)。

        遵循 Parent-Pointer 机制：
        [祖先分支自根节点至 fork_message_id 的消息] + [当前分支特有消息]

        Args:
            db: 数据库异步会话
            session_id: 会话 UUID
            branch_id: 目标分支 UUID

        Returns:
            list[ChatMessage]: 完整时序消息列表
        """
        branch = await db.get(StoryBranch, branch_id)
        if not branch or branch.session_id != session_id:
            return []

        # 1. 获取当前分支自身的消息
        curr_stmt = (
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session_id,
                ChatMessage.branch_id == branch_id,
            )
            .order_by(ChatMessage.created_at.asc())
        )
        curr_res = await db.execute(curr_stmt)
        curr_messages = list(curr_res.scalars().all())

        # 2. 如果是主线或没有父分支，直接返回自身消息
        if branch.is_main or not branch.parent_branch_id or not branch.fork_message_id:
            return curr_messages

        # 3. 递归追溯父分支消息直至 fork_message_id
        parent_messages = await cls.get_branch_active_messages(
            db, session_id, branch.parent_branch_id
        )

        # 截取父分支截至 fork_message_id 的部分
        ancestor_messages: list[ChatMessage] = []
        for m in parent_messages:
            ancestor_messages.append(m)
            if m.id == branch.fork_message_id:
                break

        return ancestor_messages + curr_messages

    @classmethod
    async def fork_branch(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: ForkBranchRequest,
    ) -> StoryBranchDetailDTO:
        """从指定消息节点派生新的平行剧情分支。

        Args:
            db: 数据库异步会话
            session_id: 会话 UUID
            user_id: 用户 UUID
            payload: 分叉请求参数

        Returns:
            StoryBranchDetailDTO: 新建分支详情
        """
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权访问",
            )

        fork_msg = await db.get(ChatMessage, payload.fork_message_id)
        if not fork_msg or fork_msg.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的分叉消息节点不存在",
            )

        # 统计已有分支数生成默认名称
        count_stmt = select(func.count(StoryBranch.id)).where(StoryBranch.session_id == session_id)
        count_res = await db.execute(count_stmt)
        existing_branch_count = count_res.scalar() or 0

        clean_snippet = fork_msg.content.replace("\n", " ").strip()[:10]
        branch_name = (
            payload.name.strip()
            if payload.name and payload.name.strip()
            else f"🔀 分支 {existing_branch_count}：{clean_snippet}..."
        )

        new_branch = StoryBranch(
            id=uuid.uuid4(),
            session_id=session_id,
            name=branch_name,
            parent_branch_id=fork_msg.branch_id,
            fork_message_id=fork_msg.id,
            is_main=False,
        )
        db.add(new_branch)

        if payload.switch_to:
            session.current_branch_id = new_branch.id

        await db.commit()
        await db.refresh(new_branch)

        path_msgs = await cls.get_branch_active_messages(db, session_id, new_branch.id)

        logger.info(
            "Forked new story branch '%s' (%s) from msg %s",
            new_branch.name,
            new_branch.id,
            fork_msg.id,
        )

        return StoryBranchDetailDTO(
            id=new_branch.id,
            session_id=new_branch.session_id,
            name=new_branch.name,
            parent_branch_id=new_branch.parent_branch_id,
            fork_message_id=new_branch.fork_message_id,
            is_main=new_branch.is_main,
            node_count=0,
            total_path_count=len(path_msgs),
            created_at=new_branch.created_at,
        )

    @classmethod
    async def switch_branch(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        branch_id: uuid.UUID,
    ) -> ChatSessionResponse:
        """切换当前会话的活跃剧情分支。

        Args:
            db: 数据库异步会话
            session_id: 会话 UUID
            user_id: 用户 UUID
            branch_id: 目标分支 UUID

        Returns:
            ChatSessionResponse: 切换后的完整会话详情
        """
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权访问",
            )

        branch = await db.get(StoryBranch, branch_id)
        if not branch or branch.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="目标分支不存在",
            )

        session.current_branch_id = branch_id
        await db.commit()

        logger.info("Switched session %s to branch '%s' (%s)", session_id, branch.name, branch_id)
        session = await ChatService.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        return await ChatService.get_session_response(db=db, session=session)

    @classmethod
    async def delete_branch(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        branch_id: uuid.UUID,
    ) -> None:
        """删除指定非主线分支。

        Args:
            db: 数据库异步会话
            session_id: 会话 UUID
            user_id: 用户 UUID
            branch_id: 待删除分支 UUID
        """
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权访问",
            )

        branch = await db.get(StoryBranch, branch_id)
        if not branch or branch.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分支不存在",
            )

        if branch.is_main:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法删除主线剧情分支",
            )

        # 若当前会话正处于被删除的分支，先切回主线
        if session.current_branch_id == branch_id:
            main_stmt = select(StoryBranch).where(
                StoryBranch.session_id == session_id,
                StoryBranch.is_main.is_(True),
            )
            main_res = await db.execute(main_stmt)
            main_branch = main_res.scalar_one_or_none()
            if main_branch:
                session.current_branch_id = main_branch.id

        await db.delete(branch)
        await db.commit()
        logger.info("Deleted branch %s from session %s", branch_id, session_id)

    @classmethod
    async def rollback_to_message(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: RollbackRequest,
    ) -> ChatSessionResponse:
        """回溯至指定消息节点。

        Args:
            db: 数据库异步会话
            session_id: 会话 UUID
            user_id: 用户 UUID
            payload: 回溯参数 (模式: fork 或 truncate)

        Returns:
            ChatSessionResponse: 回溯后的会话详情
        """
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权访问",
            )

        target_msg = await db.get(ChatMessage, payload.target_message_id)
        if not target_msg or target_msg.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="目标消息节点不存在",
            )

        if payload.mode == "fork":
            # 模式 1: 派生新分支保留旧历史
            fork_dto = await cls.fork_branch(
                db=db,
                session_id=session_id,
                user_id=user_id,
                payload=ForkBranchRequest(
                    fork_message_id=target_msg.id,
                    name=payload.branch_name,
                    switch_to=True,
                ),
            )
            session = await ChatService.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        return await ChatService.get_session_response(db=db, session=session)

        # 模式 2: 原地截断模式 (Truncate)
        # 删除当前分支中在 target_msg 之后创建的所有消息
        del_stmt = delete(ChatMessage).where(
            ChatMessage.session_id == session_id,
            ChatMessage.branch_id == target_msg.branch_id,
            ChatMessage.created_at > target_msg.created_at,
        )
        await db.execute(del_stmt)
        session.current_branch_id = target_msg.branch_id
        await db.commit()

        logger.info(
            "Rolled back session %s to message %s (truncate mode)",
            session_id,
            target_msg.id,
        )
        session = await ChatService.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        return await ChatService.get_session_response(db=db, session=session)

    @classmethod
    async def edit_message(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        message_id: uuid.UUID,
        payload: EditMessageRequest,
    ) -> ChatSessionResponse:
        """编辑消息内容 (支持模式 A: 原位修改 / 模式 B: 分叉并重跑)。

        Args:
            db: 数据库异步会话
            session_id: 会话 UUID
            user_id: 用户 UUID
            message_id: 消息 UUID
            payload: 编辑请求

        Returns:
            ChatSessionResponse: 修改后的会话详情
        """
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权访问",
            )

        target_msg = await db.get(ChatMessage, message_id)
        if not target_msg or target_msg.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="待编辑消息不存在",
            )

        if payload.mode == "edit_only":
            # 模式 A: 仅原位保存修改
            target_msg.content = payload.content
            await db.commit()
            logger.info("Edited message %s content in-place", message_id)
            session = await ChatService.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
            return await ChatService.get_session_response(db=db, session=session)

        # 模式 B: 保存并派生新分支 (Edit and Fork)
        # 以该消息的父节点为起点开辟新分支
        fork_point_id = target_msg.parent_message_id or target_msg.id
        new_branch_dto = await cls.fork_branch(
            db=db,
            session_id=session_id,
            user_id=user_id,
            payload=ForkBranchRequest(
                fork_message_id=fork_point_id,
                name=payload.branch_name or f"🔀 改写：{payload.content[:10]}...",
                switch_to=True,
            ),
        )

        # 在新分支上创建修改后的消息副本
        new_msg = ChatMessage(
            id=uuid.uuid4(),
            session_id=session_id,
            branch_id=new_branch_dto.id,
            sender=target_msg.sender,
            character_name=target_msg.character_name,
            avatar_url=target_msg.avatar_url,
            content=payload.content,
            parent_message_id=target_msg.parent_message_id,
        )
        db.add(new_msg)
        await db.commit()

        logger.info(
            "Edited message %s via fork to new branch %s",
            message_id,
            new_branch_dto.id,
        )
        session = await ChatService.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        return await ChatService.get_session_response(db=db, session=session)

    @classmethod
    async def get_dag_graph(
        cls,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> DAGGraphDTO:
        """生成供前端 Vue Flow 渲染的全景 DAG 剧情树拓扑图。

        Args:
            db: 数据库异步会话
            session_id: 会话 UUID
            user_id: 用户 UUID

        Returns:
            DAGGraphDTO: 包含完整节点与有向边的图结构
        """
        session = await db.get(ChatSession, session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权访问",
            )

        # 1. 查询所有分支
        b_stmt = select(StoryBranch).where(StoryBranch.session_id == session_id)
        b_res = await db.execute(b_stmt)
        branches = {b.id: b for b in b_res.scalars().all()}

        # 2. 查询所有消息
        m_stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        m_res = await db.execute(m_stmt)
        all_messages = list(m_res.scalars().all())

        # 3. 统计分叉点
        fork_point_ids = {b.fork_message_id for b in branches.values() if b.fork_message_id}

        # 4. 当前活跃路径末端
        active_branch_id = session.current_branch_id or uuid.uuid4()
        active_path = await cls.get_branch_active_messages(db, session_id, active_branch_id)
        active_last_msg_id = active_path[-1].id if active_path else None

        nodes: list[DAGNodeDTO] = []
        edges: list[DAGEdgeDTO] = []

        # 按分支分组消息
        branch_msgs: dict[uuid.UUID, list[ChatMessage]] = {}
        for m in all_messages:
            branch_msgs.setdefault(m.branch_id, []).append(m)

            b_info = branches.get(m.branch_id)
            branch_name = b_info.name if b_info else "未知分支"
            is_main = b_info.is_main if b_info else False

            clean_summary = (
                m.content.replace("<thinking>", "")
                .replace("</thinking>", "")
                .replace("\n", " ")
                .strip()
            )
            if len(clean_summary) > 60:
                clean_summary = f"{clean_summary[:60]}..."

            time_str = m.created_at.strftime("%H:%M") if m.created_at else "00:00"

            nodes.append(
                DAGNodeDTO(
                    id=f"node_{m.id}",
                    message_id=m.id,
                    branch_id=m.branch_id,
                    branch_name=branch_name,
                    sender=m.sender,
                    character_name=m.character_name,
                    avatar_url=m.avatar_url,
                    content=m.content,
                    summary=clean_summary,
                    timestamp=time_str,
                    is_current=(m.id == active_last_msg_id),
                    is_main=is_main,
                    is_fork_point=(m.id in fork_point_ids),
                    parent_message_id=m.parent_message_id,
                )
            )

        # 5. 构建边 (Edges)
        # A. 分支内部连续节点连线
        for b_id, msgs in branch_msgs.items():
            b_info = branches.get(b_id)
            is_main_branch = b_info.is_main if b_info else False

            for i in range(len(msgs) - 1):
                src = msgs[i]
                tgt = msgs[i + 1]
                edges.append(
                    DAGEdgeDTO(
                        id=f"edge_{src.id}_{tgt.id}",
                        source=f"node_{src.id}",
                        target=f"node_{tgt.id}",
                        is_main=is_main_branch,
                    )
                )

        # B. 分支分叉连线 (fork_message -> 该分支第 1 条特有消息)
        for b_id, b_info in branches.items():
            if b_info.fork_message_id and b_id in branch_msgs and len(branch_msgs[b_id]) > 0:
                first_child = branch_msgs[b_id][0]
                edges.append(
                    DAGEdgeDTO(
                        id=f"edge_fork_{b_info.fork_message_id}_{first_child.id}",
                        source=f"node_{b_info.fork_message_id}",
                        target=f"node_{first_child.id}",
                        is_main=False,
                    )
                )

        return DAGGraphDTO(
            nodes=nodes,
            edges=edges,
            active_branch_id=active_branch_id,
            active_message_id=active_last_msg_id,
        )
