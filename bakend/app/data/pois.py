"""POI 数据模型和预设路线配置"""
from typing import List, Dict, Optional
from pydantic import BaseModel


class POI(BaseModel):
    """POI 点位信息"""
    id: str  # POI ID，如 gugong, tiantan
    name: str
    lat: float
    lon: float
    category: str
    tags: List[str] = []
    zone: str = "central"  # central, north, west, east
    image_key: Optional[str] = None
    description: Optional[str] = None
    visit_duration_min: int = 60  # 默认参观时长（分钟）


class PresetRoute(BaseModel):
    """预设路线"""
    id: str
    name: str
    desc: str
    poi_ids: List[str]  # 按顺序排列的 POI ID


# ========== POI 数据库（内存版） ==========
POIS_DB: Dict[str, POI] = {
    # 京城名胜
    "gugong": POI(
        id="gugong",
        name="故宫",
        lat=39.9163,
        lon=116.3972,
        category="imperial",
        tags=["history", "architecture", "imperial"],
        zone="central",
        image_key="gugong",
        visit_duration_min=180
    ),
    "tiantan": POI(
        id="tiantan",
        name="天坛",
        lat=39.8828,
        lon=116.4074,
        category="temple",
        tags=["history", "architecture", "temple"],
        zone="central",
        image_key="tiantan",
        visit_duration_min=90
    ),
    "tiananmen": POI(
        id="tiananmen",
        name="天安门",
        lat=39.9075,
        lon=116.3914,
        category="landmark",
        tags=["history", "landmark"],
        zone="central",
        image_key="tiananmen",
        visit_duration_min=30
    ),
    "yiheyuan": POI(
        id="yiheyuan",
        name="颐和园",
        lat=39.9998,
        lon=116.2755,
        category="garden",
        tags=["garden", "nature", "imperial"],
        zone="west",
        image_key="yiheyuan",
        visit_duration_min=180
    ),
    "changcheng": POI(
        id="changcheng",
        name="长城",
        lat=40.4319,
        lon=116.5704,
        category="landmark",
        tags=["history", "landmark", "nature"],
        zone="north",
        image_key="changcheng",
        visit_duration_min=240
    ),
    "yuanmingyuan": POI(
        id="yuanmingyuan",
        name="圆明园",
        lat=40.0077,
        lon=116.2951,
        category="garden",
        tags=["history", "garden", "imperial"],
        zone="west",
        image_key="yuanmingyuan",
        visit_duration_min=120
    ),
    "ditan": POI(
        id="ditan",
        name="地坛",
        lat=39.9483,
        lon=116.4071,
        category="temple",
        tags=["temple", "park"],
        zone="north",
        image_key="ditan",
        visit_duration_min=60
    ),
    "zhongshan": POI(
        id="zhongshan",
        name="中山公园",
        lat=39.9094,
        lon=116.3892,
        category="park",
        tags=["park", "nature"],
        zone="central",
        image_key="zhongshan",
        visit_duration_min=45
    ),
    "shejitan": POI(
        id="shejitan",
        name="社稷坛",
        lat=39.9089,
        lon=116.3883,
        category="temple",
        tags=["temple", "history"],
        zone="central",
        image_key="shejitan",
        visit_duration_min=30
    ),
    
    # 京华墨韵
    "guozijian": POI(
        id="guozijian",
        name="国子监",
        lat=39.9488,
        lon=116.4109,
        category="culture",
        tags=["culture", "history", "education"],
        zone="north",
        image_key="guozijian",
        visit_duration_min=60
    ),
    "kongmiao": POI(
        id="kongmiao",
        name="孔庙",
        lat=39.9491,
        lon=116.4106,
        category="temple",
        tags=["culture", "history", "temple"],
        zone="north",
        image_key="kongmiao",
        visit_duration_min=60
    ),
    "liulichang": POI(
        id="liulichang",
        name="琉璃厂",
        lat=39.8944,
        lon=116.3731,
        category="culture",
        tags=["culture", "art", "shopping"],
        zone="central",
        image_key="liulichang",
        visit_duration_min=90
    ),
    "nanluogu": POI(
        id="nanluogu",
        name="南锣鼓巷",
        lat=39.9370,
        lon=116.4029,
        category="hutong",
        tags=["culture", "hutong", "shopping"],
        zone="central",
        image_key="nanluogu",
        visit_duration_min=90
    ),
    "shichahai": POI(
        id="shichahai",
        name="什刹海",
        lat=39.9390,
        lon=116.3861,
        category="nature",
        tags=["nature", "hutong", "culture"],
        zone="central",
        image_key="shichahai",
        visit_duration_min=120
    ),
    "houhai": POI(
        id="houhai",
        name="后海",
        lat=39.9380,
        lon=116.3823,
        category="nature",
        tags=["nature", "bar", "culture"],
        zone="central",
        image_key="houhai",
        visit_duration_min=90
    ),
    "yandaixie": POI(
        id="yandaixie",
        name="烟袋斜街",
        lat=39.9408,
        lon=116.3875,
        category="hutong",
        tags=["culture", "hutong", "shopping"],
        zone="central",
        image_key="yandaixie",
        visit_duration_min=60
    ),
    
    # 京祀胜迹
    "lama": POI(
        id="lama",
        name="雍和宫",
        lat=39.9486,
        lon=116.4188,
        category="temple",
        tags=["temple", "buddhism", "architecture"],
        zone="north",
        image_key="lama",
        visit_duration_min=90
    ),
    "biyun": POI(
        id="biyun",
        name="碧云寺",
        lat=40.0028,
        lon=116.1919,
        category="temple",
        tags=["temple", "buddhism", "nature"],
        zone="west",
        image_key="biyun",
        visit_duration_min=90
    ),
    "tanzhe": POI(
        id="tanzhe",
        name="潭柘寺",
        lat=39.9458,
        lon=115.9817,
        category="temple",
        tags=["temple", "buddhism", "history"],
        zone="west",
        image_key="tanzhe",
        visit_duration_min=120
    ),
    "fayuan": POI(
        id="fayuan",
        name="法源寺",
        lat=39.8883,
        lon=116.3711,
        category="temple",
        tags=["temple", "buddhism", "culture"],
        zone="central",
        image_key="fayuan",
        visit_duration_min=60
    ),
    "jietai": POI(
        id="jietai",
        name="戒台寺",
        lat=39.9322,
        lon=116.0117,
        category="temple",
        tags=["temple", "buddhism", "history"],
        zone="west",
        image_key="jietai",
        visit_duration_min=90
    ),
    
    # 和合圣境
    "baiyun": POI(
        id="baiyun",
        name="白云观",
        lat=39.8828,
        lon=116.3525,
        category="temple",
        tags=["temple", "taoism", "culture"],
        zone="central",
        image_key="baiyun",
        visit_duration_min=60
    ),
    "dongyue": POI(
        id="dongyue",
        name="东岳庙",
        lat=39.9264,
        lon=116.4472,
        category="temple",
        tags=["temple", "taoism", "culture"],
        zone="east",
        image_key="dongyue",
        visit_duration_min=60
    ),
    "niujie": POI(
        id="niujie",
        name="牛街礼拜寺",
        lat=39.8822,
        lon=116.3586,
        category="mosque",
        tags=["temple", "islam", "culture"],
        zone="central",
        image_key="niujie",
        visit_duration_min=45
    ),
    "guangji": POI(
        id="guangji",
        name="广济寺",
        lat=39.9178,
        lon=116.3694,
        category="temple",
        tags=["temple", "buddhism", "culture"],
        zone="central",
        image_key="guangji",
        visit_duration_min=45
    ),
    
    # 补充景点
    "jingshan": POI(
        id="jingshan",
        name="景山公园",
        lat=39.9275,
        lon=116.3953,
        category="park",
        tags=["park", "nature", "history"],
        zone="central",
        image_key="jingshan",
        visit_duration_min=60
    ),
    "gulou": POI(
        id="gulou",
        name="鼓楼",
        lat=39.9444,
        lon=116.3933,
        category="landmark",
        tags=["history", "landmark", "culture"],
        zone="central",
        image_key="gulou",
        visit_duration_min=45
    ),
    "xiangshan": POI(
        id="xiangshan",
        name="香山",
        lat=39.9917,
        lon=116.1878,
        category="nature",
        tags=["nature", "park", "mountain"],
        zone="west",
        image_key="xiangshan",
        visit_duration_min=180
    ),
    "gui": POI(
        id="gui",
        name="簋街美食",
        lat=39.9389,
        lon=116.4322,
        category="food",
        tags=["food", "spicy", "crayfish", "nightlife"],
        zone="east",
        image_key="gui",
        visit_duration_min=120
    ),
    "huguo": POI(
        id="huguo",
        name="护国寺小吃",
        lat=39.9289,
        lon=116.3733,
        category="food",
        tags=["food", "snack", "traditional", "cheap"],
        zone="central",
        image_key="huguo",
        visit_duration_min=60
    ),
    "wangfujing": POI(
        id="wangfujing",
        name="王府井小吃街",
        lat=39.9139,
        lon=116.4108,
        category="food",
        tags=["food", "snack", "shopping", "tourist"],
        zone="central",
        image_key="wangfujing",
        visit_duration_min=90
    ),
    "quanjude": POI(
        id="quanjude",
        name="全聚德烤鸭",
        lat=39.9041,
        lon=116.4119,
        category="food",
        tags=["food", "beijing_cuisine", "duck", "famous"],
        zone="central",
        image_key="quanjude",
        visit_duration_min=90
    ),
    "donglaishun": POI(
        id="donglaishun",
        name="东来顺涮肉",
        lat=39.9252,
        lon=116.4071,
        category="food",
        tags=["food", "hotpot", "mutton", "famous"],
        zone="central",
        image_key="donglaishun",
        visit_duration_min=90
    ),
    "luzhu": POI(
        id="luzhu",
        name="卤煮火烧",
        lat=39.8951,
        lon=116.3759,
        category="food",
        tags=["food", "traditional", "cheap", "local"],
        zone="central",
        image_key="luzhu",
        visit_duration_min=45
    ),
    
    # 岁时庙会
    "ditan_mh": POI(
        id="ditan_mh",
        name="地坛庙会",
        lat=39.9483,
        lon=116.4071,
        category="festival",
        tags=["festival", "temple_fair", "traditional", "spring"],
        zone="central",
        image_key="ditan_mh",
        visit_duration_min=120
    ),
    "longtan": POI(
        id="longtan",
        name="龙潭庙会",
        lat=39.8790,
        lon=116.4344,
        category="festival",
        tags=["festival", "temple_fair", "traditional", "spring"],
        zone="east",
        image_key="longtan",
        visit_duration_min=120
    ),
    "changdian": POI(
        id="changdian",
        name="厂甸庙会",
        lat=39.8957,
        lon=116.3735,
        category="festival",
        tags=["festival", "temple_fair", "traditional", "culture"],
        zone="central",
        image_key="changdian",
        visit_duration_min=120
    ),
    "baiyun_mh": POI(
        id="baiyun_mh",
        name="白云观庙会",
        lat=39.8828,
        lon=116.3525,
        category="festival",
        tags=["festival", "temple_fair", "taoism", "spring"],
        zone="central",
        image_key="baiyun_mh",
        visit_duration_min=120
    ),
}


