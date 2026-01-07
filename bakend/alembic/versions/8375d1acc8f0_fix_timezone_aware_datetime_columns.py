"""fix_timezone_aware_datetime_columns

Revision ID: 8375d1acc8f0
Revises: 453181091015
Create Date: 2026-01-04 16:57:28.925654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8375d1acc8f0'
down_revision = '453181091015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    升级数据库结构（应用此迁移）
    将 trip_stops 表的 arrived_at 和 completed_at 列从 TIMESTAMP 改为 TIMESTAMP WITH TIME ZONE
    
    注意：
    1. PostgreSQL 会将现有的 naive datetime 值视为本地时区时间
    2. 为了安全，假设现有数据都是 UTC 时间（与 datetime.utcnow() 一致）
    3. 使用 AT TIME ZONE 'UTC' 将 naive timestamp 转换为 UTC timezone-aware
    """
    # 修改 arrived_at 列
    # 步骤 1: 将列类型改为 TIMESTAMPTZ，并将现有值视为 UTC
    op.execute("""
        ALTER TABLE trip_stops 
        ALTER COLUMN arrived_at 
        TYPE TIMESTAMP WITH TIME ZONE 
        USING arrived_at AT TIME ZONE 'UTC'
    """)
    
    # 修改 completed_at 列
    op.execute("""
        ALTER TABLE trip_stops 
        ALTER COLUMN completed_at 
        TYPE TIMESTAMP WITH TIME ZONE 
        USING completed_at AT TIME ZONE 'UTC'
    """)


def downgrade() -> None:
    """
    降级数据库结构（回滚此迁移）
    将 TIMESTAMP WITH TIME ZONE 改回 TIMESTAMP（移除时区信息）
    
    警告：回滚会丢失时区信息！
    """
    # 回滚 completed_at
    op.execute("""
        ALTER TABLE trip_stops 
        ALTER COLUMN completed_at 
        TYPE TIMESTAMP 
        USING completed_at AT TIME ZONE 'UTC'
    """)
    
    # 回滚 arrived_at
    op.execute("""
        ALTER TABLE trip_stops 
        ALTER COLUMN arrived_at 
        TYPE TIMESTAMP 
        USING arrived_at AT TIME ZONE 'UTC'
    """)
