"""
PostComment 模型：社区评论
"""
import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base


class PostComment(Base):
    """社区评论表：存储用户对 Post 的评论"""

    __tablename__ = "post_comments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="评论唯一标识"
    )

    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联的 Post ID"
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="评论用户 ID"
    )

    content = Column(
        Text,
        nullable=False,
        comment="评论内容"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间（UTC）"
    )

    def __repr__(self):
        return f"<PostComment(id={self.id}, post_id={self.post_id})>"
