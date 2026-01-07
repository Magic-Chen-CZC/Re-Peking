import os
import sys
import time
import json
from dotenv import load_dotenv

# Load env vars first
load_dotenv()
print(f"DEBUG: AMAP_API_KEY from env: {os.getenv('AMAP_API_KEY')}")

# Ensure app modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.map_service import amap_service
from app.services.rag_service import rag_service

REAL_BEIJING_DATA = [
    {
        "id": "gugong",
        "name": "故宫博物院",
        "zone": "center",
        "tags": ["history", "royal", "architecture"],
        "description": "故宫博物院，旧称为紫禁城，位于北京中轴线的中心，是中国明、清两代24位皇帝的皇家宫殿，是中国古代汉族宫廷建筑之精华，无与伦比的建筑杰作，也是世界上现存规模最大、保存乃至最完整的木结构古建筑之一。它有大小宫殿七十多座，房屋九千余间，以太和、中和、保和三大殿为中心。"
    },
    {
        "id": "tiantan",
        "name": "天坛公园",
        "zone": "center",
        "tags": ["history", "royal", "ritual"],
        "description": "天坛，在北京市南部，东城区永定门内大街东侧。占地约273万平方米。天坛始建于明永乐十八年（1420年），清乾隆、光绪时曾重修改建。为明、清两代帝王祭祀皇天、祈五谷丰登之场所。天坛是圜丘、祈谷两坛的总称，有坛墙两重，形成内外坛，坛墙南方北圆，象征天圆地方。"
    },
    {
        "id": "yiheyuan",
        "name": "颐和园",
        "zone": "haidian",
        "tags": ["history", "royal", "garden", "nature"],
        "description": "颐和园，中国清朝时期皇家园林，前身为清漪园，坐落在北京西郊，距城区15公里，占地约290公顷，与圆明园毗邻。它是以昆明湖、万寿山为基址，按照江南园林的设计手法建造，是保存最完整的一座皇家行宫御苑，被誉为“皇家园林博物馆”。"
    },
    {
        "id": "nanluoguxiang",
        "name": "南锣鼓巷",
        "zone": "center",
        "tags": ["hutong", "food", "crowded", "history"],
        "description": "南锣鼓巷是一条胡同，位于北京中轴线东侧的交道口地区，北起鼓楼东大街，南至平安大街，宽8米，全长787米，于元大都同期建成。是北京最古老的街区之一，至今已有740多年的历史。也位列规划中的25片旧城保护区之中。"
    },
    {
        "id": "798_art",
        "name": "798艺术区",
        "zone": "chaoyang",
        "tags": ["art", "modern", "photo"],
        "description": "798艺术区位于北京朝阳区酒仙桥街道大山子地区，故又称大山子艺术区，原为原国营798厂等电子工业的老厂区所在地。如今798已经引起了国内外媒体和大众的广泛关注，成为了北京都市文化的新地标。"
    },
    {
        "id": "yonghegong",
        "name": "雍和宫",
        "zone": "center",
        "tags": ["history", "buddhism", "mystic"],
        "description": "雍和宫（The Lama Temple），位于北京市区东北角，清康熙三十三年（1694年），康熙帝在此建造府邸、赐予四子雍亲王，称雍亲王府。雍正三年（1725年），改王府为行宫，称雍和宫。雍和宫是北京市内最大的藏传佛教寺院。"
    },
    {
        "id": "badaling",
        "name": "八达岭长城",
        "zone": "suburb",
        "tags": ["history", "hiking", "nature"],
        "description": "八达岭长城，位于北京市延庆区军都山关沟古道北口。是中国古代伟大的防御工程万里长城的重要组成部分，是明长城的一个隘口。八达岭长城为居庸关的重要前哨，古称“居庸之险不在关而在八达岭”。"
    },
    {
        "id": "universal_studios",
        "name": "北京环球度假区",
        "zone": "tongzhou",
        "tags": ["theme_park", "family", "entertainment"],
        "description": "北京环球度假区（Universal Beijing Resort），位于北京市通州区，是亚洲第三座、全球第五座环球影城主题公园。包含七大主题景区、37个骑乘设施及地标景点，以及24个精彩纷呈的娱乐演出。"
    },
    {
        "id": "sanlitun",
        "name": "三里屯太古里",
        "zone": "chaoyang",
        "tags": ["shopping", "modern", "fashion"],
        "description": "三里屯太古里位于北京市朝阳区工人体育场北路甲6号，是北京最具时尚气息的商业街区之一。这里汇聚了众多国际一线品牌旗舰店、潮流买手店以及特色餐饮，是年轻人购物、休闲、娱乐的首选之地。"
    },
    {
        "id": "shichahai",
        "name": "什刹海",
        "zone": "center",
        "tags": ["history", "lake", "bar", "nightlife"],
        "description": "什刹海，是北京市历史文化旅游风景区、北京市历史文化保护区。位于市中心城区西城区，毗邻北京城中轴线。水域面积33.6万平方米，与中南海水域一脉相连，是北京内城唯一一处具有开阔水面的开放型景区，也是北京城内面积最大、风貌保存最完整的一片历史街区。"
    },
    {
        "id": "olympic_park",
        "name": "奥林匹克公园",
        "zone": "chaoyang",
        "tags": ["modern", "sports", "architecture"],
        "description": "北京奥林匹克公园位于北京市朝阳区，地处北京城中轴线北端。是2008年北京奥运会的主要举办地，拥有鸟巢（国家体育场）、水立方（国家游泳中心）等标志性建筑。"
    },
    {
        "id": "beihai",
        "name": "北海公园",
        "zone": "center",
        "tags": ["history", "royal", "garden", "lake"],
        "description": "北海公园，位于北京市中心区，城内景山西侧，在故宫的西北面，与中海、南海合称三海。属于中国古代皇家园林。全园以北海为中心，面积约71公顷，水面占583市亩，陆地占480市亩。这里原是辽、金、元建离宫，明、清辟为帝王御苑。"
    },
    {
        "id": "national_museum",
        "name": "中国国家博物馆",
        "zone": "center",
        "tags": ["history", "museum", "culture"],
        "description": "中国国家博物馆，位于北京市中心天安门广场东侧，东长安街南侧，与人民大会堂东西相对称，是代表国家收藏、研究、展示、阐释能够充分反映中华优秀传统文化、革命文化和社会主义先进文化代表性物证的最高机构。"
    },
    {
        "id": "wudaoying",
        "name": "五道营胡同",
        "zone": "center",
        "tags": ["hutong", "cafe", "quiet", "art"],
        "description": "五道营胡同位于东城区北部，安定门立交桥东南侧，东起雍和宫大街，西止安定门内大街。全长632米，宽6米。如今这里已经成为北京最新兴的小资文艺聚集地，各种特色咖啡馆、餐厅、创意小店林立。"
    },
    {
        "id": "jingshan",
        "name": "景山公园",
        "zone": "center",
        "tags": ["history", "royal", "view", "nature"],
        "description": "景山公园，位于北京市西城区景山前街，坐落在明清北京城的中轴线上，西临北海，南与故宫神武门隔街相望，是明、清两代的御苑。公园中心的景山，曾是全城的制高点。登上万春亭，可俯瞰故宫全景。"
    },
    {
        "id": "gongwangfu",
        "name": "恭王府",
        "zone": "center",
        "tags": ["history", "royal", "architecture"],
        "description": "恭王府，位于北京市西城区柳荫街，是清代规模最大的一座王府，曾先后作为和珅、永璘的宅邸。1851年恭亲王奕訢成为宅子主人，恭王府的名称也因此得来。恭王府历经了清王朝由鼎盛而至衰亡的历史进程，承载了极其丰富的历史文化信息，故有了“一座恭王府，半部清代史”的说法。"
    },
    {
        "id": "zoo",
        "name": "北京动物园",
        "zone": "xicheng",
        "tags": ["family", "nature", "animals"],
        "description": "北京动物园位于北京市西城区西直门外大街，占地面积约86公顷，水面8.6公顷。始建于清光绪三十二年（1906年），是中国开放最早、饲养展出动物种类最多的动物园。园内有大熊猫馆等知名场馆。"
    },
    {
        "id": "summer_palace_ruins",
        "name": "圆明园遗址公园",
        "zone": "haidian",
        "tags": ["history", "royal", "ruins", "nature"],
        "description": "圆明园，中国清代大型皇家园林，位于北京市海淀区，由圆明园、长春园和绮春园组成，所以也称为圆明三园。占地面积3.5平方千米，建筑面积达20万平方米，一百五十余景，有“万园之园”之称。1860年被英法联军洗劫焚毁，现为遗址公园。"
    },
    {
        "id": "fragrant_hills",
        "name": "香山公园",
        "zone": "haidian",
        "tags": ["nature", "hiking", "autumn"],
        "description": "香山公园，位于北京市海淀区买卖街40号，北京市区西北郊，占地188公顷，是一座具有山林特色的皇家园林。景区内主峰香炉峰俗称“鬼见愁”，海拔575米。香山红叶是北京秋季最著名的景观之一。"
    },
    {
        "id": "happy_valley",
        "name": "北京欢乐谷",
        "zone": "chaoyang",
        "tags": ["theme_park", "entertainment", "thrill"],
        "description": "北京欢乐谷是国家4A级旅游景区、新北京十六景、北京文化创意产业基地，由华侨城集团创办，是集国际化、现代化的主题公园。位于朝阳区东四环四方桥东南角，占地56万平方米。"
    }
]

