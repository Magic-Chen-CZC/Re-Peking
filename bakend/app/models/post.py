"""
Post 模型：社区分享表
用于存储用户分享的行程到社区（支持编辑后再分享）
"""
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from app.db.session import Base


# ============ ORM 模型 ============

class Post(Base):
    """
    社区分享表：存储用户分享的行程
    - 用户可以编辑标题、感想、封面后再分享
    - post 包含 trip 快照（manifest_json），独立于原 trip
    """
    
    __tablename__ = "posts"
    
    # 主键
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Post 唯一标识"
    )
    
    # 关联行程
    trip_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="关联的行程 ID（原始 trip）"
    )
    
    # 关联用户
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="发布用户 ID（从 trips.user_id 获取）"
    )
    
    # 标题（用户可编辑）
    title = Column(
        String(500),
        nullable=False,
        default="",
        comment="分享标题（用户可编辑，默认为空字符串）"
    )
    
    # 感想/反思（用户可编辑）
    reflection = Column(
        Text,
        nullable=True,
        comment="用户对行程的感想/反思（可选）"
    )
    
    # 封面图片 URL（用户上传）
    cover_image_url = Column(
        String(1000),
        nullable=True,
        comment="封面图片 URL（用户上传的图片，可选）"
    )
    
    # 封面 POI ID（备选封面）
    cover_poi_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="封面 POI ID（备选封面，如果没有上传图片则使用）"
    )
    
    # Trip 快照（JSON）
    manifest_json = Column(
        JSON,
        nullable=False,
        comment="Trip 快照（stops: seq/poi_id/name/status/lat/lon/user_logs/ai_summary），发布时冻结"
    )
    
    # 时间戳（timezone-aware，统一使用 UTC）
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间（UTC）"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="最后更新时间（UTC）"
    )
    
    def __repr__(self):
        return f"<Post(id={self.id}, trip_id={self.trip_id}, title={self.title[:30]})>"
