"""
Alembic 数据库迁移环境配置文件

常用命令（在项目根目录执行）：
1. 生成迁移脚本（自动检测模型变化）：
   alembic revision --autogenerate -m "描述信息"

2. 执行迁移（升级到最新版本）：
   alembic upgrade head

3. 回滚一个版本：
   alembic downgrade -1

4. 查看当前版本：
   alembic current

5. 查看迁移历史：
   alembic history

注意：
- 确保 .env 文件中已配置 DATABASE_URL
- 所有模型必须继承 app.db.session.Base 并在此处导入
"""

from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# ✅ 关键：确保 alembic 运行时能 import 到项目里的 app 包
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]  # 项目根目录（包含 app/ 的那层）
sys.path.insert(0, str(BASE_DIR))

# 加载 .env 文件到环境变量（确保 DATABASE_URL 可用）
load_dotenv()

# Alembic Config 对象（提供 alembic.ini 中的配置）
config = context.config

# 从环境变量读取数据库连接串，写入 Alembic 配置
# 这样可以避免在 alembic.ini 中硬编码数据库 URL
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
else:
    raise ValueError("DATABASE_URL environment variable is not set")

# 解析 alembic.ini 日志配置（如果存在）
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入所有模型的 Base，以便 Alembic 自动检测表结构变化
# ✅ 必须导入 app.models，确保所有模型都注册到 Base.metadata
from app.models import Base  # 这会触发所有模型的导入

# 设置 target_metadata，Alembic 会根据这个元数据生成迁移脚本
# 如果不设置，autogenerate 将不起作用
target_metadata = Base.metadata

# 其他值从 config 对象获取（由 env.py 文件自身使用）
# target_metadata = None  # 如果不使用 autogenerate，可以设为 None


def run_migrations_offline() -> None:
    """
    离线模式：生成 SQL 脚本但不连接数据库
    使用场景：当你需要手动执行 SQL 或在无数据库连接的环境中生成迁移
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在线模式：直接连接数据库执行迁移
    这是最常用的模式（alembic upgrade head）
    """
    # 从配置创建数据库引擎（使用连接池）
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # 迁移时使用简单连接池
    )

    with connectable.connect() as connection:
        # 配置迁移上下文
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        # 在事务中执行迁移
        with context.begin_transaction():
            context.run_migrations()


# 根据 Alembic 运行模式选择对应函数
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
