from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import logging
import traceback
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# Import the graph
from app.graph import app_graph

# Import routers
from app.api.trips import router as trips_router
from app.api.posts import router as posts_router
from app.api.uploads import router as uploads_router

app = FastAPI(title="Beijing Tour Guide Agent")

# 挂载静态文件目录（用于访问上传的图片）
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 获取 uvicorn 的 logger
logger = logging.getLogger("uvicorn.error")

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器：捕获所有未处理的异常
    - 打印完整的 traceback 到终端
    - 返回 JSON 错误信息
    - 如果 DEBUG_API_ERRORS=1，返回完整堆栈信息
    """
    # 1. 记录完整的异常堆栈到日志（在终端可见）
    logger.exception(
        f"❌ Unhandled exception at {request.method} {request.url.path}: {exc}"
    )
    
    # 2. 构造基本错误响应
    error_response = {
        "detail": "Internal Server Error",
        "error": str(exc)
    }
    
    # 3. 如果开启调试模式，返回完整堆栈
    debug_mode = os.getenv("DEBUG_API_ERRORS", "0") == "1"
    if debug_mode:
        error_response["trace"] = traceback.format_exc()
    
    # 4. 返回 500 错误
    return JSONResponse(
        status_code=500,
        content=error_response
    )

# Include routers
app.include_router(trips_router)
app.include_router(posts_router)
app.include_router(uploads_router)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "Beijing Tour Guide Agent"}

# 测试异常处理器的端点（仅用于开发/测试）
@app.get("/api/test-error")
async def test_error():
    """
    测试端点：故意抛出异常，验证全局异常处理器
    访问此端点将触发一个 ValueError，用于测试全局异常处理器是否正常工作
    """
    raise ValueError("这是一个测试异常 - 用于验证全局异常处理器")

# Define Request Model
class PlanRequest(BaseModel):
    selected_themes: List[str]
    time_budget: str
    mbti: Optional[str] = None
    transportation: str = "walking"
    user_text_input: str = ""
    selected_route_name: Optional[str] = ""
    pace_preference: str = "medium"

# ========== V2 Request Model ==========
class PlanRequestV2(BaseModel):
    """V2 版本的行程规划请求（支持三种模式）"""
    # 模式选择（必填）
    mode: str  # "PICK_POIS" | "PRESET_ROUTE" | "FREE_TEXT"
    
    # 模式相关参数
    selected_poi_ids: Optional[List[str]] = None  # PICK_POIS 模式使用
    preset_route_id: Optional[str] = None  # PRESET_ROUTE 模式使用
    user_text_input: Optional[str] = None  # FREE_TEXT 模式使用
    
    # 通用参数
    time_budget: str = "half_day"  # "half_day" | "full_day"
    transportation: str = "walking"  # "walking" | "driving"
    pace_preference: str = "medium"  # "slow" | "medium" | "fast"
    mbti: Optional[str] = None
    
    # 控制选项
    allow_auto_fill: bool = False  # 是否允许自动补充POI（仅PICK_POIS模式）
    keep_order: bool = True  # 是否保持用户选择的顺序（仅PICK_POIS模式）

# Define Stop Model for structured response
class PlanStop(BaseModel):
    """单个站点的结构化信息"""
    seq: int
    poi_id: str
    name: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    category: Optional[str] = None
    distance_m: Optional[int] = None
    zone: Optional[str] = None
    tags: Optional[List[str]] = None
    visit_duration_min: Optional[int] = None
    transit_note: Optional[str] = None
    status: Optional[str] = "UPCOMING"

# Define Plan Model for structured response
class PlanStructured(BaseModel):
    """结构化的行程规划"""
    mode: str
    summary: str
    total_duration_min: int
    total_distance_m: int
    stops: List[PlanStop]
    zones: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    polyline: Optional[str] = None

# Define Response Model
class PlanResponse(BaseModel):
    """
    /api/plan 的响应模型
    - response_text: AI 生成的文本描述
    - plan: 结构化的行程规划（必须包含 stops 数组，且每个 stop 有 seq）
    - run_id: LangGraph 运行 ID（可选）
    """
    response_text: str
    plan: PlanStructured
    run_id: Optional[str] = None

@app.post("/api/plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    # 1. Translation Layer: JSON -> Natural Language
    themes_str = ', '.join(request.selected_themes)
    route_str = f"，参考路线：{request.selected_route_name}" if request.selected_route_name else ""
    text_str = f"，补充想法：{request.user_text_input}" if request.user_text_input else ""
    
    user_prompt = (
        f"我计划在北京玩 {request.time_budget}。我对 {themes_str} 感兴趣{route_str}{text_str}。"
        f"我的MBTI是 {request.mbti}。我想通过 {request.transportation} 出行。"
        f"我的步速偏好是 {request.pace_preference}。"
    )
    
    print(f"\n{'='*80}")
    print(f"📝 POST /api/plan")
    print(f"{'='*80}")
    print(f"Translated Prompt: {user_prompt}")
    print(f"selected_themes: {request.selected_themes}")
    
    # 🔥 区分 POI IDs 和 tags
    # 检查 selected_themes 中是否有 POI IDs（从统一数据源判断）
    from app.data.pois import POIS_BY_ID
    
    potential_poi_ids = []
    actual_tags = []
    
    for theme in request.selected_themes:
        if theme in POIS_BY_ID:
            potential_poi_ids.append(theme)
        else:
            actual_tags.append(theme)
    
    print(f"  → 识别到 POI IDs: {potential_poi_ids}")
    print(f"  → 识别到 tags: {actual_tags}")
    print(f"{'='*80}\n")
    
    # 2. Construct Initial State
    # Populate user_profile to allow skipping Profiler if data is sufficient
    from app.state import UserProfile
    
    # Always create UserProfile with available data
    initial_profile = UserProfile(
         mbti_type=request.mbti or "Unknown",
         interests=request.selected_themes, # Can be empty list
         time_budget=request.time_budget,
         pace_preference=request.pace_preference,
         transportation=request.transportation,
         persona_instruction="" 
    )

    initial_state = {
        "messages": [HumanMessage(content=user_prompt)],
        "user_profile": initial_profile,
        "selected_poi_ids": potential_poi_ids if potential_poi_ids else []  # 🔥 传递 POI IDs
    }
    
    # 3. Invoke Graph
    # We can use collect_runs if we want to return the run_id
    from langchain_core.tracers.context import collect_runs
    
    run_id = None
    with collect_runs() as runs:
        final_state = app_graph.invoke(initial_state, config={"recursion_limit": 50})
        if runs.traced_runs:
            run_id = str(runs.traced_runs[0].id)
    
    # 4. Extract Final Response
    last_message = final_state["messages"][-1]
    response_text = last_message.content
    
    # 5. Extract plan from state (Navigator 生成的结构化 plan)
    plan_dict = final_state.get("plan")
    
    # 如果 plan 为空，构造一个最小可用 plan（保证前端不会报错）
    if not plan_dict or not plan_dict.get("stops"):
        print("⚠️  Warning: plan 为空或 stops 为空，使用 fallback")
        plan_dict = {
            "mode": request.transportation or "walking",
            "total_distance_m": 0,
            "total_duration_min": 0,
            "summary": "未生成具体路线",
            "polyline": "",
            "tags": request.selected_themes,
            "zones": [],
            "stops": [],
        }
    
    # 6. 验证 plan 结构（确保 stops 有 seq）
    stops = plan_dict.get("stops", [])
    if stops:
        for idx, stop in enumerate(stops):
            # 如果 stop 没有 seq，自动补充（从 1 开始）
            if "seq" not in stop or stop["seq"] is None:
                stop["seq"] = idx + 1
                print(f"⚠️  Warning: Stop {idx} 缺少 seq，已自动补充为 {stop['seq']}")
            
            # 🔥 确保必需字段存在
            if "lat" not in stop or stop["lat"] is None:
                print(f"⚠️  Warning: Stop {idx} 缺少 lat")
            if "lon" not in stop or stop["lon"] is None:
                print(f"⚠️  Warning: Stop {idx} 缺少 lon")
            if "poi_id" not in stop or not stop["poi_id"]:
                stop["poi_id"] = f"poi_{idx + 1}"
                print(f"⚠️  Warning: Stop {idx} 缺少 poi_id，已自动补充")
    
    # 7. Construct PlanStructured from dict
    plan_structured = PlanStructured(**plan_dict)
    
    # 8. Return Response
    return PlanResponse(
        response_text=response_text,
        plan=plan_structured,
        run_id=run_id
    )


# ========== V2 API Endpoint ==========
@app.post("/api/plan/v2")
async def generate_plan_v2(request: PlanRequestV2):
    """
    V2 版本的行程规划 API
    支持三种模式:
    1. PICK_POIS: 用户手选景点
    2. PRESET_ROUTE: 预设路线
    3. FREE_TEXT: 自然语言输入
    """
    from app.services.plan_service_v2 import (
        resolve_candidates_pick_pois,
        resolve_candidates_preset_route,
        resolve_candidates_free_text,
        build_plan_from_pois
    )
    
    print(f"\n{'='*80}")
    print(f"🚀 POST /api/plan/v2")
    print(f"{'='*80}")
    print(f"Request body:")
    print(f"  - mode: {request.mode}")
    print(f"  - selected_poi_ids: {request.selected_poi_ids}")
    print(f"  - preset_route_id: {request.preset_route_id}")
    print(f"  - user_text_input: {request.user_text_input}")
    print(f"  - time_budget: {request.time_budget}")
    print(f"  - transportation: {request.transportation}")
    print(f"  - allow_auto_fill: {request.allow_auto_fill}")
    print(f"  - keep_order: {request.keep_order}")
    print(f"{'='*80}\n")
    
    # 1. 根据 mode 分流获取候选 POI
    pois = []
    
    if request.mode == "PICK_POIS":
        if not request.selected_poi_ids:
            raise HTTPException(
                status_code=400,
                detail="PICK_POIS 模式需要提供 selected_poi_ids"
            )
        pois = resolve_candidates_pick_pois(
            selected_poi_ids=request.selected_poi_ids,
            allow_auto_fill=request.allow_auto_fill,
            keep_order=request.keep_order,
            time_budget=request.time_budget
        )
    
    elif request.mode == "PRESET_ROUTE":
        if not request.preset_route_id:
            raise HTTPException(
                status_code=400,
                detail="PRESET_ROUTE 模式需要提供 preset_route_id"
            )
        pois = resolve_candidates_preset_route(
            preset_route_id=request.preset_route_id
        )
    
    elif request.mode == "FREE_TEXT":
        if not request.user_text_input:
            raise HTTPException(
                status_code=400,
                detail="FREE_TEXT 模式需要提供 user_text_input"
            )
        pois = resolve_candidates_free_text(
            user_text_input=request.user_text_input,
            mbti=request.mbti,
            time_budget=request.time_budget
        )
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的 mode: {request.mode}。支持的模式: PICK_POIS, PRESET_ROUTE, FREE_TEXT"
        )
    
    # 2. 检查是否获取到 POI
    if not pois:
        raise HTTPException(
            status_code=400,
            detail="未找到匹配的 POI，请检查输入参数"
        )
    
    # 3. 构建完整的 plan
    plan_dict = build_plan_from_pois(
        pois=pois,
        mode=request.mode,
        transportation=request.transportation,
        pace_preference=request.pace_preference
    )
    
    # 4. 构建响应
    response_text = f"为您规划了{len(plan_dict['stops'])}个站点的行程：{plan_dict['summary']}"
    
    plan_structured = PlanStructured(**plan_dict)
    
    print(f"\n{'='*80}")
    print(f"✅ 行程生成成功")
    print(f"{'='*80}")
    print(f"返回数据:")
    print(f"  - stops 数量: {len(plan_dict['stops'])}")
    print(f"  - 总时长: {plan_dict['total_duration_min']} 分钟")
    print(f"  - 总距离: {plan_dict['total_distance_m']} 米")
    print(f"  - 摘要: {plan_dict['summary']}")
    print(f"{'='*80}\n")
    
    return PlanResponse(
        response_text=response_text,
        plan=plan_structured,
        run_id=None  # V2 不使用 LangGraph，所以没有 run_id
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