def run_seed():
    print("🚀 Starting Data Seeding Process...")
    
    # Step 1: Enrich Coordinates
    enriched_data = []
    print("\n📍 Step 1: Fetching Coordinates from AMap...")
    
    for item in REAL_BEIJING_DATA:
        name = item["name"]
        print(f"   Querying: {name}...", end=" ")
        
        coords = amap_service.get_coordinates(name)
        
        if coords:
            lat, lon = coords
            item["lat"] = lat
            item["lon"] = lon
            enriched_data.append(item)
            print(f"✅ ({lat:.4f}, {lon:.4f})")
        else:
            print("❌ Failed (Skipping)")
            
        # Rate limiting
        time.sleep(0.2)
        
    print(f"\n✨ Successfully enriched {len(enriched_data)} POIs.")
    
    # Step 2: Build RAG Index
    print("\n📚 Step 2: Building and Persisting RAG Index...")
    
    rag_input_data = []
    for item in enriched_data:
        # Construct text for RAG
        # We can combine description with basic info
        text = f"{item['name']} ({item['zone']})\n{item['description']}"
        rag_input_data.append({
            "id": item["name"], # Use name as ID for retrieval matching
            "text": text,
            "tags": item["tags"]
        })
        
    rag_service.build_from_data(rag_input_data)
    print("✅ RAG Index built and saved.")
    
    # Step 3: Generate Mock DB Code
    print("\n💾 Step 3: Generating app/services/mock_db.py...")
    
    mock_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "services", "mock_db.py")
    
    # Read existing content to preserve imports and functions
    # Actually, the user asked to overwrite the list but keep functions.
    # To be safe and simple, we will rewrite the file with the new list and the SAME functions as before.
    # We can hardcode the functions here since we know them.
    
    file_content = f"""from typing import List
from collections import Counter
from ..state import POI, RoutePlan, RouteStep

# Auto-generated by scripts/seed_data.py
MOCK_DB = [
"""
    
    for item in enriched_data:
        file_content += f'    POI(id="{item["id"]}", name="{item["name"]}", lat={item["lat"]}, lon={item["lon"]}, tags={item["tags"]}, zone="{item["zone"]}"),\n'
        
    file_content += """]

def select_pois(interests: List[str], time_budget: str) -> List[POI]:
    # 1. Tag Filtering
    matched_pois = []
    for poi in MOCK_DB:
        # Check intersection of tags
        if any(tag in interests for tag in poi.tags):
            matched_pois.append(poi)
            
    if not matched_pois:
        # Fallback: return top 3 popular ones if no match
        return MOCK_DB[:3]
        
    # 2. Zone Clustering
    zone_counts = Counter([p.zone for p in matched_pois])
    
    if not zone_counts:
         return MOCK_DB[:3]

    if time_budget == "half_day":
        # Pick single best zone
        best_zone = zone_counts.most_common(1)[0][0]
        selected_pois = [p for p in matched_pois if p.zone == best_zone]
        limit = 3
    else: # full_day
        # Pick top 2 zones
        top_zones = [z[0] for z in zone_counts.most_common(2)]
        selected_pois = [p for p in matched_pois if p.zone in top_zones]
        limit = 5
        
    # 3. Truncate
    return selected_pois[:limit]

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
        summary=summary
    )
"""

    with open(mock_db_path, "w") as f:
        f.write(file_content)
        
    print(f"✅ Updated {mock_db_path}")
    print("\n🎉 Seeding Complete!")

if __name__ == "__main__":
    run_seed()
