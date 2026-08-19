"""防御性异常体系定义模块。

本模块定义了系统的层级化业务异常，严禁静默捕获任何未处理的异常，
所有异常均携带清晰的状态码、内部错误标识与人类可读的上下文信息。

Usage:
    >>> from app.core.exceptions import InsufficientBalanceError
    >>> raise InsufficientBalanceError(required=10, available=5, currency="star_coin")
"""

from typing import Any

from fastapi import status


class AppException(Exception):
    """系统顶级抽象业务异常。

    Attributes:
        status_code (int): HTTP 响应状态码。
        error_code (str): 机器可识别的业务错误码。
        message (str): 错误描述信息。
        details (Optional[Dict[str, Any]]): 额外的上下文调试信息。
    """

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_SERVER_ERROR",
        message: str = "系统内部发生未知异常，请稍后重试",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """将异常转换为统一 API 响应格式。

        Returns:
            Dict[str, Any]: 结构化错误字典。
        """
        return {
            "success": False,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class EntityNotFoundError(AppException):
    """实体资源未找到异常 (404)。"""

    def __init__(
        self,
        entity_name: str,
        entity_id: Any,
        message: str | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ENTITY_NOT_FOUND",
            message=message or f"未找到指定的 {entity_name} (ID: {entity_id})",
            details={"entity_name": entity_name, "entity_id": str(entity_id)},
        )


class AuthenticationError(AppException):
    """身份认证失败异常 (401)。"""

    def __init__(self, message: str = "身份凭证无效或已过期，请重新登录") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_FAILED",
            message=message,
        )


class PermissionDeniedError(AppException):
    """权限不足异常 (403)。"""

    def __init__(self, message: str = "您没有权限执行此操作") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="PERMISSION_DENIED",
            message=message,
        )


class InsufficientBalanceError(AppException):
    """钱包余额不足异常 (402)。"""

    def __init__(
        self,
        required: int,
        available: int,
        currency: str = "star_coin",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code="INSUFFICIENT_BALANCE",
            message=f"{'星元' if currency == 'star_coin' else '月华'} 余额不足，需要 {required}，当前可用 {available}",
            details={"required": required, "available": available, "currency": currency},
        )


class CardParsingError(AppException):
    """SillyTavern 角色卡 PNG 编解码异常 (422)。"""

    def __init__(self, reason: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="CARD_PARSING_FAILED",
            message=f"角色卡解析失败: {reason}",
            details=details,
        )


class LLMStreamError(AppException):
    """大模型流式调用网关异常 (502)。"""

    def __init__(self, provider: str, reason: str) -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="LLM_STREAM_ERROR",
            message=f"大模型服务提供商 [{provider}] 请求失败: {reason}",
            details={"provider": provider, "reason": reason},
        )
