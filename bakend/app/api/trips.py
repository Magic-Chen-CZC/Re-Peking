"""
Trips API：行程管理接口
提供创建行程、查询行程详情、更新站点状态、添加记忆等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from app.db.session import get_db
from app.models import (
    User, Trip, TripStop, Memory,
    TripStatus, StopStatus, MemorySource, MemoryType
)

router = APIRouter(prefix="/api", tags=["trips"])


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

class StopInput(BaseModel):
    """站点输入（用于创建行程）"""
    seq: int = Field(description="站点顺序（1-based）")
    poi_id: str = Field(description="POI ID")
    name: str = Field(description="站点名称")
    category: Optional[str] = Field(None, description="站点分类")
    distance_m: Optional[int] = Field(None, description="距离上一站的距离（米）")


class CreateTripRequest(BaseModel):
    """创建行程请求"""
    user_openid: str = Field(description="用户 OpenID")
    request_json: Dict[str, Any] = Field(description="用户请求 JSON（themes/time_budget/transportation/pace 等）")
    plan: Dict[str, Any] = Field(description="规划结果（来自 /api/plan 的 plan_dict，包含 stops 数组）")
    run_id: Optional[str] = Field(None, description="LangGraph run_id")


class StopCreatedResponse(BaseModel):
    """创建后的站点响应（含数据库生成的 stop_id）"""
    stop_id: str
    seq: int
    poi_id: str
    name: str
    lat: float
    lon: float
    status: str


class CreateTripResponse(BaseModel):
    """创建行程响应"""
    trip_id: str = Field(description="行程 ID")
    stops: List[StopCreatedResponse] = Field(description="已创建的站点列表（含 stop_id）")
    plan: Optional[Dict[str, Any]] = Field(None, description="原始 plan（可选返回）")


class StopResponse(BaseModel):
    """站点响应（所有 ID 字段使用 str 类型，确保 JSON 序列化兼容）"""
    id: str
    seq: int
    poi_id: str
    name: str
    category: Optional[str]
    distance_m: Optional[int]
    status: str
    arrived_at: Optional[datetime]
    completed_at: Optional[datetime]
    lat: Optional[float] = Field(None, description="纬度")
    lon: Optional[float] = Field(None, description="经度")

    model_config = {"from_attributes": True}


class StopResponseWithMemories(BaseModel):
    """站点响应（含聚合的记忆字段，所有 ID 字段使用 str 类型）"""
    id: str
    seq: int
    poi_id: str
    name: str
    category: Optional[str]
    distance_m: Optional[int]
    status: str
    arrived_at: Optional[datetime]
    completed_at: Optional[datetime]
    lat: Optional[float] = Field(None, description="纬度")
    lon: Optional[float] = Field(None, description="经度")
    user_logs: List[str] = Field(default_factory=list, description="用户笔记列表")
    ai_summary: Optional[str] = Field(None, description="AI 洞察（最新一条）")

    model_config = {"from_attributes": True}


class MemoryResponse(BaseModel):
    """记忆响应（所有 ID 字段使用 str 类型）"""
    id: str
    stop_id: Optional[str]
    source: str
    type: str
    content: str
    meta_json: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}


class TripDetailResponse(BaseModel):
    """行程详情响应"""
    trip: Dict[str, Any]
    stops: List[StopResponseWithMemories]
    memories: List[MemoryResponse]


class CreateMemoryRequest(BaseModel):
    """创建记忆请求"""
    stop_id: Optional[str] = Field(None, description="关联站点 ID（可选）")
    source: MemorySource = Field(description="记忆来源：USER/AI")
    type: MemoryType = Field(description="记忆类型：NOTE/INSIGHT")
    content: str = Field(description="记忆内容")
    meta: Optional[Dict[str, Any]] = Field(None, description="元数据（可选）")


class CreateStopMemoryRequest(BaseModel):
    """为站点创建记忆请求（简化版）
    
    支持两种格式：
    1. 组合格式：source + type（如 source="USER", type="NOTE"）
    2. 简化格式：type 直接为 "USER_NOTE" 或 "AI_INSIGHT"
    """
    source: Optional[str] = Field(None, description="记忆来源：USER/AI（可选，如果 type 已包含来源信息）")
    type: str = Field(
        description="记忆类型：支持 'NOTE'/'INSIGHT'（配合 source）或 'USER_NOTE'/'AI_INSIGHT'（独立使用）",
        examples=["USER_NOTE", "AI_INSIGHT", "NOTE", "INSIGHT"]
    )
    text: str = Field(description="记忆内容")


class StopCompleteResponse(BaseModel):
    """完成站点响应"""
    stop: StopResponse
    ai_summary: Optional[str] = Field(None, description="AI 生成的洞察")


class CreateStopMemoryResponse(BaseModel):
    """创建站点记忆响应"""
    id: str
    stop_id: str
    type: str
    text: str
    created_at: datetime


class TripHistoryStop(BaseModel):
    """历史行程中的站点摘要"""
    seq: int
    poi_id: str
    name: str
    user_logs: List[str] = Field(default_factory=list)
    ai_summary: Optional[str] = None


class TripHistoryItem(BaseModel):
    """历史行程摘要"""
    trip_id: str
    title: str
    created_at: datetime
    stops: List[TripHistoryStop]


# ============ API 端点 ============

@router.post("/trips", response_model=CreateTripResponse)
def create_trip(
    req: CreateTripRequest,
    db: Session = Depends(get_db)
):
    """
    创建新行程
    1. 根据 openid 查找或创建用户
    2. 创建 Trip 记录（状态为 DRAFT）
    3. 从 plan["stops"] 创建所有 TripStop（状态为 UPCOMING）
    4. 返回 trip_id + stops（含数据库生成的 stop_id）
    
    注意：如果 plan["stops"] 中的 stop 没有 seq 字段，后端会自动按数组顺序生成（从 1 开始）
    """
    # 1. 查找或创建用户
    user = db.query(User).filter(User.openid == req.user_openid).first()
    if not user:
        # 用户不存在，创建新用户（昵称和头像为空，后续可更新）
        user = User(openid=req.user_openid)
        db.add(user)
        db.flush()  # 确保 user.id 可用
    
    # 2. 创建行程
    trip = Trip(
        user_id=user.id,
        status=TripStatus.DRAFT,
        request_json=req.request_json,
        run_id=req.run_id
    )
    db.add(trip)
    db.flush()  # 确保 trip.id 可用
    
    # 3. 解析 plan 中的 stops 并创建站点（增强健壮性）
    stops_data = req.plan.get("stops", [])
    if not stops_data:
        raise HTTPException(status_code=400, detail="plan.stops is required and cannot be empty")
    
    created_stops = []
    for index, stop_data in enumerate(stops_data):
        # === 健壮性处理：确保所有必需字段存在且非空 ===
        
        # 1. seq: 如果缺失，按数组顺序自动生成（从 1 开始）
        seq = stop_data.get("seq")
        if seq is None:
            seq = index + 1
            print(f"⚠️  Warning: Stop {index} 缺少 seq，自动补充为 {seq}")
        
        # 2. poi_id: 兼容多种字段名，去除空格，确保非空
        poi_id = stop_data.get("poi_id") or stop_data.get("poiId") or ""
        poi_id = str(poi_id).strip()  # 去除前后空格
        if not poi_id:  # 如果为空字符串，使用默认值
            poi_id = f"unknown_{seq}"
            print(f"⚠️  Warning: Stop {index} (seq={seq}) 缺少 poi_id，使用默认值 {poi_id}")
        
        # 3. name: 去除空格，如果为空则使用 poi_id
        name = stop_data.get("name") or ""
        name = str(name).strip()
        if not name:  # 如果为空字符串，使用默认名称
            if poi_id.startswith("unknown_"):
                name = f"Unknown Stop {seq}"
            else:
                name = poi_id
            print(f"⚠️  Warning: Stop {index} (seq={seq}) 缺少 name，使用默认值: {name}")
        
        # 4. category: 去除空格，如果为空则使用 "WAYPOINT"
        category = stop_data.get("category") or ""
        category = str(category).strip()
        if not category:  # 如果为空字符串，使用默认分类
            category = "WAYPOINT"
        
        # 5. distance_m: 兼容多种字段名，确保为整数
        distance_m = stop_data.get("distance_m") or stop_data.get("distanceM")
        try:
            distance_m = int(distance_m or 0)
        except (ValueError, TypeError):
            distance_m = 0
        
        # 6. 兼容前端常用的 lng 字段名（统一为 lon）
        lon = stop_data.get("lon") or stop_data.get("lng")
        lat = stop_data.get("lat")
        
        # 7. 如果 lat/lon 缺失，使用 None（数据库允许 NULL）
        if lat is None:
            print(f"⚠️  Warning: Stop {index} 缺少 lat，设置为 None")
        if lon is None:
            print(f"⚠️  Warning: Stop {index} 缺少 lon，设置为 None")
        
        # === 最终验证：确保 poi_id 绝对不是空字符串 ===
        assert poi_id and poi_id.strip(), f"Stop {index} 的 poi_id 不能为空字符串"
        
        # 创建 TripStop 记录
        stop = TripStop(
            trip_id=trip.id,
            seq=seq,
            poi_id=poi_id,  # 已确保非空
            name=name,      # 已确保非空
            category=category,  # 已确保非空
            distance_m=distance_m,
            status=StopStatus.UPCOMING
        )
        db.add(stop)
        db.flush()  # 确保能获取到生成的 stop.id
        
        # 构造返回的 stop 信息（含数据库生成的 stop_id）
        created_stops.append(StopCreatedResponse(
            stop_id=str(stop.id),
            seq=stop.seq,
            poi_id=stop.poi_id,
            name=stop.name,
            lat=lat if lat is not None else 0.0,
            lon=lon if lon is not None else 0.0,
            status=stop.status.value
        ))
    
    db.commit()
    
    return CreateTripResponse(
        trip_id=str(trip.id),
        stops=created_stops,
        plan=req.plan
    )


@router.get("/trips/history", response_model=List[TripHistoryItem])
def list_trip_history(
    user_openid: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取用户历史行程摘要（供前端下拉选择）
    返回包含站点名称、AI summary 与用户记忆点的简要信息。
    """
    user = db.query(User).filter(User.openid == user_openid).first()
    if not user:
        return []

    trips = db.query(Trip).filter(
        Trip.user_id == user.id
    ).order_by(Trip.created_at.desc()).limit(limit).all()

    result: List[TripHistoryItem] = []
    for trip in trips:
        stops = db.query(TripStop).filter(
            TripStop.trip_id == trip.id
        ).order_by(TripStop.seq).all()

        memories = db.query(Memory).filter(
            Memory.trip_id == trip.id
        ).order_by(Memory.created_at).all()

        stop_memories_map: Dict[Any, Dict[str, List[Dict[str, Any]]]] = {}
        for mem in memories:
            if mem.stop_id:
                if mem.stop_id not in stop_memories_map:
                    stop_memories_map[mem.stop_id] = {"user_notes": [], "ai_insights": []}
                if mem.source == MemorySource.USER and mem.type == MemoryType.NOTE:
                    stop_memories_map[mem.stop_id]["user_notes"].append(mem.content)
                elif mem.source == MemorySource.AI and mem.type == MemoryType.INSIGHT:
                    stop_memories_map[mem.stop_id]["ai_insights"].append(mem.content)

        stop_items: List[TripHistoryStop] = []
        for stop in stops:
            mem_data = stop_memories_map.get(stop.id, {"user_notes": [], "ai_insights": []})
            ai_summary = mem_data["ai_insights"][-1] if mem_data["ai_insights"] else None
            stop_items.append(TripHistoryStop(
                seq=stop.seq,
                poi_id=stop.poi_id,
                name=stop.name,
                user_logs=mem_data["user_notes"],
                ai_summary=ai_summary
            ))

        title = "我的旅程"
        if trip.request_json and isinstance(trip.request_json, dict):
            title = trip.request_json.get("selected_route_name") or title

        result.append(TripHistoryItem(
            trip_id=str(trip.id),
            title=title,
            created_at=trip.created_at,
            stops=stop_items
        ))

    return result


