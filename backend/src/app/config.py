"""系统全局配置模块。

基于 Pydantic Settings 实现类型安全的环境变量加载与解析。
支持从系统环境变量或 `.env` 文件读取。

Usage:
    >>> from app.config import get_settings
    >>> settings = get_settings()
    >>> print(settings.DATABASE_URL)
    'postgresql+asyncpg://...'
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """SpikeAI 全局系统配置类。

    Attributes:
        APP_NAME (str): 应用程序名称。
        APP_ENV (str): 运行环境 (development / staging / production)。
        DEBUG (bool): 是否开启调试模式。
        SECRET_KEY (str): 系统安全密钥，用于加解密。

        DATABASE_URL (str): 异步 PostgreSQL 数据库连接串 (asyncpg)。
        DB_POOL_SIZE (int): 数据库连接池基础大小。
        DB_MAX_OVERFLOW (int): 连接池最大溢出大小。
        DB_POOL_TIMEOUT (int): 连接池获取超时时间（秒）。

        REDIS_URL (str): Redis 连接串。

        JWT_SECRET (str): JWT 签名密钥。
        JWT_ALGORITHM (str): JWT 签名算法。
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Access Token 过期时长（分钟）。

        OPENAI_API_KEY (str): OpenAI API 密钥。
        OPENAI_BASE_URL (str): OpenAI API 代理/基础网关地址。
        DEEPSEEK_API_KEY (str): DeepSeek API 密钥。
        GEMINI_API_KEY (str): Gemini API 密钥。
        OLLAMA_BASE_URL (str): 本地 Ollama 接口地址。

        UPLOAD_DIR (str): 用户上传文件（角色卡/头像）本地存储路径。
        MAX_UPLOAD_SIZE_MB (int): 最大上传文件限制（MB）。
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # 基础服务信息
    APP_NAME: str = "SpikeAI API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = True
    SECRET_KEY: str = Field(
        default="spikeai_dev_secret_key_32_characters_long_min",
        description="用于系统内部加密的密钥",
    )

    @property
    def ENV(self) -> str:
        return self.APP_ENV

    # 异步数据库配置 (PostgreSQL 16)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://spikeai:spikeai_password@localhost:5432/spikeai_db",
        description="PostgreSQL asyncpg 异步连接串",
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    # Redis 缓存与分布式锁
    REDIS_URL: str = Field(
        default="redis://:spikeai_redis_pass@localhost:6379/0",
        description="Redis 异步连接串",
    )

    # JWT 鉴权安全
    JWT_SECRET: str = Field(
        default="spikeai_jwt_secret_dev_key_2026_secure",
        description="JWT 签名密钥",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # 多渠道大模型 API
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    DEEPSEEK_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # MIMO API (小米 mimo-v2.5)
    MIMO_API_KEY: str = "sk-cm6d7d8eo1ymvfo748hq68nqdcrwnwp0onaqbjujinst5seo"
    MIMO_BASE_URL: str = "https://api.xiaomimimo.com/v1"

    # LongCat API (LongCat-2.0)
    LONGCAT_API_KEY: str = "ak_2lI2QB9o81qD3K61fH9kJ1xB0hP0a"
    LONGCAT_BASE_URL: str = "https://api.longcat.chat/openai"

    # 角色卡与静态资源存储
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 20

    # MinIO / S3 对象存储配置
    STORAGE_BACKEND: Literal["minio", "local"] = "minio"
    MINIO_ENDPOINT: str = "140.143.87.234:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "naro-assets"
    MINIO_PUBLIC_URL_PREFIX: str = "http://140.143.87.234:9000/naro-assets"
    MINIO_SECURE: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取单例配置对象。

    使用 LRU 缓存确保配置只在进程启动时加载一次，减少 I/O 开销。

    Returns:
        Settings: 强类型配置实例。

    Usage:
        >>> settings = get_settings()
        >>> print(settings.APP_ENV)
        'development'
    """
    return Settings()
