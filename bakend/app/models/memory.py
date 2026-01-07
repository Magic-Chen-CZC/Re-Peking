"""
Memory 模型：行程记忆表
用于存储用户在行程中的笔记、AI 生成的洞察等
"""
import uuid
import enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.session import Base


# ============ 枚举定义 ============

class MemorySource(str, enum.Enum):
    """记忆来源枚举"""
    USER = "USER"  # 用户输入（笔记、评论等）
    AI = "AI"      # AI 生成（洞察、推荐等）


class MemoryType(str, enum.Enum):
    """记忆类型枚举"""
    NOTE = "NOTE"        # 笔记/备注
    INSIGHT = "INSIGHT"  # 洞察/反思


# ============ ORM 模型 ============

class Memory(Base):
    """
    记忆表：存储行程中的笔记和 AI 洞察
    - 可以关联到整个行程（stop_id 为空）
    - 也可以关联到具体站点（stop_id 非空）
    """
    
    __tablename__ = "memories"
    
    # 主键
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="记忆唯一标识"
    )
    
    # 外键：关联行程（必须）
    trip_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属行程 ID"
    )
    
    # 外键：关联站点（可选，如果是行程级别记忆则为空）
    stop_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trip_stops.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="关联站点 ID（可选）"
    )
    
    # 记忆来源
    source = Column(
        Enum(MemorySource, native_enum=False),
        nullable=False,
        comment="记忆来源：USER/AI"
    )
    
    # 记忆类型
    type = Column(
        Enum(MemoryType, native_enum=False),
        nullable=False,
        comment="记忆类型：NOTE/INSIGHT"
    )
    
    # 记忆内容
    content = Column(
        Text,
        nullable=False,
        comment="记忆内容（文本）"
    )
    
    # 元数据（JSONB 存储扩展信息，如图片 URL、标签等）
    meta_json = Column(
        JSONB,
        nullable=True,
        comment="元数据 JSON（如图片、标签、情感分析结果等）"
    )
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    def __repr__(self):
        return f"<Memory(id={self.id}, trip_id={self.trip_id}, source={self.source}, type={self.type})>"
