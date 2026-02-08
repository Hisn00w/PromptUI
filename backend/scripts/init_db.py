#!/usr/bin/env python3
"""初始化数据库表并播种默认分类"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


DEFAULT_CATEGORIES = [
    {"key": "layouts", "name": "页面结构", "description": "页面布局相关的提示词，包括首屏、侧栏、网格、瀑布流等"},
    {"key": "cards", "name": "卡片形式", "description": "卡片组件相关的提示词"},
    {"key": "components", "name": "基础组件", "description": "通用 UI 组件相关的提示词"},
    {"key": "animations", "name": "动效方式", "description": "动画和过渡效果相关的提示词"},
    {"key": "colors", "name": "配色搭配", "description": "配色方案相关的提示词"},
]


async def init_db():
    """创建所有数据库表"""
    from app.db.session import engine
    from app.db.base import Base

    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

    print("✓ Database tables created successfully!")


async def seed_categories():
    """播种默认分类（如果不存在）"""
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    from app.models.category import Category

    async with AsyncSessionLocal() as session:
        for cat_data in DEFAULT_CATEGORIES:
            exists = await session.scalar(
                select(Category).where(Category.key == cat_data["key"])
            )
            if not exists:
                session.add(Category(**cat_data))
                print(f"  + Category '{cat_data['key']}' created")
            else:
                print(f"  - Category '{cat_data['key']}' already exists")
        await session.commit()

    print("✓ Default categories seeded!")


async def main():
    """Main entry point - run all initialization steps in a single event loop"""
    await init_db()
    await seed_categories()


if __name__ == "__main__":
    asyncio.run(main())
