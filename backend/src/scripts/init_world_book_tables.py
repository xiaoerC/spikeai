"""初始化世界书相关数据库表。

Usage:
    uv run python -m src.scripts.init_world_book_tables
"""

import asyncio
from app.core.database import async_engine, Base
import app.models  # 确保加载所有模型


async def main() -> None:
    print("开始检查并创建数据库表...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表结构同步完成 (world_books, world_book_entries 已创建)！")


if __name__ == "__main__":
    asyncio.run(main())
