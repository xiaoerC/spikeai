"""通用 API 请求响应与分页 DTO 契约。

定义符合大厂 RESTful 标准的统一响应体结构与分页封装。

Usage:
    >>> from app.schemas.common import ApiResponse, PaginatedResponse
    >>> resp = ApiResponse(code=0, message="success", data={"id": 1})
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 业务响应体包装器。"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    code: int = Field(default=0, description="业务状态码，0 表示成功，非 0 表示具体错误码")
    message: str = Field(default="success", description="提示信息或错误原因")
    show_message: bool = Field(default=False, description="前端是否应弹窗/Toast 展示 message 提示")
    data: T | None = Field(default=None, description="业务负载数据")


class ApiErrorResponse(BaseModel):
    """统一错误响应体。"""

    code: int = Field(..., description="业务错误码 (如 40001, 40101, 50001)")
    message: str = Field(..., description="用户友好的错误描述")
    error_details: str | None = Field(default=None, description="详细的错误堆栈或异常原因")


class PaginationParams(BaseModel):
    """通用分页查询参数。"""

    page: int = Field(default=1, ge=1, description="当前页码，从 1 开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数，最大 100")


class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页列表数据包装。"""

    items: list[T] = Field(default_factory=list, description="当前页数据列表")
    total: int = Field(default=0, ge=0, description="总记录数")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, description="每页条数")
    total_pages: int = Field(default=0, ge=0, description="总页数")