@router.get("/trips/{trip_id}", response_model=TripDetailResponse)
def get_trip_detail(
    trip_id: str,
    include_memories: bool = False,
    db: Session = Depends(get_db)
):
    """
    获取行程详情
    返回：行程信息 + 站点列表（按 seq 排序，含聚合的 user_logs/ai_summary）+ 记忆列表（可选）
    user_logs: 从 memories 聚合（source=USER, type=NOTE，按 created_at 升序）
    ai_summary: 从 memories 聚合（source=AI, type=INSIGHT，取最新一条）
    lat/lon: 从 MOCK_DB 根据 poi_id 查询补充
    """
    # 导入 MOCK_DB
    from app.services.mock_db import MOCK_DB
    
    # 构建 POI ID -> POI 映射表
    poi_by_id = {poi.id: poi for poi in MOCK_DB}
    
    # 查询行程（404 if not found）
    try:
        trip_uuid = UUID(trip_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid trip_id format")
    
    trip = db.query(Trip).filter(Trip.id == trip_uuid).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # 查询站点（按 seq 排序）
    stops = db.query(TripStop).filter(
        TripStop.trip_id == trip_uuid
    ).order_by(TripStop.seq).all()
    
    # 查询记忆（按创建时间排序）
    memories = db.query(Memory).filter(
        Memory.trip_id == trip_uuid
    ).order_by(Memory.created_at).all()
    
    # 构建 stop_id -> memories 映射
    stop_memories_map = {}
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
    
    # 构造站点响应（含 user_logs 和 ai_summary 以及 lat/lon）
    stops_with_memories = []
    for stop in stops:
        # 从 MOCK_DB 查询 POI 坐标
        poi = poi_by_id.get(stop.poi_id)
        lat = poi.lat if poi else None
        lon = poi.lon if poi else None
        
        if not poi:
            print(f"⚠️  Warning: Stop {stop.seq} (poi_id={stop.poi_id}) 未在 MOCK_DB 中找到，lat/lon 设置为 None")
        else:
            print(f"✅ Stop {stop.seq} (poi_id={stop.poi_id}, name={stop.name}) 坐标: lat={lat}, lon={lon}")
        
        # 将 ORM 对象转换为字典，确保 UUID 字段转换为 str
        stop_dict = {
            "id": str(stop.id),
            "seq": stop.seq,
            "poi_id": stop.poi_id,
            "name": stop.name,
            "category": stop.category,
            "distance_m": stop.distance_m,
            "status": stop.status.value,
            "arrived_at": stop.arrived_at,
            "completed_at": stop.completed_at,
            "lat": lat,
            "lon": lon
        }
        
        mem_data = stop_memories_map.get(stop.id, {"user_notes": [], "ai_insights": []})
        
        # user_logs: 按 created_at 升序
        user_notes = sorted(mem_data["user_notes"], key=lambda x: x["created_at"])
        stop_dict["user_logs"] = [note["content"] for note in user_notes]
        
        # ai_summary: 最新一条（created_at 最大）
        ai_insights = sorted(mem_data["ai_insights"], key=lambda x: x["created_at"], reverse=True)
        stop_dict["ai_summary"] = ai_insights[0]["content"] if ai_insights else None
        
        stops_with_memories.append(StopResponseWithMemories(**stop_dict))
    
    # 构造响应
    trip_dict = {
        "id": str(trip.id),
        "user_id": str(trip.user_id),
        "status": trip.status.value,
        "request_json": trip.request_json,
        "run_id": trip.run_id,
        "created_at": trip.created_at,
        "updated_at": trip.updated_at
    }
    
    # 仅在 include_memories=true 时返回完整 memories 列表
    memories_list = []
    if include_memories:
        for m in memories:
            mem_dict = {
                "id": str(m.id),
                "stop_id": str(m.stop_id) if m.stop_id else None,
                "source": m.source.value,
                "type": m.type.value,
                "content": m.content,
                "meta_json": m.meta_json,
                "created_at": m.created_at
            }
            memories_list.append(MemoryResponse(**mem_dict))
    
    return TripDetailResponse(
        trip=trip_dict,
        stops=stops_with_memories,
        memories=memories_list
    )


@router.post("/trips/{trip_id}/stops/{stop_id}/arrive", response_model=StopResponse)
def arrive_at_stop(
    trip_id: str,
    stop_id: str,
    db: Session = Depends(get_db)
):
    """
    标记站点为"已到达"
    1. 更新 stop.status = ARRIVED, arrived_at = now
    2. 如果 trip.status 是 DRAFT，改为 ACTIVE（首次到达任意站点即开始行程）
    3. 返回更新后的 stop
    """
    # 校验并查询 stop
    try:
        trip_uuid = UUID(trip_id)
        stop_uuid = UUID(stop_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    stop = db.query(TripStop).filter(
        TripStop.id == stop_uuid,
        TripStop.trip_id == trip_uuid
    ).first()
    
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found or does not belong to this trip")
    
    # 更新站点状态（使用 timezone-aware UTC 时间）
    stop.status = StopStatus.ARRIVED
    stop.arrived_at = now_utc()  # 使用 UTC timezone-aware datetime
    
    # Debug: 打印时区信息
    print(f"[arrive_at_stop] stop_id={stop_id}, arrived_at={stop.arrived_at}, tzinfo={stop.arrived_at.tzinfo}")
    
    # 查询行程，如果是 DRAFT 则改为 ACTIVE
    trip = db.query(Trip).filter(Trip.id == trip_uuid).first()
    if trip and trip.status == TripStatus.DRAFT:
        trip.status = TripStatus.ACTIVE
    
    db.commit()
    db.refresh(stop)
    
    # 手动构造响应，确保 UUID 转换为 str
    return StopResponse(
        id=str(stop.id),
        seq=stop.seq,
        poi_id=stop.poi_id,
        name=stop.name,
        category=stop.category,
        distance_m=stop.distance_m,
        status=stop.status.value,
        arrived_at=stop.arrived_at,
        completed_at=stop.completed_at
    )


@router.post("/trips/{trip_id}/stops/{stop_id}/complete", response_model=StopCompleteResponse)
def complete_stop(
    trip_id: str,
    stop_id: str,
    db: Session = Depends(get_db)
):
    """
    标记站点为"已完成"
    1. 更新 stop.status = COMPLETED, completed_at = now
    2. 生成 AI 洞察（基于 POI 信息和用户笔记）
    3. 检查该行程下是否所有站点都已完成或跳过，如果是则 trip.status = COMPLETED
    4. 返回更新后的 stop 和 ai_summary
    """
    # 校验并查询 stop
    try:
        trip_uuid = UUID(trip_id)
        stop_uuid = UUID(stop_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    stop = db.query(TripStop).filter(
        TripStop.id == stop_uuid,
        TripStop.trip_id == trip_uuid
    ).first()
    
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found or does not belong to this trip")
    
    # 更新站点状态（使用 timezone-aware UTC 时间）
    stop.status = StopStatus.COMPLETED
    stop.completed_at = now_utc()  # 使用 UTC timezone-aware datetime
    
    # Debug: 打印时区信息
    print(f"[complete_stop] stop_id={stop_id}, completed_at={stop.completed_at}, tzinfo={stop.completed_at.tzinfo}")
    
    # 计算停留时长（确保两个时间都是 timezone-aware）
    visit_duration_min = None
    if stop.arrived_at:
        # 确保两个 datetime 都是 UTC timezone-aware
        arrived_at_utc = ensure_utc(stop.arrived_at)
        completed_at_utc = ensure_utc(stop.completed_at)
        
        # Debug: 打印转换后的时区信息
        print(f"[complete_stop] arrived_at_utc={arrived_at_utc}, tzinfo={arrived_at_utc.tzinfo if arrived_at_utc else None}")
        print(f"[complete_stop] completed_at_utc={completed_at_utc}, tzinfo={completed_at_utc.tzinfo if completed_at_utc else None}")
        
        if arrived_at_utc and completed_at_utc:
            duration = completed_at_utc - arrived_at_utc
            visit_duration_min = int(duration.total_seconds() / 60)
            print(f"[complete_stop] visit_duration_min={visit_duration_min}")
        else:
            print(f"[complete_stop] ⚠️ arrived_at 或 completed_at 为 None，跳过时长计算")
    else:
        print(f"[complete_stop] ⚠️ stop.arrived_at 为 None，跳过时长计算，duration=None")
    
    # 查询该 stop 的用户笔记（USER_NOTE）
    user_notes = db.query(Memory).filter(
        Memory.stop_id == stop_uuid,
        Memory.type == MemoryType.NOTE
    ).all()
    user_notes_text = [note.content for note in user_notes]
    
    # 生成 AI 洞察
    ai_summary = None
    try:
        import os
        from langchain_community.chat_models import ChatTongyi
        from langchain_core.prompts import ChatPromptTemplate
        
        llm_model = os.getenv("LLM_MODEL_NAME", "qwen-plus")
        llm = ChatTongyi(model=llm_model, temperature=0.7)
        
        # 构造 prompt
        user_notes_str = "\n".join(user_notes_text) if user_notes_text else "无用户笔记"
        duration_str = f"{visit_duration_min} 分钟" if visit_duration_min else "未知"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的旅行导览助手。用户刚完成了一个景点的游览，请根据以下信息生成 1-3 句简洁的中文洞察（aiSummary），总结用户的体验和该景点的特点。"),
            ("user", f"景点名称：{stop.name}\n分类：{stop.category or '未知'}\n停留时长：{duration_str}\n用户笔记：\n{user_notes_str}\n\n请生成 aiSummary（1-3 句，中文）：")
        ])
        
        chain = prompt | llm
        result = chain.invoke({})
        ai_summary = result.content.strip()
        
        # 写入 memories
        memory = Memory(
            trip_id=trip_uuid,
            stop_id=stop_uuid,
            source=MemorySource.AI,
            type=MemoryType.INSIGHT,
            content=ai_summary,
            meta_json={"visit_duration_min": visit_duration_min}
        )
        db.add(memory)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to generate AI insight: {e}")
        ai_summary = None
    
    # 检查是否所有站点都已完成或跳过
    all_stops = db.query(TripStop).filter(TripStop.trip_id == trip_uuid).all()
    all_finished = all(
        s.status in [StopStatus.COMPLETED, StopStatus.SKIPPED]
        for s in all_stops
    )
    
    # 如果所有站点都已完成，标记行程为已完成
    if all_finished:
        trip = db.query(Trip).filter(Trip.id == trip_uuid).first()
        if trip:
            trip.status = TripStatus.COMPLETED
    
    db.commit()
    db.refresh(stop)
    
    # 手动构造 StopResponse，确保 UUID 转换为 str
    stop_response = StopResponse(
        id=str(stop.id),
        seq=stop.seq,
        poi_id=stop.poi_id,
        name=stop.name,
        category=stop.category,
        distance_m=stop.distance_m,
        status=stop.status.value,
        arrived_at=stop.arrived_at,
        completed_at=stop.completed_at
    )
    
    return StopCompleteResponse(
        stop=stop_response,
        ai_summary=ai_summary
    )


@router.post("/trips/{trip_id}/stops/{stop_id}/memories", response_model=CreateStopMemoryResponse)
def create_stop_memory(
    trip_id: str,
    stop_id: str,
    req: CreateStopMemoryRequest,
    db: Session = Depends(get_db)
):
    """
    为站点添加记忆（用户笔记或 AI 洞察）
    
    支持两种格式：
    1. 组合格式：{"source": "USER", "type": "NOTE", "text": "..."}
    2. 简化格式：{"type": "USER_NOTE", "text": "..."}
    """
    # 校验 trip_id 和 stop_id
    try:
        trip_uuid = UUID(trip_id)
        stop_uuid = UUID(stop_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    # 检查 stop 是否存在且属于该 trip
    stop = db.query(TripStop).filter(
        TripStop.id == stop_uuid,
        TripStop.trip_id == trip_uuid
    ).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found or does not belong to this trip")
    
    # 智能映射 type 和 source
    source = None
    mem_type = None
    type_input = req.type.upper()
    source_input = req.source.upper() if req.source else None
    
    # 情况1：简化格式（type 已包含来源信息）
    if type_input == "USER_NOTE":
        source = MemorySource.USER
        mem_type = MemoryType.NOTE
    elif type_input == "AI_INSIGHT":
        source = MemorySource.AI
        mem_type = MemoryType.INSIGHT
    # 情况2：组合格式（source + type）
    elif type_input == "NOTE" and source_input == "USER":
        source = MemorySource.USER
        mem_type = MemoryType.NOTE
    elif type_input == "INSIGHT" and source_input == "AI":
        source = MemorySource.AI
        mem_type = MemoryType.INSIGHT
    # 情况3：其他组合
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid type/source combination. Supported: "
                   f"1) type='USER_NOTE' or 'AI_INSIGHT' (standalone), "
                   f"2) type='NOTE' + source='USER', or type='INSIGHT' + source='AI'. "
                   f"Got: type='{req.type}', source='{req.source}'"
        )
    
    # 创建记忆
    memory = Memory(
        trip_id=trip_uuid,
        stop_id=stop_uuid,
        source=source,
        type=mem_type,
        content=req.text,
        meta_json=None
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    
    return CreateStopMemoryResponse(
        id=str(memory.id),
        stop_id=str(memory.stop_id),
        type=f"{source.value}_{mem_type.value}",  # 返回统一格式 USER_NOTE/AI_INSIGHT
        text=memory.content,
        created_at=memory.created_at
    )


@router.post("/trips/{trip_id}/memories")
def create_memory(
    trip_id: str,
    req: CreateMemoryRequest,
    db: Session = Depends(get_db)
):
    """
    为行程添加记忆（笔记或洞察）
    可以关联到整个行程（stop_id 为空），或关联到具体站点
    """
    # 校验 trip_id
    try:
        trip_uuid = UUID(trip_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid trip_id format")
    
    # 检查行程是否存在
    trip = db.query(Trip).filter(Trip.id == trip_uuid).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # 校验 stop_id（如果提供）
    stop_uuid = None
    if req.stop_id:
        try:
            stop_uuid = UUID(req.stop_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid stop_id format")
        
        # 检查 stop 是否存在且属于该 trip
        stop = db.query(TripStop).filter(
            TripStop.id == stop_uuid,
            TripStop.trip_id == trip_uuid
        ).first()
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found or does not belong to this trip")
    
    # 创建记忆
    memory = Memory(
        trip_id=trip_uuid,
        stop_id=stop_uuid,
        source=req.source,
        type=req.type,
        content=req.content,
        meta_json=req.meta
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    
    return {
        "ok": True,
        "memory_id": str(memory.id),
        "message": "Memory created successfully"
    }
