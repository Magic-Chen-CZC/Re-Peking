"""
Posts API：社区分享接口
提供从行程创建分享、查询分享列表等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
import logging

from app.db.session import get_db
from app.models import Trip, TripStop, Memory, Post, MemorySource

router = APIRouter(prefix="/api/posts", tags=["posts"])

# 设置日志
logger = logging.getLogger("uvicorn.error")


# ============ Timezone 工具函数 ============

def now_utc() -> datetime:
    """
    返回当前 UTC 时间（timezone-aware）
    使用此函数替代 datetime.utcnow()，避免产生 naive datetime
    """
    return datetime.now(timezone.utc)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    确保 datetime 对象是 timezone-aware 的 UTC 时间
    
    Args:
        dt: datetime 对象或 None
    
    Returns:
        - 如果 dt 为 None，返回 None
        - 如果 dt 是 naive（无时区），假设为 UTC，添加 UTC 时区信息
        - 如果 dt 已有时区，转换为 UTC
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # Naive datetime，假设为 UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # 已有时区，转换为 UTC
        return dt.astimezone(timezone.utc)


# ============ Request/Response 模型 ============

class CreatePostFromTripRequest(BaseModel):
    """从行程创建分享请求"""
    trip_id: str = Field(description="行程 ID")
    user_openid: Optional[str] = Field(None, description="用户 OpenID（可选，如果提供则用于验证）")


class PostResponse(BaseModel):
    """分享响应"""
    id: str = Field(description="Post ID")
    trip_id: str = Field(description="行程 ID")
    user_id: str = Field(description="用户 ID")
    title: str = Field(description="分享标题")
    summary: Optional[str] = Field(None, description="行程摘要")
    cover_poi_id: Optional[str] = Field(None, description="封面 POI ID")
    created_at: datetime = Field(description="创建时间（UTC）")
    
    class Config:
        from_attributes = True


class CreatePostResponse(BaseModel):
    """创建分享响应"""
    post_id: str = Field(description="Post ID")
    trip_id: str = Field(description="行程 ID")
    title: str = Field(description="分享标题")
    created_at: datetime = Field(description="创建时间（UTC）")


# ============ 辅助函数 ============

def generate_post_title(trip: Trip, stops_count: int) -> str:
    """
    生成 Post 标题
    
    优先级：
    1. 如果 request_json 中有 selected_themes，拼接主题
    2. 否则使用默认格式：Trip · {n} stops
    
    Args:
        trip: Trip 对象
        stops_count: 站点数量
    
    Returns:
        生成的标题
    """
    # 尝试从 request_json 提取主题
    if trip.request_json and isinstance(trip.request_json, dict):
        themes = trip.request_json.get("selected_themes", [])
        if themes and isinstance(themes, list) and len(themes) > 0:
            # 拼接主题，例如：Historical & Cultural · 5 stops
            themes_str = " & ".join(themes[:3])  # 最多取前3个主题
            return f"{themes_str} · {stops_count} stops"
    
    # 默认标题
    return f"Trip · {stops_count} stops"


def generate_post_summary(db: Session, trip_id: UUID) -> Optional[str]:
    """
    生成 Post 摘要
    
    从 stops 的 ai_summary 或 memories 拼接生成摘要
    
    Args:
        db: 数据库会话
        trip_id: 行程 ID
    
    Returns:
        生成的摘要，如果没有内容则返回 None
    """
    summary_parts = []
    
    # 1. 获取所有 stops，尝试提取 ai_summary（假设存储在某个字段，这里需要根据实际情况调整）
    # 注意：当前 TripStop 模型中没有 ai_summary 字段，所以跳过这一步
    
    # 2. 获取所有 AI 生成的 memories（INSIGHT 类型）
    memories = db.query(Memory).filter(
        Memory.trip_id == trip_id,
        Memory.source == MemorySource.AI,
    ).order_by(Memory.created_at.desc()).limit(5).all()
    
    for memory in memories:
        if memory.content:
            summary_parts.append(memory.content.strip())
    
    # 3. 拼接摘要（最多取前3条，用 " · " 连接）
    if summary_parts:
        return " · ".join(summary_parts[:3])
    
    return None


def get_cover_poi_id(db: Session, trip_id: UUID) -> Optional[str]:
    """
    获取封面 POI ID
    
    默认取第一站的 poi_id
    
    Args:
        db: 数据库会话
        trip_id: 行程 ID
    
    Returns:
        封面 POI ID，如果没有站点则返回 None
    """
    first_stop = db.query(TripStop).filter(
        TripStop.trip_id == trip_id
    ).order_by(TripStop.seq.asc()).first()
    
    if first_stop:
        return first_stop.poi_id
    
    return None


# ============ API 端点 ============

@router.post("/from_trip", response_model=CreatePostResponse)
async def create_post_from_trip(
    request: CreatePostFromTripRequest,
    db: Session = Depends(get_db)
):
    """
    从行程创建分享
    
    # 验证方式
    curl -X POST http://localhost:8000/api/posts/from_trip \
      -H "Content-Type: application/json" \
      -d '{
        "trip_id": "your-trip-uuid",
        "user_openid": "optional-user-openid"
      }'
    
    Args:
        request: 创建请求
        db: 数据库会话
    
    Returns:
        创建的 Post 基本信息
    """
    logger.info(f"[create_post_from_trip] 开始创建分享，trip_id={request.trip_id}")
    
    try:
        trip_uuid = UUID(request.trip_id)
    except ValueError:
        logger.error(f"[create_post_from_trip] 无效的 trip_id: {request.trip_id}")
        raise HTTPException(status_code=400, detail="Invalid trip_id format")
    
    # 1. 校验 trip 存在
    trip = db.query(Trip).filter(Trip.id == trip_uuid).first()
    if not trip:
        logger.error(f"[create_post_from_trip] Trip 不存在: {request.trip_id}")
        raise HTTPException(status_code=404, detail=f"Trip not found: {request.trip_id}")
    
    logger.info(f"[create_post_from_trip] 找到 Trip，user_id={trip.user_id}, status={trip.status}")
    
    # 2. 获取 stops 数量
    stops_count = db.query(TripStop).filter(TripStop.trip_id == trip_uuid).count()
    logger.info(f"[create_post_from_trip] Trip 包含 {stops_count} 个 stops")
    
    # 3. 生成标题
    title = generate_post_title(trip, stops_count)
    logger.info(f"[create_post_from_trip] 生成标题: {title}")
    
    # 4. 生成摘要
    summary = generate_post_summary(db, trip_uuid)
    logger.info(f"[create_post_from_trip] 生成摘要: {summary}")
    
    # 5. 获取封面 POI ID
    cover_poi_id = get_cover_poi_id(db, trip_uuid)
    logger.info(f"[create_post_from_trip] 封面 POI ID: {cover_poi_id}")
    
    # 6. 创建 Post
    post = Post(
        trip_id=trip_uuid,
        user_id=trip.user_id,
        title=title,
        summary=summary,
        cover_poi_id=cover_poi_id,
        created_at=now_utc(),
        updated_at=now_utc()
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    logger.info(f"[create_post_from_trip] ✅ Post 创建成功，post_id={post.id}")
    
    # 7. 返回响应
    return CreatePostResponse(
        post_id=str(post.id),
        trip_id=str(post.trip_id),
        title=post.title,
        created_at=ensure_utc(post.created_at)
    )


@router.get("", response_model=List[PostResponse])
async def list_posts(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取分享列表（按创建时间倒序）
    
    # 验证方式
    curl http://localhost:8000/api/posts?limit=20
    
    Args:
        limit: 返回的最大数量（默认 20）
        db: 数据库会话
    
    Returns:
        Post 列表
    """
    logger.info(f"[list_posts] 查询分享列表，limit={limit}")
    
    # 查询 posts，按 created_at 降序排列
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()
    
    logger.info(f"[list_posts] ✅ 查询到 {len(posts)} 条分享")
    
    # 转换为响应格式
    result = []
    for post in posts:
        result.append(PostResponse(
            id=str(post.id),
            trip_id=str(post.trip_id),
            user_id=str(post.user_id),
            title=post.title,
            summary=post.summary,
            cover_poi_id=post.cover_poi_id,
            created_at=ensure_utc(post.created_at)
        ))
    
    return result
