"""
Posts API：社区分享接口（V2 - 支持编辑后再分享）
提供创建分享、查询分享列表、查询分享详情等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID, uuid4
import logging

# 🔥 创建 router（必须在所有导入之前，确保即使数据库导入失败也能导出 router）
router = APIRouter(prefix="/api/posts", tags=["posts"])

# 设置日志
logger = logging.getLogger("uvicorn.error")

# 导入数据库依赖（如果失败，使用种子数据兜底）
try:
    from app.db.session import get_db
    from app.models import Trip, TripStop, Post, User, PostComment, PostLike, Memory, MemorySource, MemoryType
    DB_AVAILABLE = True
    logger.info("✅ Database imports successful")
except Exception as e:
    logger.warning(f"⚠️ Database imports failed, will use seed data: {e}")
    DB_AVAILABLE = False
    get_db = None
    Trip = None
    TripStop = None
    Post = None
    User = None
    PostComment = None
    PostLike = None
    Memory = None
    MemorySource = None
    MemoryType = None


# ============ 种子数据（数据库不可用时使用） ============

SEED_POSTS = [
    {
        "id": "seed-post-001",
        "trip_id": "seed-trip-001",
        "user_id": "seed-user-001",
        "title": "故宫深度游记 · 5个景点",
        "reflection": "在故宫的每一步都是历史的回响，太和殿的壮观让我印象深刻。建议早上8点前入园，可以避开人流高峰，更好地感受皇家建筑的宏伟气势。",
        "cover_poi_id": "gugong",
        "cover_image_url": None,
        "manifest_json": {
            "trip_id": "seed-trip-001",
            "status": "COMPLETED",
            "total_stops": 5,
            "stops": [
                {
                    "seq": 1,
                    "poi_id": "gugong",
                    "name": "故宫博物院",
                    "status": "VISITED",
                    "lat": 39.9163,
                    "lon": 116.3972,
                    "user_logs": ["太和殿非常壮观", "建议早上去人少"],
                    "ai_summary": "明清两代的皇家宫殿"
                }
            ]
        },
        "created_at": "2024-01-05T08:00:00+00:00",
        "updated_at": "2024-01-05T08:00:00+00:00"
    },
    {
        "id": "seed-post-002",
        "trip_id": "seed-trip-002",
        "user_id": "seed-user-002",
        "title": "天坛文化之旅 · 4个景点",
        "reflection": "天坛的建筑设计体现了古人的智慧，回音壁的声学效果令人惊叹。推荐下午去，光线很好适合拍照，而且可以看到很多当地人在这里锻炼、唱歌。",
        "cover_poi_id": "tiantan",
        "cover_image_url": None,
        "manifest_json": {
            "trip_id": "seed-trip-002",
            "status": "COMPLETED",
            "total_stops": 4,
            "stops": [
                {
                    "seq": 1,
                    "poi_id": "tiantan",
                    "name": "天坛",
                    "status": "VISITED",
                    "lat": 39.8823,
                    "lon": 116.4068,
                    "user_logs": ["回音壁效果很棒", "下午光线好"],
                    "ai_summary": "明清帝王祭天的场所"
                }
            ]
        },
        "created_at": "2024-01-04T14:30:00+00:00",
        "updated_at": "2024-01-04T14:30:00+00:00"
    },
    {
        "id": "seed-post-003",
        "trip_id": "seed-trip-003",
        "user_id": "seed-user-003",
        "title": "颐和园半日游 · 3个景点",
        "reflection": "颐和园的湖光山色美不胜收，长廊的彩绘值得细细品味。建议预留至少3小时游览，春秋季节来最合适，可以划船游湖。",
        "cover_poi_id": "yiheyuan",
        "cover_image_url": None,
        "manifest_json": {
            "trip_id": "seed-trip-003",
            "status": "COMPLETED",
            "total_stops": 3,
            "stops": [
                {
                    "seq": 1,
                    "poi_id": "yiheyuan",
                    "name": "颐和园",
                    "status": "VISITED",
                    "lat": 39.9998,
                    "lon": 116.2754,
                    "user_logs": ["长廊彩绘很精美", "可以划船"],
                    "ai_summary": "清代皇家园林"
                }
            ]
        },
        "created_at": "2024-01-03T10:00:00+00:00",
        "updated_at": "2024-01-03T10:00:00+00:00"
    },
    {
        "id": "seed-post-004",
        "trip_id": "seed-trip-004",
        "user_id": "seed-user-004",
        "title": "长城一日游 · 八达岭段",
        "reflection": "不到长城非好汉！八达岭长城虽然游客很多，但站在城墙上俯瞰群山还是很震撼。建议带足水和零食，爬城墙很消耗体力。",
        "cover_poi_id": "badaling",
        "cover_image_url": None,
        "manifest_json": {
            "trip_id": "seed-trip-004",
            "status": "COMPLETED",
            "total_stops": 2,
            "stops": [
                {
                    "seq": 1,
                    "poi_id": "badaling",
                    "name": "八达岭长城",
                    "status": "VISITED",
                    "lat": 40.3592,
                    "lon": 116.0155,
                    "user_logs": ["很震撼", "体力消耗大"],
                    "ai_summary": "明长城最具代表性的一段"
                }
            ]
        },
        "created_at": "2024-01-02T09:00:00+00:00",
        "updated_at": "2024-01-02T09:00:00+00:00"
    },
    {
        "id": "seed-post-005",
        "trip_id": "seed-trip-005",
        "user_id": "seed-user-005",
        "title": "南锣鼓巷胡同游 · 老北京味道",
        "reflection": "南锣鼓巷保留了很多老北京的风貌，胡同里有很多有特色的小店和咖啡馆。推荐傍晚来，可以感受胡同的夜生活，还能吃到地道的北京小吃。",
        "cover_poi_id": "nanluoguxiang",
        "cover_image_url": None,
        "manifest_json": {
            "trip_id": "seed-trip-005",
            "status": "COMPLETED",
            "total_stops": 2,
            "stops": [
                {
                    "seq": 1,
                    "poi_id": "nanluoguxiang",
                    "name": "南锣鼓巷",
                    "status": "VISITED",
                    "lat": 39.9371,
                    "lon": 116.4023,
                    "user_logs": ["特色小店很多", "北京小吃"],
                    "ai_summary": "保存完好的四合院胡同区"
                }
            ]
        },
        "created_at": "2024-01-01T16:00:00+00:00",
        "updated_at": "2024-01-01T16:00:00+00:00"
    }
]


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

class CreatePostRequest(BaseModel):
    """创建分享请求"""
    trip_id: str = Field(description="行程 ID")
    title: str = Field(default="", description="分享标题（用户可编辑）")
    reflection: Optional[str] = Field(None, description="用户感想/反思（可选）")
    cover_image_url: Optional[str] = Field(None, description="封面图片 URL（用户上传，可选）")
    cover_poi_id: Optional[str] = Field(None, description="封面 POI ID（备选封面，可选）")


class CreatePostResponse(BaseModel):
    """创建分享响应"""
    post_id: str = Field(description="Post ID")
    trip_id: str = Field(description="行程 ID")
    title: str = Field(description="分享标题")
    cover_image_url: Optional[str] = Field(None, description="封面图片 URL")
    created_at: datetime = Field(description="创建时间（UTC）")


class PostListItemResponse(BaseModel):
    """分享列表项响应（不包含 manifest_json）"""
    id: str = Field(description="Post ID")
    trip_id: str = Field(description="行程 ID")
    title: str = Field(description="分享标题")
    reflection: Optional[str] = Field(None, description="用户感想/反思")
    cover_image_url: Optional[str] = Field(None, description="封面图片 URL")
    cover_poi_id: Optional[str] = Field(None, description="封面 POI ID")
    comments_count: int = Field(default=0, description="评论数量")
    likes_count: int = Field(default=0, description="点赞数量")
    created_at: datetime = Field(description="创建时间（UTC）")


class CommentCreateRequest(BaseModel):
    """创建评论请求"""
    user_openid: str = Field(description="用户 OpenID")
    content: str = Field(description="评论内容")


class CommentResponse(BaseModel):
    """评论响应"""
    id: str
    user_id: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LikeResponse(BaseModel):
    """点赞响应"""
    liked: bool
    likes_count: int


class PostDetailResponse(BaseModel):
    """分享详情响应（包含 manifest_json）"""
    id: str = Field(description="Post ID")
    trip_id: str = Field(description="行程 ID")
    user_id: str = Field(description="用户 ID")
    title: str = Field(description="分享标题")
    reflection: Optional[str] = Field(None, description="用户感想/反思")
    cover_image_url: Optional[str] = Field(None, description="封面图片 URL")
    cover_poi_id: Optional[str] = Field(None, description="封面 POI ID")
    manifest_json: Dict[str, Any] = Field(description="Trip 快照（stops 详情）")
    comments: List[CommentResponse] = Field(default_factory=list, description="评论列表")
    comments_count: int = Field(default=0, description="评论数量")
    likes_count: int = Field(default=0, description="点赞数量")
    user_liked: bool = Field(default=False, description="当前用户是否已点赞")
    created_at: datetime = Field(description="创建时间（UTC）")
    updated_at: datetime = Field(description="最后更新时间（UTC）")


# ============ 辅助函数 ============

def resolve_poi_latlon(poi_id: str) -> tuple[float | None, float | None]:
    """
    根据 POI ID 查询经纬度坐标
    
    优先级：
    1. app.data.pois.POIS_DB
    2. app.services.mock_db.MOCK_DB (fallback)
    3. 如果都找不到，返回 (None, None)
    
    Args:
        poi_id: POI ID
    
    Returns:
        (lat, lon) 元组，找不到时返回 (None, None)
    """
    try:
        # 优先从 pois.py 的 POIS_DB 查询
        from app.data.pois import get_poi_by_id
        poi = get_poi_by_id(poi_id)
        if poi:
            return (poi.lat, poi.lon)
        
        # Fallback: 尝试从 mock_db.py 的 MOCK_DB 查询
        try:
            from app.services.mock_db import MOCK_DB
            for mock_poi in MOCK_DB:
                if mock_poi.id == poi_id:
                    return (mock_poi.lat, mock_poi.lon)
        except Exception as e:
            logger.warning(f"[resolve_poi_latlon] 无法访问 MOCK_DB: {e}")
        
        # 都找不到
        logger.warning(f"[resolve_poi_latlon] POI not found: {poi_id}")
        return (None, None)
    
    except Exception as e:
        logger.error(f"[resolve_poi_latlon] 查询 POI 坐标失败: {e}")
        return (None, None)


def get_or_create_user(db: Session, user_openid: str) -> User:
    """获取或创建用户"""
    user = db.query(User).filter(User.openid == user_openid).first()
    if not user:
        user = User(openid=user_openid)
        db.add(user)
        db.flush()
    return user


def get_post_comments(db: Session, post_id: UUID, limit: int = 50) -> List[PostComment]:
    return db.query(PostComment).filter(
        PostComment.post_id == post_id
    ).order_by(PostComment.created_at.asc()).limit(limit).all()


def get_post_counts(db: Session, post_id: UUID) -> tuple[int, int]:
    comments_count = db.query(func.count(PostComment.id)).filter(PostComment.post_id == post_id).scalar() or 0
    likes_count = db.query(func.count(PostLike.id)).filter(PostLike.post_id == post_id).scalar() or 0
    return comments_count, likes_count


def generate_manifest_json(db: Session, trip_id: UUID) -> Dict[str, Any]:
    """
    生成 Trip 快照（manifest_json）
    
    包含 trip 的 COMPLETED stops 信息：
    - stop_id, seq, poi_id, name, category, status
    - arrived_at, completed_at (ISO string)
    - lat, lon (通过 resolve_poi_latlon 从 POI 数据源查询)
    - user_logs, ai_summary (暂时为空，等待后续实现)
    
    Args:
        db: 数据库会话
        trip_id: 行程 ID
    
    Returns:
        manifest_json 字典
    
    Raises:
        HTTPException: 如果没有 COMPLETED stops
    """
    logger.info(f"[generate_manifest_json] 生成 trip_id={trip_id} 的快照")
    
    # 查询 trip
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise ValueError(f"Trip not found: {trip_id}")
    
    # 查询所有 stops（按 seq 排序）
    all_stops = db.query(TripStop).filter(
        TripStop.trip_id == trip_id
    ).order_by(TripStop.seq.asc()).all()
    
    logger.info(f"[generate_manifest_json] 找到 {len(all_stops)} 个 stops")
    
    # 🔥 只保留 COMPLETED stops
    from app.models.trip import StopStatus
    completed_stops = [s for s in all_stops if s.status == StopStatus.COMPLETED]
    
    logger.info(f"[generate_manifest_json] 其中 COMPLETED stops: {len(completed_stops)} 个")
    
    # 🔥 如果没有 COMPLETED stops，抛出 400 错误
    if len(completed_stops) == 0:
        logger.warning(f"[generate_manifest_json] Trip {trip_id} 没有 COMPLETED stops")
        raise HTTPException(
            status_code=400,
            detail="请先完成至少一个景点的游览，才能分享到社区哦！"
        )
    
    # 获取 trip 标题（从 request_json 中提取）
    trip_title = "我的旅程"
    if trip.request_json and isinstance(trip.request_json, dict):
        trip_title = trip.request_json.get("selected_route_name") or trip_title
    
    # 预加载记忆点（用户笔记 + AI 洞察）
    memories = db.query(Memory).filter(
        Memory.trip_id == trip_id
    ).order_by(Memory.created_at).all()

    stop_memories_map: Dict[Any, Dict[str, List[Dict[str, Any]]]] = {}
    for mem in memories:
        if mem.stop_id:
            if mem.stop_id not in stop_memories_map:
                stop_memories_map[mem.stop_id] = {"user_notes": [], "ai_insights": []}
            if mem.source == MemorySource.USER and mem.type == MemoryType.NOTE:
                stop_memories_map[mem.stop_id]["user_notes"].append({
                    "content": mem.content,
                    "created_at": mem.created_at
                })
            elif mem.source == MemorySource.AI and mem.type == MemoryType.INSIGHT:
                stop_memories_map[mem.stop_id]["ai_insights"].append({
                    "content": mem.content,
                    "created_at": mem.created_at
                })

    # 构造 manifest
    manifest = {
        "trip_id": str(trip_id),
        "title": trip_title,
        "status": trip.status.value if hasattr(trip.status, 'value') else str(trip.status),
        "total_stops": len(completed_stops),
        "stops": []
    }
    
    for stop in completed_stops:
        # 🔥 通过 resolve_poi_latlon 从 POI 数据源获取坐标（不访问 stop.lat/stop.lon）
        lat, lon = resolve_poi_latlon(stop.poi_id)
        
        mem_data = stop_memories_map.get(stop.id, {"user_notes": [], "ai_insights": []})

        user_notes = sorted(mem_data["user_notes"], key=lambda x: x["created_at"])
        ai_insights = sorted(mem_data["ai_insights"], key=lambda x: x["created_at"], reverse=True)

        # 🔥 构造 stop 数据（所有字段序列化为 JSON 兼容类型）
        stop_data = {
            "stop_id": str(stop.id),
            "seq": stop.seq,
            "poi_id": stop.poi_id,
            "name": stop.name,
            "category": stop.category,
            "status": stop.status.value if hasattr(stop.status, 'value') else str(stop.status),
            "lat": lat,  # float or None
            "lon": lon,  # float or None
            "arrived_at": stop.arrived_at.isoformat() if stop.arrived_at else None,
            "completed_at": stop.completed_at.isoformat() if stop.completed_at else None,
            "user_logs": [note["content"] for note in user_notes],
            "ai_summary": ai_insights[0]["content"] if ai_insights else None
        }
        manifest["stops"].append(stop_data)
    
    logger.info(f"[generate_manifest_json] ✅ 快照生成成功，包含 {len(manifest['stops'])} 个 COMPLETED stops")
    
    return manifest


# ============ API 端点 ============

@router.get("", response_model=List[PostListItemResponse])
async def list_posts(
    limit: int = 20,
    db: Session = Depends(get_db) if DB_AVAILABLE else None
):
    """
    获取分享列表（按创建时间倒序）
    
    默认不返回 manifest_json（太大），只返回基本信息
    
    Args:
        limit: 返回的最大数量（默认 20）
        db: 数据库会话
    
    Returns:
        Post 列表
    """
    logger.info(f"[list_posts] 查询分享列表，limit={limit}")
    
    # 🔥 如果数据库不可用，使用种子数据
    if not DB_AVAILABLE or db is None:
        logger.warning("[list_posts] ⚠️ 数据库不可用，使用种子数据")
        result = []
        for seed_post in SEED_POSTS[:limit]:
            result.append(PostListItemResponse(
                id=seed_post["id"],
                trip_id=seed_post["trip_id"],
                title=seed_post["title"],
                reflection=seed_post["reflection"],
                cover_image_url=seed_post["cover_image_url"],
                cover_poi_id=seed_post["cover_poi_id"],
                comments_count=0,
                likes_count=0,
                created_at=datetime.fromisoformat(seed_post["created_at"])
            ))
        logger.info(f"[list_posts] ✅ 返回 {len(result)} 条种子数据")
        return result
    
    # 查询 posts，按 created_at 降序排列
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()
    
    logger.info(f"[list_posts] ✅ 查询到 {len(posts)} 条分享")
    
    # 转换为响应格式（不包含 manifest_json）
    result = []
    for post in posts:
        comments_count, likes_count = get_post_counts(db, post.id)
        result.append(PostListItemResponse(
            id=str(post.id),
            trip_id=str(post.trip_id),
            title=post.title,
            reflection=post.reflection,
            cover_image_url=post.cover_image_url,
            cover_poi_id=post.cover_poi_id,
            comments_count=comments_count,
            likes_count=likes_count,
            created_at=ensure_utc(post.created_at)
        ))
    
    return result


@router.get("/{post_id}", response_model=PostDetailResponse)
async def get_post_detail(
    post_id: str,
    user_openid: Optional[str] = None,
    db: Session = Depends(get_db) if DB_AVAILABLE else None
):
    """
    获取分享详情（包含 manifest_json）
    
    Args:
        post_id: Post ID
        db: 数据库会话
    
    Returns:
        Post 详情（包含 manifest_json）
    """
    logger.info(f"[get_post_detail] 查询分享详情，post_id={post_id}")
    
    # 🔥 如果数据库不可用，使用种子数据
    if not DB_AVAILABLE or db is None:
        logger.warning("[get_post_detail] ⚠️ 数据库不可用，使用种子数据")
        
        # 从种子数据中查找
        seed_post = next((p for p in SEED_POSTS if p["id"] == post_id), None)
        
        if not seed_post:
            logger.error(f"[get_post_detail] 种子数据中未找到 post_id={post_id}")
            raise HTTPException(status_code=404, detail=f"Post not found: {post_id}")
        
        logger.info(f"[get_post_detail] ✅ 找到种子 Post，title={seed_post['title']}")
        
        return PostDetailResponse(
            id=seed_post["id"],
            trip_id=seed_post["trip_id"],
            user_id=seed_post["user_id"],
            title=seed_post["title"],
            reflection=seed_post["reflection"],
            cover_image_url=seed_post["cover_image_url"],
            cover_poi_id=seed_post["cover_poi_id"],
            manifest_json=seed_post["manifest_json"],
            comments=[],
            comments_count=0,
            likes_count=0,
            user_liked=False,
            created_at=datetime.fromisoformat(seed_post["created_at"]),
            updated_at=datetime.fromisoformat(seed_post["updated_at"])
        )
    
    try:
        post_uuid = UUID(post_id)
    except ValueError:
        logger.error(f"[get_post_detail] 无效的 post_id: {post_id}")
        raise HTTPException(status_code=400, detail="Invalid post_id format")
    
    # 查询 post
    post = db.query(Post).filter(Post.id == post_uuid).first()
    if not post:
        logger.error(f"[get_post_detail] Post 不存在: {post_id}")
        raise HTTPException(status_code=404, detail=f"Post not found: {post_id}")
    
    logger.info(f"[get_post_detail] ✅ 找到 Post，trip_id={post.trip_id}, title={post.title}")
    
    comments = get_post_comments(db, post_uuid, limit=50)
    comments_count, likes_count = get_post_counts(db, post_uuid)
    user_liked = False
    if user_openid:
        user = db.query(User).filter(User.openid == user_openid).first()
        if user:
            liked = db.query(PostLike).filter(
                PostLike.post_id == post_uuid,
                PostLike.user_id == user.id
            ).first()
            user_liked = liked is not None

    # 返回完整信息（包含 manifest_json）
    return PostDetailResponse(
        id=str(post.id),
        trip_id=str(post.trip_id),
        user_id=str(post.user_id),
        title=post.title,
        reflection=post.reflection,
        cover_image_url=post.cover_image_url,
        cover_poi_id=post.cover_poi_id,
        manifest_json=post.manifest_json,
        comments=[
            CommentResponse(
                id=str(c.id),
                user_id=str(c.user_id),
                content=c.content,
                created_at=ensure_utc(c.created_at)
            ) for c in comments
        ],
        comments_count=comments_count,
        likes_count=likes_count,
        user_liked=user_liked,
        created_at=ensure_utc(post.created_at),
        updated_at=ensure_utc(post.updated_at)
    )


@router.post("/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: str,
    payload: CommentCreateRequest,
    db: Session = Depends(get_db) if DB_AVAILABLE else None
):
    if not DB_AVAILABLE or db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        post_uuid = UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post_id format")

    post = db.query(Post).filter(Post.id == post_uuid).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="评论内容不能为空")

    user = get_or_create_user(db, payload.user_openid)
    comment = PostComment(
        post_id=post.id,
        user_id=user.id,
        content=payload.content.strip()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=str(comment.id),
        user_id=str(comment.user_id),
        content=comment.content,
        created_at=ensure_utc(comment.created_at)
    )


@router.post("/{post_id}/likes", response_model=LikeResponse)
async def like_post(
    post_id: str,
    user_openid: str,
    db: Session = Depends(get_db) if DB_AVAILABLE else None
):
    if not DB_AVAILABLE or db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        post_uuid = UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post_id format")

    post = db.query(Post).filter(Post.id == post_uuid).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    user = get_or_create_user(db, user_openid)
    like = PostLike(post_id=post.id, user_id=user.id)
    db.add(like)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()

    _, likes_count = get_post_counts(db, post.id)
    return LikeResponse(liked=True, likes_count=likes_count)


@router.delete("/{post_id}/likes", response_model=LikeResponse)
async def unlike_post(
    post_id: str,
    user_openid: str,
    db: Session = Depends(get_db) if DB_AVAILABLE else None
):
    if not DB_AVAILABLE or db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        post_uuid = UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post_id format")

    post = db.query(Post).filter(Post.id == post_uuid).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    user = db.query(User).filter(User.openid == user_openid).first()
    if user:
        db.query(PostLike).filter(
            PostLike.post_id == post.id,
            PostLike.user_id == user.id
        ).delete()
        db.commit()

    _, likes_count = get_post_counts(db, post.id)
    return LikeResponse(liked=False, likes_count=likes_count)


@router.post("", response_model=CreatePostResponse)
async def create_post(
    request: CreatePostRequest,
    db: Session = Depends(get_db) if DB_AVAILABLE else None
):
    """
    创建社区分享
    
    用户编辑标题、感想、封面后发布到社区
    
    Args:
        request: 创建请求
        db: 数据库会话
    
    Returns:
        创建的 Post 基本信息
    """
    logger.info(f"[create_post] 开始创建分享，trip_id={request.trip_id}, title={request.title}")
    
    # 🔥 如果数据库不可用，返回错误
    if not DB_AVAILABLE or db is None:
        logger.error("[create_post] ❌ 数据库不可用，无法创建分享")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Cannot create posts at this time. Please check DATABASE_URL configuration."
        )
    
    try:
        trip_uuid = UUID(request.trip_id)
    except ValueError:
        logger.error(f"[create_post] 无效的 trip_id: {request.trip_id}")
        raise HTTPException(status_code=400, detail="Invalid trip_id format")
    
    # 1. 验证 trip 存在
    trip = db.query(Trip).filter(Trip.id == trip_uuid).first()
    if not trip:
        logger.error(f"[create_post] Trip 不存在: {request.trip_id}")
        raise HTTPException(status_code=404, detail=f"Trip not found: {request.trip_id}")
    
    logger.info(f"[create_post] 找到 Trip，user_id={trip.user_id}, status={trip.status}")
    
    # 2. 生成 manifest_json（trip 快照）
    # 🔥 这里会自动校验是否有 COMPLETED stops，没有则抛出 400
    try:
        manifest_json = generate_manifest_json(db, trip_uuid)
        logger.info(f"[create_post] manifest_json 生成成功，包含 {manifest_json['total_stops']} 个 COMPLETED stops")
    except HTTPException as e:
        # 🔥 重新抛出 HTTPException（如 400: 没有 COMPLETED stops）
        logger.error(f"[create_post] HTTPException: {e.detail}")
        raise
    except Exception as e:
        # 🔥 其他异常统一处理
        logger.error(f"[create_post] 生成 manifest_json 失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成 trip 快照失败: {str(e)}"
        )
    
    # 3. 创建 Post
    try:
        post = Post(
            trip_id=trip_uuid,
            user_id=trip.user_id,
            title=request.title or "",
            reflection=request.reflection,
            cover_image_url=request.cover_image_url,
            cover_poi_id=request.cover_poi_id,
            manifest_json=manifest_json,
            created_at=now_utc(),
            updated_at=now_utc()
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        logger.info(f"[create_post] ✅ Post 创建成功，post_id={post.id}")
    except Exception as e:
        logger.error(f"[create_post] 创建 Post 失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"创建分享失败: {str(e)}"
        )
    
    # 4. 返回响应
    return CreatePostResponse(
        post_id=str(post.id),
        trip_id=str(post.trip_id),
        title=post.title,
        cover_image_url=post.cover_image_url,
        created_at=ensure_utc(post.created_at)
    )
