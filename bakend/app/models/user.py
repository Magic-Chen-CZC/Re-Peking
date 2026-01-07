"""
User 模型：用户表
存储小程序用户的基本信息
"""
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    """用户表：存储小程序用户基本信息"""
    
    __tablename__ = "users"
    
    # 主键：使用 UUID 而非自增 ID，避免暴露用户数量
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="用户唯一标识"
    )
    
    # 微信 OpenID：必须唯一，用于登录态校验
    openid = Column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        comment="微信 OpenID（唯一）"
    )
    
    # 用户昵称：可空（用户可能未授权）
    nickname = Column(
        String(128),
        nullable=True,
        comment="用户昵称"
    )
    
    # 用户头像 URL：可空
    avatar = Column(
        String(512),
        nullable=True,
        comment="用户头像 URL"
    )
    
    # 创建时间：使用 timezone-aware，自动记录首次创建时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, openid={self.openid[:8]}***, nickname={self.nickname})>"
