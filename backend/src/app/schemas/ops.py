"""运营与支持领域 Pydantic v2 DTO 契约。

包含活动中心 (Activity)、公告中心 (Notice) 与问卷调查 (Survey)。

Usage:
    >>> from app.schemas.ops import NoticeResponse, ActivityResponse
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ActivityResponse(BaseModel):
    """运营活动响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="活动 ID")
    title: str = Field(..., description="活动标题")
    tag: str = Field(..., description="标签 (招募/征集/福利)")
    reward_text: str = Field(..., description="奖励说明")
    date_range: str = Field(..., description="时间范围")
    status: str = Field(..., description="状态 (active / ended)")
    rules: list[str] = Field(default_factory=list, description="活动规则列表")
    created_at: datetime = Field(..., description="发布时间")


class NoticeResponse(BaseModel):
    """系统公告响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="公告 ID")
    title: str = Field(..., description="标题")
    category: str = Field(..., description="分类 (系统公告/更新日志/活动公告)")
    date_text: str = Field(..., description="显示日期")
    badge_type: str = Field(default="notice", description="徽章类型 (update/notice/event)")
    summary: str = Field(..., description="摘要")
    content_html: str = Field(default="", description="富文本详情")
    created_at: datetime = Field(..., description="发布时间")


class SurveyResponse(BaseModel):
    """问卷调查响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="问卷 ID")
    title: str = Field(..., description="问卷标题")
    reward_star: int = Field(..., description="奖励星元数")
    category: str = Field(..., description="分类")
    duration_text: str = Field(default="约3分钟", description="用时说明")
    status: str = Field(default="active", description="状态 (active/completed)")
    questions: list[dict[str, Any]] = Field(default_factory=list, description="题目列表")
    created_at: datetime = Field(..., description="发布时间")


class SurveySubmitRequest(BaseModel):
    """提交问卷请求体。"""

    answers: dict[str, Any] = Field(..., description="用户填写的答案字典 (题号 -> 选项/文本)")
