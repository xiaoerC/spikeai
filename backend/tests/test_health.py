"""系统健康检查接口自动化测试用例。

Usage:
    $ uv run pytest tests/test_health.py
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint() -> None:
    """测试 /api/v1/health 健康探针接口连通性与数据结构完整性。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        payload = response.json()

        # 校验核心字段结构
        assert "status" in payload
        assert "app_name" in payload
        assert "version" in payload
        assert "environment" in payload
        assert "timestamp" in payload
        assert "components" in payload

        assert payload["status"] == "healthy"
        assert payload["components"].get("api") == "operational"
