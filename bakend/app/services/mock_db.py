from typing import List
from collections import Counter
from ..state import RoutePlan, RouteStep

# 🔥 使用统一的 POI 数据源（不再维护本地 MOCK_DB）
from app.data.pois import (
    POI,
    POIS_LIST,
    POIS_BY_ID,
    get_pois_by_ids,
    search_pois_by_tags
)

# 为了保持兼容性，导出 MOCK_DB（指向统一数据）
MOCK_DB = POIS_LIST


def select_pois(interests: List[str], time_budget: str, selected_poi_ids: List[str] = None) -> List[POI]:
    """
    POI 选择的统一逻辑（支持三种模式）
    
    优先级：
    1. 如果提供 selected_poi_ids，直接按 ID 返回（PICK_POIS 模式）
    2. 否则，分析 interests：
       - 如果 interests 中包含 POI ID，作为用户指定必选点
       - 剩余的作为 tags 进行标签匹配
    3. 按区域聚合，根据 time_budget 限制数量
    
    Args:
        interests: 用户兴趣列表（可能包含 tags 或 POI IDs）
        time_budget: "half_day" | "full_day"
        selected_poi_ids: 用户明确选择的 POI IDs（优先级最高）
    
    Returns:
        List[POI]: 选中的 POI 列表
    """
    print(f"\n{'='*60}")
    print(f"[select_pois] 🎯 开始 POI 选择")
    print(f"{'='*60}")
    print(f"📥 输入 interests: {interests}")
    print(f"📥 输入 time_budget: {time_budget}")
    print(f"📥 输入 selected_poi_ids: {selected_poi_ids}")
    
    # 🔥 模式1: 用户明确选择了 POI IDs（PICK_POIS 模式）
    if selected_poi_ids:
        print(f"\n✨ 模式1: PICK_POIS - 用户明确选择景点")
        result = get_pois_by_ids(selected_poi_ids)
        print(f"✅ 返回用户选择的 {len(result)}个 POI:")
        for poi in result:
            print(f"   - {poi.id:20s} → {poi.name}")
        print(f"{'='*60}\n")
        return result
    
    # 2. 分离用户指定的 POI ID 和 tags
    user_selected_pois = []  # 用户明确指定的 POI（按 ID 匹配）
    remaining_tags = []      # 剩余的作为 tags
    seen_poi_ids = set()     # 去重
    
    print(f"\n🔍 分析 interests 中的每一项:")
    for idx, item in enumerate(interests):
        if item in POIS_BY_ID:
            # 匹配到 POI ID，加入必选点
            poi = POIS_BY_ID[item]
            if poi.id not in seen_poi_ids:
                user_selected_pois.append(poi)
                seen_poi_ids.add(poi.id)
                print(f"   [{idx}] ✅ '{item}' → 匹配到 POI: {poi.name}")
            else:
                print(f"   [{idx}] ⚠️  '{item}' → 重复的 POI ID，已跳过")
        else:
            # 当作 tag 处理
            remaining_tags.append(item)
            print(f"   [{idx}] 🏷️  '{item}' → 作为 tag 处理")
    
    print(f"\n📊 分析结果:")
    print(f"   - 用户指定的 POI: {len(user_selected_pois)}个")
    if user_selected_pois:
        for poi in user_selected_pois:
            print(f"     • {poi.id} ({poi.name})")
    print(f"   - 剩余的 tags: {len(remaining_tags)}个 → {remaining_tags}")
    
    # 3. 根据 remaining_tags 进行标签匹配，扩展推荐点
    tag_matched_pois = []
    if remaining_tags:
        print(f"\n🔎 开始标签匹配 (tags: {remaining_tags}):")
        for poi in MOCK_DB:
            if poi.id not in seen_poi_ids:  # 避免重复
                matched_tags = [tag for tag in remaining_tags if tag in poi.tags]
                if matched_tags:
                    tag_matched_pois.append(poi)
                    seen_poi_ids.add(poi.id)
                    print(f"   ✅ {poi.id:20s} ({poi.name:15s}) 匹配 tags: {matched_tags}")
        print(f"   📈 标签匹配到 {len(tag_matched_pois)} 个 POI")
    
    # 4. 合并：用户指定 + 标签匹配
    all_matched_pois = user_selected_pois + tag_matched_pois
    print(f"\n📦 合并结果: {len(all_matched_pois)}个 POI (用户指定 {len(user_selected_pois)} + 标签匹配 {len(tag_matched_pois)})")
    
    # 5. Fallback：如果完全没有匹配，返回热门景点
    if not all_matched_pois:
        print(f"⚠️  警告: 没有任何匹配的 POI，使用默认热门景点")
        fallback = MOCK_DB[:3]
        print(f"📤 最终返回: {[p.name for p in fallback]}")
        print(f"{'='*60}\n")
        return fallback
    
    # 6. 如果只有用户指定的 POI（没有 tag 匹配），且数量 >= 1，直接返回
    if user_selected_pois and not tag_matched_pois:
        limit = 3 if time_budget == "half_day" else 5
        result = user_selected_pois[:limit]
        print(f"✅ 只有用户指定的 POI，直接返回 (limit={limit})")
        print(f"📤 最终返回: {[p.name for p in result]}")
        print(f"{'='*60}\n")
        return result
    
    # 7. Zone Clustering：根据区域聚合，优化路线
    zone_counts = Counter([p.zone for p in all_matched_pois])
    print(f"\n🗺️  区域分布: {dict(zone_counts)}")
    
    if time_budget == "half_day":
        # 半天行程：选择单个最佳区域
        # 优先保留用户指定的 POI 所在区域
        if user_selected_pois:
            user_zones = Counter([p.zone for p in user_selected_pois])
            best_zone = user_zones.most_common(1)[0][0]
            print(f"   - half_day: 用户指定POI的主要区域 → {best_zone}")
        else:
            best_zone = zone_counts.most_common(1)[0][0]
            print(f"   - half_day: 最热门区域 → {best_zone}")
        
        # 先加入用户指定的 POI（不受区域限制）
        selected_pois = [p for p in user_selected_pois]
        # 再从同区域的 tag 匹配点中补充
        selected_pois += [p for p in tag_matched_pois if p.zone == best_zone]
        limit = 3
    else:  # full_day
        # 全天行程：选择 2 个最佳区域
        if user_selected_pois:
            user_zones = Counter([p.zone for p in user_selected_pois])
            # 优先包含用户指定 POI 的区域
            top_zones = [z[0] for z in user_zones.most_common(2)]
            # 如果用户只选了一个区域的 POI，补充第二个热门区域
            if len(top_zones) < 2:
                remaining_zones = [z[0] for z in zone_counts.most_common(3) if z[0] not in top_zones]
                top_zones += remaining_zones[:2 - len(top_zones)]
            print(f"   - full_day: 用户指定POI的主要区域 → {top_zones}")
        else:
            top_zones = [z[0] for z in zone_counts.most_common(2)]
            print(f"   - full_day: 最热门区域 → {top_zones}")
        
        # 先加入用户指定的 POI
        selected_pois = [p for p in user_selected_pois]
        # 再从选定区域的 tag 匹配点中补充
        selected_pois += [p for p in tag_matched_pois if p.zone in top_zones]
        limit = 5
    
    print(f"\n🎯 应用区域聚合后: {len(selected_pois)}个 POI (limit={limit})")
    
    # 8. 去重并截断
    final_pois = []
    final_ids = set()
    for poi in selected_pois:
        if poi.id not in final_ids:
            final_pois.append(poi)
            final_ids.add(poi.id)
        if len(final_pois) >= limit:
            break
    
    # 9. 确保至少返回 1 个 POI（避免空 stops）
    if not final_pois:
        print(f"⚠️  警告: 最终结果为空，使用默认POI")
        final_pois = MOCK_DB[:1]
    
    print(f"\n✅ 最终选择 {len(final_pois)}个 POI:")
    for idx, poi in enumerate(final_pois, 1):
        print(f"   {idx}. {poi.id:20s} → {poi.name:15s} (zone={poi.zone}, tags={poi.tags})")
    print(f"{'='*60}\n")
    
    return final_pois

def sort_route(pois: List[POI]) -> RoutePlan:
    # Simple TSP: Sort by Latitude (North -> South)
    sorted_pois = sorted(pois, key=lambda p: p.lat, reverse=True)
    
    steps = []
    total_duration = 0
    
    for i, poi in enumerate(sorted_pois):
        duration = 60 # Mock 1 hour per spot
        transit = "步行 10 分钟" if i < len(sorted_pois) - 1 else "行程结束"
        
        steps.append(RouteStep(
            poi=poi,
            visit_duration=duration,
            transit_note=transit
        ))
        total_duration += duration + 10
        
    summary = " -> ".join([p.name for p in sorted_pois])
    
    return RoutePlan(
        steps=steps,
        total_duration=total_duration,
        total_distance=0, # Mock distance
        summary=summary
    )
