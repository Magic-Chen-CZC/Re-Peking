from langchain_core.messages import AIMessage
from ..state import AgentState
from ..services.mock_db import select_pois, sort_route

def navigator_node(state: AgentState):
    user_profile = state["user_profile"]
    
    # 🔥 支持三种 POI 选择模式
    # 1. 检查是否有明确的 selected_poi_ids（优先级最高）
    selected_poi_ids = state.get("selected_poi_ids", None) or []
    
    print(f"\n[navigator_node] 开始生成行程")
    print(f"  - interests: {user_profile.interests}")
    print(f"  - selected_poi_ids: {selected_poi_ids}")
    print(f"  - time_budget: {user_profile.time_budget}")
    
    # Logic A: Select POIs
    if selected_poi_ids:
        # 模式1: 用户明确选择了 POI IDs
        print(f"  → 使用用户明确选择的 POI IDs")
        selected_pois = select_pois(
            interests=user_profile.interests,
            time_budget=user_profile.time_budget,
            selected_poi_ids=selected_poi_ids
        )
    else:
        # 模式2: 从 interests 分析（可能包含 POI IDs 或 tags）
        print(f"  → 从 interests 分析 POI 选择")
        selected_pois = select_pois(
            interests=user_profile.interests,
            time_budget=user_profile.time_budget
        )
    
    print(f"  ✅ 选中 {len(selected_pois)} 个 POI")
    
    # Logic B: Determine Mode & Sort Route
    from ..services.map_service import amap_service
    
    # 1. Determine Mode
    user_mode = user_profile.transportation
    final_mode = "walking" # Default
    
    if user_mode in ["walking", "driving"]:
        final_mode = user_mode
    else:
        # Auto mode: Check straight line distance
        # Simple heuristic: if any two points are far, use driving.
        # For simplicity, we can check total straight line distance or just assume driving if > 3km
        # Here we do a quick check if we have coords
        # Since we haven't routed yet, we can't know exact distance.
        # We can use a rough estimate or just default to walking if close, driving if far.
        # Let's try to get a rough route first or just use driving for safety if "auto" and > 3 POIs?
        # Better: Use AMap to get walking distance first? No that's double cost.
        # Let's use the logic: if "auto", we check if the user has "slow" pace -> walking, "fast" -> driving?
        # Or just use the user requirement: "if > 3km, auto switch to driving".
        # To know if > 3km without routing, we can calculate Haversine distance of the sequence.
        
        # Let's do a simple Haversine check on the selected POIs (assuming sorted by input/mock logic first?)
        # Actually selected_pois are just clustered.
        # Let's just default to "driving" for "auto" if there are more than 3 POIs or if they are in different zones?
        # The requirement says: "if > 3km, auto switch to driving".
        # We need to estimate distance.
        
        total_est_dist = 0
        for i in range(len(selected_pois) - 1):
            p1 = selected_pois[i]
            p2 = selected_pois[i+1]
            # Simple Euclidean approx for Beijing (lat/lon)
            # 1 deg lat ~ 111km, 1 deg lon ~ 85km
            dx = (p1.lon - p2.lon) * 85000
            dy = (p1.lat - p2.lat) * 111000
            dist = (dx**2 + dy**2)**0.5
            total_est_dist += dist
            
        if total_est_dist > 3000:
            final_mode = "driving"
        else:
            final_mode = "walking"

    # 2. Call Routing
    route_plan = amap_service.get_optimal_route(selected_pois, travel_mode=final_mode)
    
    # 3. 构造纯 JSON 可序列化的 plan_dict（供 /api/plan 返回 & POST /api/trips 使用）
    zone_summary = list(set([p.zone for p in selected_pois]))
    tags_summary = user_profile.interests
    
    # 从 route_plan.steps 生成 stops 数组（确保每个 stop 有 seq, poi_id, name, lat, lon 等必需字段）
    stops = []
    for idx, step in enumerate(route_plan.steps, start=1):
        # 提取距离信息（如果 transit_note 包含距离，可以解析；否则使用默认值）
        distance_m = 0
        if idx > 1:  # 第一个站点没有"距离上一站"
            # 简单估算：根据经纬度计算 Haversine 距离
            prev_step = route_plan.steps[idx - 2]
            dx = (step.poi.lon - prev_step.poi.lon) * 85000  # 1度经度 ≈ 85km (北京纬度)
            dy = (step.poi.lat - prev_step.poi.lat) * 111000  # 1度纬度 ≈ 111km
            distance_m = int((dx**2 + dy**2)**0.5)
        
        # === 健壮性处理：提取并验证必需字段 ===
        
        # 1. poi_id: 兼容多种字段名，去除空格，确保非空
        raw_poi_id = getattr(step.poi, "id", None) or getattr(step.poi, "poi_id", None) or ""
        poi_id = str(raw_poi_id).strip()
        if not poi_id:
            poi_id = f"unknown_{idx}"
            print(f"⚠️  Warning: Step {idx} 的 poi.id 为空，使用默认值: {poi_id}")
        
        # 2. name: 去除空格，如果为空则使用 poi_id
        raw_name = getattr(step.poi, "name", None) or ""
        name = str(raw_name).strip()
        if not name:
            name = poi_id
            print(f"⚠️  Warning: Step {idx} 的 poi.name 为空，使用 poi_id: {name}")
        
        # 3. category: 从 tags 提取第一个，如果为空则使用 "WAYPOINT"
        category = ""
        if step.poi.tags and len(step.poi.tags) > 0:
            category = str(step.poi.tags[0]).strip()
        if not category:
            category = "WAYPOINT"
        
        # 构造 stop 字典（包含所有后端创建 TripStop 所需的字段）
        stop_dict = {
            # 必需字段（已验证非空）
            "seq": idx,
            "poi_id": poi_id,
            "name": name,
            "lat": step.poi.lat,
            "lon": step.poi.lon,
            # 可选但推荐的字段
            "zone": step.poi.zone,
            "tags": step.poi.tags,
            "category": category,
            "distance_m": distance_m,  # 距离上一站的距离
            "visit_duration_min": step.visit_duration,
            "transit_note": step.transit_note,
            "status": "UPCOMING",
            # camelCase 别名（前端兼容）
            "poiId": poi_id,
            "visitDurationMin": step.visit_duration,
            "transitNote": step.transit_note,
            "distanceM": distance_m,
        }
        stops.append(stop_dict)
    
    # 构造完整的 plan_dict
    plan_dict = {
        # snake_case 字段（Python/后端风格）
        "mode": route_plan.mode,
        "total_distance_m": route_plan.total_distance,
        "total_duration_min": route_plan.total_duration,
        "summary": route_plan.summary,
        "polyline": getattr(route_plan, "polyline", "") or "",  # 兼容：如果 RoutePlan 没这个属性则置空
        "tags": tags_summary,
        "zones": zone_summary,
        "stops": stops,
        # camelCase 别名（前端兼容）
        "totalDistanceM": route_plan.total_distance,
        "totalDurationMin": route_plan.total_duration,
    }
    
    # 4. 构造返回消息（原有逻辑）
    mode_str = "驾车" if route_plan.mode == "driving" else "步行"
    
    msg_content = (
        f"[Navigator] 根据您的选择，为您规划了【{mode_str}】路线。\n"
        f"主题：【{', '.join(tags_summary)}】，区域：【{', '.join(zone_summary)}】。\n"
        f"全程预计耗时 {route_plan.total_duration} 分钟，距离 {route_plan.total_distance} 米。\n"
        f"路线包含：{route_plan.summary}。"
    )
    
    # 5. 返回 state（保留原有 route_plan/messages/next，新增 plan）
    return {
        "route_plan": route_plan,  # 原有：供其他 Agent 使用
        "plan": plan_dict,          # 新增：供 /api/plan 返回 & 前端创建行程使用
        "messages": [AIMessage(content=msg_content)],
        "next": "Supervisor"
    }
