"""图片与文件资产上传 API 路由模块。

支持上传立绘、封面背景、聊天背景及角色卡资产，直接对接 MinIO 对象存储，并支持优雅本地存储降级。

Usage:
    POST /api/v1/upload/image
    Content-Type: multipart/form-data
    file: <binary>
    folder: "avatars" | "banners" | "chat"
"""

from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.common import ApiResponse
from app.services.storage_service import storage_service

router = APIRouter(prefix="/upload", tags=["Upload 上传资产"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/image",
    response_model=ApiResponse[dict],
    summary="上传单张图片资产 (MinIO/Local)",
    description="支持 JPG, PNG, WEBP, GIF，文件上限 10MB。自动持久化至 MinIO 并返回公开直链 URL。",
)
async def upload_image(
    file: UploadFile = File(..., description="待上传的图片文件"),
    folder: Literal["avatars", "banners", "chat", "cards"] = Form(
        "avatars", description="归档目标目录"
    ),
) -> ApiResponse[dict]:
    """处理图片上传请求。"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式: {file.content_type}，仅支持 JPG/PNG/WEBP/GIF",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片体积超过 10MB 限制",
        )

    url = await storage_service.upload_image(
        file_bytes=file_bytes,
        original_filename=file.filename or "image.png",
        folder=folder,
        content_type=file.content_type or "image/png",
    )

    return ApiResponse(
        code=0,
        message="图片上传成功",
        show_message=False,
        data={"url": url, "filename": file.filename},
    )
