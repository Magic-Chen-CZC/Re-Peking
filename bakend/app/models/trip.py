"""
Trip 模型：行程相关表
- Trip: 主行程表（一次完整的导览）
- TripStop: 行程站点表（一个行程包含多个站点）
"""
import uuid
import enum
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


# ============ 枚举定义 ============

class TripStatus(str, enum.Enum):
    """行程状态枚举"""
    DRAFT = "DRAFT"           # 草稿（规划中，未开始）
    ACTIVE = "ACTIVE"         # 进行中
    COMPLETED = "COMPLETED"   # 已完成
    ARCHIVED = "ARCHIVED"     # 已归档


class StopStatus(str, enum.Enum):
    """站点状态枚举"""
    UPCOMING = "UPCOMING"     # 未到达
    ARRIVED = "ARRIVED"       # 已到达（正在游览）
    COMPLETED = "COMPLETED"   # 已完成
    SKIPPED = "SKIPPED"       # 已跳过


# ============ ORM 模型 ============

class Trip(Base):
    """行程表：记录用户的一次完整导览"""
    
    __tablename__ = "trips"
    
    # 主键
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="行程唯一标识"
    )
    
    # 外键：关联用户
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属用户 ID"
    )
    
    # 行程状态
    status = Column(
        Enum(TripStatus, native_enum=False),
        nullable=False,
        default=TripStatus.DRAFT,
        index=True,
        comment="行程状态：DRAFT/ACTIVE/COMPLETED/ARCHIVED"
    )
    
    # 用户请求原始数据（JSONB 存储，便于查询和扩展）
    request_json = Column(
        JSONB,
        nullable=True,
        comment="用户请求 JSON（如兴趣、时间预算等）"
    )
    
    # LangGraph 运行 ID（用于追溯 LangSmith）
    run_id = Column(
        Text,
        nullable=True,
        comment="LangGraph run_id（可用于调试追踪）"
    )
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="最后更新时间"
    )
    
    # 关系：一个行程包含多个站点
    stops = relationship(
        "TripStop",
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripStop.seq"
    )
    
    def __repr__(self):
        return f"<Trip(id={self.id}, user_id={self.user_id}, status={self.status})>"


class TripStop(Base):
    """行程站点表：行程中的每一个景点/POI"""
    
    __tablename__ = "trip_stops"
    
    # 数据库约束：确保关键字段不为空字符串
    __table_args__ = (
        CheckConstraint(
            "length(trim(poi_id)) > 0",
            name="ck_trip_stops_poi_id_not_blank"
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_trip_stops_name_not_blank"
        ),
    )
    
    # 主键
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="站点唯一标识"
    )
    
    # 外键：关联行程
    trip_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属行程 ID"
    )
    
    # 站点顺序（1-based）
    seq = Column(
        Integer,
        nullable=False,
        comment="站点顺序（1-based，便于排序）"
    )
    
    # POI 信息
    poi_id = Column(
        Text,
        nullable=False,
        comment="POI ID（来自 mock_db 或外部数据源）"
    )
    
    name = Column(
        Text,
        nullable=False,
        comment="站点名称（如：故宫、颐和园）"
    )
    
    category = Column(
        Text,
        nullable=True,
        comment="站点分类（如：历史、自然、美食）"
    )
    
    # 距离上一站的距离（米）
    distance_m = Column(
        Integer,
        nullable=True,
        comment="距离上一站的距离（米）"
    )
    
    # 站点状态
    status = Column(
        Enum(StopStatus, native_enum=False),
        nullable=False,
        default=StopStatus.UPCOMING,
        comment="站点状态：UPCOMING/ARRIVED/COMPLETED/SKIPPED"
    )
    
    # 时间戳：到达时间 & 完成时间
    arrived_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="到达时间"
    )
    
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="完成时间"
    )
    
    # 关系：反向引用行程
    trip = relationship("Trip", back_populates="stops")
    
    def __repr__(self):
        return f"<TripStop(id={self.id}, trip_id={self.trip_id}, seq={self.seq}, name={self.name}, status={self.status})>"