# ========== 预设路线配置 ==========
PRESET_ROUTES: Dict[str, PresetRoute] = {
    "zhongzhou": PresetRoute(
        id="zhongzhou",
        name="中轴线一日游",
        desc="故宫-天安门-景山-鼓楼",
        poi_ids=["tiananmen", "gugong", "jingshan", "gulou"]
    ),
    "hutong": PresetRoute(
        id="hutong",
        name="胡同深度游",
        desc="南锣鼓巷-什刹海-烟袋斜街",
        poi_ids=["nanluogu", "shichahai", "yandaixie"]
    ),
    "royal": PresetRoute(
        id="royal",
        name="皇家园林游",
        desc="颐和园-圆明园-香山",
        poi_ids=["yiheyuan", "yuanmingyuan", "xiangshan"]
    ),
    "temple": PresetRoute(
        id="temple",
        name="古刹祈福游",
        desc="雍和宫-潭柘寺-戒台寺",
        poi_ids=["lama", "tanzhe", "jietai"]
    ),
    "culture": PresetRoute(
        id="culture",
        name="文化探索游",
        desc="国子监-孔庙-琉璃厂",
        poi_ids=["guozijian", "kongmiao", "liulichang"]
    ),
    "food": PresetRoute(
        id="food",
        name="美食寻味游",
        desc="簋街-护国寺-王府井",
        poi_ids=["gui", "huguo", "wangfujing"]
    )
}


