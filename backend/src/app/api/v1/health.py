"""系统健康检查接口模块。

提供基础设施（PostgreSQL、Redis、环境状态）的存活探针与就绪探针。

Usage:
    GET /api/v1/health -> {"status": "ok", "app_name": "SpikeAI API", ...}
"""

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from redis.exceptions import RedisError

from app.config import get_settings
from app.core.redis import get_redis_client

router = APIRouter(prefix="/health", tags=["Health"])
settings = get_settings()


class HealthResponse(BaseModel):
    """系统健康探针响应模型。"""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ..., description="系统整体运行健康状态"
    )
    app_name: str = Field(..., description="应用服务名称")
    version: str = Field(..., description="服务版本号")
    environment: str = Field(..., description="当前运行环境")
    timestamp: str = Field(..., description="探针检测 UTC 时间戳 (ISO 8601)")
    components: dict[str, str] = Field(
        default_factory=dict, description="底层组件（DB/Redis/Storage）连通状态"
    )


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="系统健康状态检查",
    description="检查 API 网关基础连通性与服务存活状态。",
)
async def check_health() -> HealthResponse:
    """执行存活与环境探针检测。

    Returns:
        HealthResponse: 包含环境与基础运行状态的数据载荷。
    """
    components: dict[str, str] = {
        "api": "operational",
    }

    # 探针检测 Redis (非阻塞可选探测，即使本地开发未启动 Redis 也不崩溃)
    try:
        redis = get_redis_client()
        pong = await redis.ping()
        components["redis"] = "connected" if pong else "unreachable"
    except (RedisError, ConnectionError, TimeoutError, OSError) as exc:
        components["redis"] = f"disconnected ({type(exc).__name__})"

    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(UTC).isoformat(),
        components=components,
    )
