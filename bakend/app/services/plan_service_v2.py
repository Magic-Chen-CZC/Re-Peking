"""行程生成服务 V2 - 支持三种模式"""
from typing import List, Dict, Optional, Tuple
from app.data.pois import (
    POI, 
    get_pois_by_ids, 
    get_route_pois, 
    search_pois_by_tags,
    POIS_DB
)
import re


def infer_preferences(
    user_text_input: str,
    mbti: Optional[str] = None,
    time_budget: str = "half_day"
) -> Tuple[List[str], List[str]]:
    """
    从自然语言输入推断用户偏好
    返回: (tags, zones)
    """
    print(f"\n{'='*60}")
    print(f"🤔 推断用户偏好")
    print(f"{'='*60}")
    print(f"用户输入: {user_text_input}")
    print(f"MBTI: {mbti}")
    print(f"时间预算: {time_budget}")
    
    tags = []
    zones = []
    
    # 关键词映射
    keyword_to_tags = {
        # 历史相关
        "历史": ["history"],
        "古代": ["history"],
        "帝王": ["imperial"],
        "皇家": ["imperial"],
        "故宫": ["imperial", "architecture"],
        "宫殿": ["imperial", "architecture"],
        
        # 建筑相关
        "建筑": ["architecture"],
        "古建": ["architecture"],
        
        # 自然相关
        "自然": ["nature"],
        "园林": ["garden", "nature"],
        "公园": ["park", "nature"],
        "山水": ["nature"],
        
        # 文化相关
        "文化": ["culture"],
        "艺术": ["art", "culture"],
        "胡同": ["hutong", "culture"],
        "传统": ["culture"],
        
        # 宗教相关
        "寺庙": ["temple"],
        "佛教": ["buddhism", "temple"],
        "道教": ["taoism", "temple"],
        "宗教": ["temple"],
        "祈福": ["temple"],
        
        # 美食相关
        "美食": ["food"],
        "小吃": ["food"],
        "餐饮": ["food"],
    }
    
    # 区域关键词
    zone_keywords = {
        "中心": "central",
        "市中心": "central",
        "城区": "central",
        "西边": "west",
        "西部": "west",
        "颐和园": "west",
        "北边": "north",
        "北部": "north",
        "东边": "east",
        "东部": "east",
    }
    
    # 提取标签
    for keyword, tag_list in keyword_to_tags.items():
        if keyword in user_text_input:
            tags.extend(tag_list)
            print(f"  ✓ 匹配关键词 '{keyword}' -> tags: {tag_list}")
    
    # 提取区域
    for keyword, zone in zone_keywords.items():
        if keyword in user_text_input:
            zones.append(zone)
            print(f"  ✓ 匹配区域关键词 '{keyword}' -> zone: {zone}")
    
    # 去重
    tags = list(set(tags))
    zones = list(set(zones))
    
    # 如果没有提取到任何标签，根据 MBTI 推断
    if not tags and mbti:
        print(f"  ℹ️  未提取到标签，根据 MBTI 推断...")
        if "NT" in mbti:  # 理性分析型
            tags = ["history", "architecture", "culture"]
        elif "NF" in mbti:  # 精神追求型
            tags = ["culture", "temple", "art"]
        elif "SF" in mbti:  # 感性体验型
            tags = ["nature", "garden", "food"]
        elif "ST" in mbti:  # 务实高效型
            tags = ["landmark", "imperial"]
        print(f"  → MBTI 推断 tags: {tags}")
    
    # 默认标签
    if not tags:
        tags = ["history", "culture"]
        print(f"  → 使用默认 tags: {tags}")
    
    print(f"\n✅ 推断结果:")
    print(f"  - Tags: {tags}")
    print(f"  - Zones: {zones}")
    print(f"{'='*60}\n")
    
    return tags, zones


