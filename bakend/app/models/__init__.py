"""
Models 包：导出所有 ORM 模型
确保 Alembic 能够自动检测到所有模型的元数据
"""

# 导入 Base（确保所有模型都继承自同一个 Base）
from app.db.session import Base

# 导入所有模型（必须在此导入，否则 Alembic autogenerate 无法检测）
from app.models.user import User
from app.models.trip import Trip, TripStop, TripStatus, StopStatus
from app.models.memory import Memory, MemorySource, MemoryType
from app.models.post import Post
from app.models.post_comment import PostComment
from app.models.post_like import PostLike

# 导出所有模型和枚举，方便其他模块使用
__all__ = [
    "Base",
    "User",
    "Trip",
    "TripStop",
    "TripStatus",
    "StopStatus",
    "Memory",
    "MemorySource",
    "MemoryType",
    "Post",
    "PostComment",
    "PostLike",
]