# ========== 辅助函数 ==========
def get_poi_by_id(poi_id: str) -> Optional[POI]:
    """根据 ID 获取 POI"""
    return POIS_DB.get(poi_id)


def get_pois_by_ids(poi_ids: List[str]) -> List[POI]:
    """根据 ID 列表获取 POI 列表（保持顺序）"""
    result = []
    for poi_id in poi_ids:
        poi = get_poi_by_id(poi_id)
        if poi:
            result.append(poi)
    return result


def get_route_pois(route_id: str) -> List[POI]:
    """根据预设路线 ID 获取 POI 列表"""
    route = PRESET_ROUTES.get(route_id)
    if not route:
        return []
    return get_pois_by_ids(route.poi_ids)


def search_pois_by_tags(tags: List[str], limit: int = 5) -> List[POI]:
    """根据标签搜索 POI"""
    matched_pois = []
    for poi in POIS_DB.values():
        # 计算匹配度
        match_score = sum(1 for tag in tags if tag in poi.tags)
        if match_score > 0:
            matched_pois.append((poi, match_score))
    
    # 按匹配度排序
    matched_pois.sort(key=lambda x: x[1], reverse=True)
    
    return [poi for poi, _ in matched_pois[:limit]]


# ========== 统一数据导出（供其他模块使用） ==========
# 提供 List 和 Dict 两种访问方式
POIS_LIST: List[POI] = list(POIS_DB.values())
POIS_BY_ID: Dict[str, POI] = POIS_DB

__all__ = [
    'POI',
    'PresetRoute',
    'POIS_DB',
    'POIS_LIST',
    'POIS_BY_ID',
    'PRESET_ROUTES',
    'get_poi_by_id',
    'get_pois_by_ids',
    'get_route_pois',
    'search_pois_by_tags'
]