def resolve_candidates_pick_pois(
    selected_poi_ids: List[str],
    allow_auto_fill: bool = False,
    keep_order: bool = True,
    time_budget: str = "half_day"
) -> List[POI]:
    """
    模式1: PICK_POIS - 用户手选景点
    - 严格按照用户选择的 POI ID 返回
    - 如果 allow_auto_fill=True 且数量不足，可以补充推荐（但标记为 recommendation）
    """
    print(f"\n{'='*60}")
    print(f"📍 模式: PICK_POIS (用户手选景点)")
    print(f"{'='*60}")
    print(f"selected_poi_ids: {selected_poi_ids}")
    print(f"allow_auto_fill: {allow_auto_fill}")
    print(f"keep_order: {keep_order}")
    print(f"time_budget: {time_budget}")
    
    if not selected_poi_ids:
        print(f"❌ 错误: selected_poi_ids 为空")
        return []
    
    # 获取用户选择的 POI
    if keep_order:
        # 保持用户选择的顺序
        result = get_pois_by_ids(selected_poi_ids)
    else:
        # 按地理位置优化顺序（北->南）
        pois = get_pois_by_ids(selected_poi_ids)
        result = sorted(pois, key=lambda p: p.lat, reverse=True)
    
    print(f"\n✅ 用户选择的 POI: {len(result)}个")
    for idx, poi in enumerate(result, 1):
        print(f"  {idx}. {poi.id:20s} → {poi.name} (lat={poi.lat}, lon={poi.lon})")
    
    # 检查是否需要补充
    limit = 3 if time_budget == "half_day" else 5
    if allow_auto_fill and len(result) < limit:
        needed = limit - len(result)
        print(f"\n🔄 自动补充: 需要补充 {needed} 个 POI")
        
        # 基于已选POI的tags补充
        existing_tags = set()
        for poi in result:
            existing_tags.update(poi.tags)
        
        # 搜索相似POI
        similar_pois = search_pois_by_tags(list(existing_tags), limit=limit * 2)
        
        # 排除已选POI
        existing_ids = {poi.id for poi in result}
        recommendations = [p for p in similar_pois if p.id not in existing_ids][:needed]
        
        print(f"  → 补充 POI:")
        for idx, poi in enumerate(recommendations, 1):
            print(f"    {idx}. {poi.id:20s} → {poi.name} (推荐)")
        
        # 注意：这里不直接加入result，而是返回时标记为recommendation
        # 在实际应用中，可以分别存储 stops 和 recommendations
    
    print(f"\n📤 最终返回: {len(result)}个 POI")
    print(f"{'='*60}\n")
    
    return result


def resolve_candidates_preset_route(
    preset_route_id: str
) -> List[POI]:
    """
    模式2: PRESET_ROUTE - 预设路线
    - 从预设路线配置中获取 POI 列表
    """
    print(f"\n{'='*60}")
    print(f"🗺️  模式: PRESET_ROUTE (预设路线)")
    print(f"{'='*60}")
    print(f"preset_route_id: {preset_route_id}")
    
    result = get_route_pois(preset_route_id)
    
    if not result:
        print(f"❌ 错误: 未找到路线 '{preset_route_id}'")
        return []
    
    print(f"\n✅ 预设路线 POI: {len(result)}个")
    for idx, poi in enumerate(result, 1):
        print(f"  {idx}. {poi.id:20s} → {poi.name} (lat={poi.lat}, lon={poi.lon})")
    
    print(f"\n📤 最终返回: {len(result)}个 POI")
    print(f"{'='*60}\n")
    
    return result


def resolve_candidates_free_text(
    user_text_input: str,
    mbti: Optional[str] = None,
    time_budget: str = "half_day"
) -> List[POI]:
    """
    模式3: FREE_TEXT - 自然语言输入
    - 从用户输入推断偏好
    - 根据 tags/zones 选择 POI
    """
    print(f"\n{'='*60}")
    print(f"💬 模式: FREE_TEXT (自然语言输入)")
    print(f"{'='*60}")
    
    # 推断偏好
    tags, zones = infer_preferences(user_text_input, mbti, time_budget)
    
    # 搜索匹配POI
    limit = 3 if time_budget == "half_day" else 5
    matched_pois = search_pois_by_tags(tags, limit=limit * 2)
    
    # 如果指定了区域，优先选择该区域的POI
    if zones:
        zone_pois = [p for p in matched_pois if p.zone in zones]
        other_pois = [p for p in matched_pois if p.zone not in zones]
        result = (zone_pois + other_pois)[:limit]
    else:
        result = matched_pois[:limit]
    
    print(f"\n✅ 匹配的 POI: {len(result)}个")
    for idx, poi in enumerate(result, 1):
        print(f"  {idx}. {poi.id:20s} → {poi.name} (zone={poi.zone}, tags={poi.tags})")
    
    print(f"\n📤 最终返回: {len(result)}个 POI")
    print(f"{'='*60}\n")
    
    return result


