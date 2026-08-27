"""对象存储与文件上传服务模块。

支持 MinIO (S3 兼容协议) 对象存储与本地静态文件弹性降级双模式。
用于头像、背景封面、角色卡卡面及多模态资产的无损持久化与公网直链分发。

Usage:
    >>> from app.services.storage_service import storage_service
    >>> url = await storage_service.upload_image(file_bytes, "avatar.png", folder="avatars")
    >>> print(url)
    'http://140.143.87.234:9000/naro-assets/avatars/xxxx.png'
"""

import io
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


class StorageService:
    """统一对象存储服务。"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._minio_client = None
        self._init_minio_client()

    def _init_minio_client(self) -> None:
        """初始化 MinIO 客户端并确保存储桶就绪。"""
        if self.settings.STORAGE_BACKEND != "minio":
            logger.info("StorageService configured with LOCAL backend.")
            return

        try:
            from minio import Minio

            self._minio_client = Minio(
                endpoint=self.settings.MINIO_ENDPOINT,
                access_key=self.settings.MINIO_ACCESS_KEY,
                secret_key=self.settings.MINIO_SECRET_KEY,
                secure=self.settings.MINIO_SECURE,
            )
            # 确保存储桶存在
            bucket = self.settings.MINIO_BUCKET_NAME
            if not self._minio_client.bucket_exists(bucket):
                self._minio_client.make_bucket(bucket)
                logger.info("MinIO bucket '%s' created successfully.", bucket)
            logger.info("MinIO client initialized connected to %s", self.settings.MINIO_ENDPOINT)
        except Exception as e:
            logger.warning(
                "Failed to initialize MinIO client (%s). Fallback to local storage enabled.",
                e,
            )
            self._minio_client = None

    async def upload_image(
        self,
        file_bytes: bytes,
        original_filename: str,
        folder: str = "avatars",
        content_type: str = "image/png",
    ) -> str:
        """上传图片并返回公网访问 URL。

        Args:
            file_bytes: 原始二进制图片内容
            original_filename: 原始文件名（用于提取后缀）
            folder: 归档目录（如 'avatars', 'banners', 'cards'）
            content_type: MIME 类型

        Returns:
            str: 可公开访问的图片 URL
        """
        ext = Path(original_filename).suffix.lower() or ".png"
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            ext = ".png"

        unique_name = f"{uuid.uuid4().hex}{ext}"
        object_key = f"{folder}/{unique_name}"

        # 1. 尝试使用 MinIO 上传
        if self._minio_client is not None:
            try:
                data_stream = io.BytesIO(file_bytes)
                self._minio_client.put_object(
                    bucket_name=self.settings.MINIO_BUCKET_NAME,
                    object_name=object_key,
                    data=data_stream,
                    length=len(file_bytes),
                    content_type=content_type,
                )
                url = f"{self.settings.MINIO_PUBLIC_URL_PREFIX.rstrip('/')}/{object_key}"
                logger.info("Uploaded to MinIO: %s", url)
                return url
            except Exception as e:
                logger.warning("MinIO upload failed (%s). Falling back to local storage.", e)

        # 2. 本地存储降级 (Local Fallback)
        upload_dir = Path(self.settings.UPLOAD_DIR) / folder
        upload_dir.mkdir(parents=True, exist_ok=True)
        local_file_path = upload_dir / unique_name
        local_file_path.write_bytes(file_bytes)

        # 本地服务静态 URL (通过 /static/uploads 挂载)
        local_url = f"/static/uploads/{folder}/{unique_name}"
        logger.info("Saved to local storage: %s", local_url)
        return local_url


storage_service = StorageService()