def build_plan_from_pois(
    pois: List[POI],
    mode: str,
    transportation: str = "walking",
    pace_preference: str = "medium"
) -> Dict:
    """
    从 POI 列表构建完整的 plan
    
    返回格式:
    {
        "mode": mode,
        "stops": [
            {
                "seq": 1,
                "poi_id": "gugong",
                "name": "故宫",
                "lat": 39.9163,
                "lon": 116.3972,
                "category": "imperial",
                "distance_m": 0,
                "visit_duration_min": 180,
                "transit_note": "步行 10 分钟"
            },
            ...
        ],
        "total_duration_min": 360,
        "total_distance_m": 5000,
        "summary": "故宫 -> 天坛 -> 颐和园"
    }
    """
    print(f"\n{'='*60}")
    print(f"🏗️  构建行程计划")
    print(f"{'='*60}")
    print(f"POI 数量: {len(pois)}")
    print(f"模式: {mode}")
    print(f"交通方式: {transportation}")
    
    if not pois:
        print(f"❌ 错误: POI 列表为空")
        return {
            "mode": mode,
            "stops": [],
            "total_duration_min": 0,
            "total_distance_m": 0,
            "summary": "无行程"
        }
    
    stops = []
    total_duration = 0
    total_distance = 0
    
    for idx, poi in enumerate(pois):
        # 计算到下一个点的距离（简化版：基于经纬度估算）
        distance_to_next = 0
        transit_note = "行程结束"
        
        if idx < len(pois) - 1:
            next_poi = pois[idx + 1]
            # 简化距离计算（实际应使用高德API）
            lat_diff = abs(next_poi.lat - poi.lat)
            lon_diff = abs(next_poi.lon - poi.lon)
            distance_to_next = int((lat_diff + lon_diff) * 111000)  # 粗略估算，1度≈111km
            
            # 估算交通时间
            if transportation == "walking":
                transit_time = distance_to_next // 80  # 假设步行速度 80m/min
                transit_note = f"步行 {transit_time} 分钟到下一站"
            else:  # driving
                transit_time = distance_to_next // 400  # 假设驾车速度 400m/min
                transit_note = f"驾车 {transit_time} 分钟到下一站"
            
            total_duration += transit_time
        
        # 构建 stop
        stop = {
            "seq": idx + 1,
            "poi_id": poi.id,
            "name": poi.name,
            "lat": poi.lat,
            "lon": poi.lon,
            "category": poi.category,
            "distance_m": distance_to_next,
            "zone": poi.zone,
            "tags": poi.tags,
            "visit_duration_min": poi.visit_duration_min,
            "transit_note": transit_note,
            "status": "UPCOMING"
        }
        
        stops.append(stop)
        total_duration += poi.visit_duration_min
        total_distance += distance_to_next
    
    # 生成摘要
    summary = " -> ".join([poi.name for poi in pois])
    
    plan = {
        "mode": mode,
        "stops": stops,
        "total_duration_min": total_duration,
        "total_distance_m": total_distance,
        "summary": summary
    }
    
    print(f"\n✅ 行程计划构建完成:")
    print(f"  - 总站点数: {len(stops)}")
    print(f"  - 总时长: {total_duration} 分钟")
    print(f"  - 总距离: {total_distance} 米")
    print(f"  - 摘要: {summary}")
    print(f"{'='*60}\n")
    
    return plan
