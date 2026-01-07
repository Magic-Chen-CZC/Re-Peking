// 引入高德地图 SDK
var amapFile = require('../../libs/amap-wx.130.js');
const { API_BASE_URL } = require('../../utils/config.js');
const {
    checkLocationPermission,
    buildOptimizedRoute
} = require('../../utils/geoUtils.js');

const MOCK_DETAILS = {
    '798': {
        detailTitle: '798艺术区',
        detailIntro: '工业遗存改造而来的当代艺术聚落，画廊与工作室并置。',
        detailQuote: '“粗粝的厂房骨架，是当代视觉语言的底色。”',
        detailBody: [
            '红砖与锯齿屋顶形成强烈的时代质感，适合拍摄冷暖对比。',
            '建议沿主街步行，留意涂鸦墙与小型展览空间的更新。',
            '傍晚光线更柔和，适合记录街区的空间秩序。'
        ]
    },
    baiyun: {
        detailTitle: '白云观',
        detailIntro: '北京著名道观，氛围清静，香火绵延。',
        detailQuote: '“清风拂面，观内自有秩序与节律。”',
        detailBody: [
            '山门与主殿轴线清晰，视觉层层推进。',
            '可留意道教纹饰与木构件细部。',
            '建议缓步游览，体验空间的静谧感。'
        ]
    },
    baiyun_mh: {
        detailTitle: '白云观庙会',
        detailIntro: '民俗氛围浓厚的庙会场景，节庆感强。',
        detailQuote: '“人流与香火，构成最生动的年景。”',
        detailBody: [
            '庙会多在节庆时段开放，热闹但不失秩序。',
            '摊位与表演区分布密集，适合抓拍人文瞬间。',
            '注意高峰时段的动线与安全。'
        ]
    },
    baiyunguan: {
        detailTitle: '白云观',
        detailIntro: '北京道教名观之一，院落层层递进。',
        detailQuote: '“院落深处，藏着一座城的慢节奏。”',
        detailBody: [
            '空间组织清晰，适合观察传统宗教建筑布局。',
            '建议留意檐下题刻与石刻细节。',
            '可在侧院停留，感受安静的氛围。'
        ]
    },
    beihai: {
        detailTitle: '北海公园',
        detailIntro: '皇家园林代表，湖景与亭台交织。',
        detailQuote: '“水面与白塔，构成城市中的静景。”',
        detailBody: [
            '湖心岛与白塔形成视觉焦点，适合远景取景。',
            '沿湖步道视角开阔，适合慢步游览。',
            '傍晚风景更柔和，适合拍摄倒影。'
        ]
    },
    biyun: {
        detailTitle: '碧云寺',
        detailIntro: '西山古寺，山门幽深，气质古朴。',
        detailQuote: '“山寺不语，石阶自有回声。”',
        detailBody: [
            '建筑依山而建，步行节奏缓慢上升。',
            '香火与松柏形成独特氛围。',
            '适合体验清静与山野气息。'
        ]
    },
    botanical: {
        detailTitle: '国家植物园',
        detailIntro: '植物展示与科普结合的城市绿洲。',
        detailQuote: '“每一片叶子都有一段微小叙事。”',
        detailBody: [
            '园区面积大，建议分区缓慢游览。',
            '温室与林地风格差异明显。',
            '春秋季色彩层次更丰富。'
        ]
    },
    changcheng: {
        detailTitle: '长城',
        detailIntro: '宏大防御体系遗迹，地形与线条极具张力。',
        detailQuote: '“山脊上的线，是历史留下的呼吸。”',
        detailBody: [
            '起伏地形带来强烈的视觉纵深。',
            '建议选择人少时段，感受空间尺度。',
            '风大注意保暖与安全。'
        ]
    },
    changdian: {
        detailTitle: '厂甸庙会',
        detailIntro: '传统市集与民俗表演并存的节庆场景。',
        detailQuote: '“年味在摊位间流动。”',
        detailBody: [
            '人流密集，适合街拍记录。',
            '注意庙会期间的开闭市时间。',
            '可寻找特色老字号摊位。'
        ]
    },
    ditan: {
        detailTitle: '地坛',
        detailIntro: '明清皇家祭坛之一，空间开阔有序。',
        detailQuote: '“坛域之中，秩序是一种庄重。”',
        detailBody: [
            '主坛结构规整，适合观察轴线构图。',
            '公园氛围宁静，适合慢走。',
            '注意石阶与古树细节。'
        ]
    },
    ditan_mh: {
        detailTitle: '地坛庙会',
        detailIntro: '北京人气很高的春节庙会之一。',
        detailQuote: '“鼓点与叫卖声，拼出城市记忆。”',
        detailBody: [
            '民俗表演集中在节庆期间。',
            '建议预留时间逛展与小吃摊。',
            '高峰时段人流较大。'
        ]
    },
    donglaishun: {
        detailTitle: '东来顺涮肉',
        detailIntro: '北京老字号清真涮肉代表。',
        detailQuote: '“一口清汤，最见京味。”',
        detailBody: [
            '经典铜锅与薄切羊肉是特色。',
            '用餐高峰需排队，建议错峰。',
            '适合体验传统老字号氛围。'
        ]
    },
    dongyue: {
        detailTitle: '东岳庙',
        detailIntro: '道教庙宇，文化氛围厚重。',
        detailQuote: '“木影与香气，拉出时间的纹理。”',
        detailBody: [
            '建筑细节丰富，适合近距离观察。',
            '院落分区明确，动线清晰。',
            '适合安静参观与摄影。'
        ]
    },
    fayuan: {
        detailTitle: '法源寺',
        detailIntro: '历史悠久的佛教寺院，气质沉静。',
        detailQuote: '“钟声落下，时间变得柔软。”',
        detailBody: [
            '春季丁香开时最为著名。',
            '院落层次分明，适合慢步。',
            '建议避开节日高峰。'
        ]
    },
    guangji: {
        detailTitle: '广济寺',
        detailIntro: '清净小寺，环境安静。',
        detailQuote: '“一隅之地，自成静场。”',
        detailBody: [
            '规模不大但格局完整。',
            '适合短暂停留与拍照。',
            '注意寺内礼仪与安静氛围。'
        ]
    },
    gugong: {
        detailTitle: '故宫',
        detailIntro: '明清皇宫，轴线严谨，建筑群宏伟。',
        detailQuote: '“秩序与威仪，是这座城的语言。”',
        detailBody: [
            '中轴线空间层层递进，步行体验丰富。',
            '屋脊装饰与彩画细节值得细看。',
            '建议提前规划线路，避开高峰。'
        ]
    },
    gui: {
        detailTitle: '簋街美食',
        detailIntro: '夜间美食街区，烟火气十足。',
        detailQuote: '“香气是这里最直接的导航。”',
        detailBody: [
            '夜晚更热闹，灯光氛围强。',
            '适合尝试特色小龙虾与烤串。',
            '人多时注意排队与交通。'
        ]
    },
    guomao: {
        detailTitle: '国贸',
        detailIntro: 'CBD 核心地段，现代城市感强烈。',
        detailQuote: '“玻璃幕墙反射着城市的节奏。”',
        detailBody: [
            '高楼林立，空间尺度感明显。',
            '适合拍摄夜景与城市线条。',
            '商业氛围浓厚，动线复杂。'
        ]
    },
    guozijian: {
        detailTitle: '国子监',
        detailIntro: '古代最高学府，文化气息浓厚。',
        detailQuote: '“书声虽远，格局仍在。”',
        detailBody: [
            '碑刻与建筑细节适合驻足观赏。',
            '胡同环境清幽，适合漫步。',
            '可与孔庙连线参观。'
        ]
    },
    houhai: {
        detailTitle: '后海',
        detailIntro: '水岸与酒吧街并存的城市休闲区。',
        detailQuote: '“水面将喧闹变得柔和。”',
        detailBody: [
            '傍晚与夜间氛围更突出。',
            '沿湖步行适合观景与拍照。',
            '注意人流密集与交通。'
        ]
    },
    huguo: {
        detailTitle: '护国寺小吃',
        detailIntro: '京味小吃集中地。',
        detailQuote: '“豆汁与驴打滚，是味觉记忆。”',
        detailBody: [
            '适合尝试传统甜点与小吃。',
            '用餐高峰需排队。',
            '可顺路体验胡同文化。'
        ]
    },
    jietai: {
        detailTitle: '戒台寺',
        detailIntro: '古寺与松柏相伴，石阶层层。',
        detailQuote: '“山寺深处，回声更长。”',
        detailBody: [
            '古松与石阶是主要景观。',
            '环境清幽，适合静心游览。',
            '建议预留充分时间。'
        ]
    },
    jingshan: {
        detailTitle: '景山公园',
        detailIntro: '俯瞰故宫全景的最佳地点。',
        detailQuote: '“登高一望，轴线尽收眼底。”',
        detailBody: [
            '登顶视野开阔，适合全景拍摄。',
            '春秋季景色更佳。',
            '台阶较多，注意体力。'
        ]
    },
    kongmiao: {
        detailTitle: '孔庙',
        detailIntro: '祭孔场所，建筑庄重肃穆。',
        detailQuote: '“礼序之地，气息凝重。”',
        detailBody: [
            '碑刻与石坊是主要看点。',
            '适合安静参观。',
            '与国子监毗邻，可连线游览。'
        ]
    },
    lama: {
        detailTitle: '雍和宫',
        detailIntro: '藏传佛教寺院，色彩与香火浓厚。',
        detailQuote: '“金色屋顶在阳光下闪烁。”',
        detailBody: [
            '香火旺盛，游客较多。',
            '建筑色彩对比强烈，适合拍照。',
            '注意保持安静与礼仪。'
        ]
    },
    liulichang: {
        detailTitle: '琉璃厂',
        detailIntro: '古籍与书画集散地，文化气息浓重。',
        detailQuote: '“街巷里藏着纸墨的味道。”',
        detailBody: [
            '店铺密集，适合慢逛。',
            '可寻找老字号文玩店。',
            '适合喜欢传统文化的人群。'
        ]
    },
    longtan: {
        detailTitle: '龙潭庙会',
        detailIntro: '春节庙会之一，民俗活动丰富。',
        detailQuote: '“锣鼓声里是最浓的年味。”',
        detailBody: [
            '表演与摊位集中，节奏热闹。',
            '适合体验传统民俗。',
            '人流密集时注意安全。'
        ]
    },
    luzhu: {
        detailTitle: '卤煮火烧',
        detailIntro: '北京传统小吃，味道浓厚。',
        detailQuote: '“一锅卤煮，撑起烟火气。”',
        detailBody: [
            '口味偏重，适合尝鲜。',
            '推荐搭配豆汁或酸梅汤。',
            '适合小份尝试。'
        ]
    },
    nanluogu: {
        detailTitle: '南锣鼓巷',
        detailIntro: '老北京胡同与文艺小店并存。',
        detailQuote: '“巷子很窄，故事很长。”',
        detailBody: [
            '人流较多，建议清晨或傍晚。',
            '巷内小店丰富，适合闲逛。',
            '注意保护传统街巷秩序。'
        ]
    },
    nanluoguxiang: {
        detailTitle: '南锣鼓巷',
        detailIntro: '胡同肌理清晰，传统与新潮交织。',
        detailQuote: '“在这里，旧时光与新生活同框。”',
        detailBody: [
            '巷内小店密集，适合边走边看。',
            '侧巷更安静，适合拍照。',
            '建议错峰游览。'
        ]
    },
    niujie: {
        detailTitle: '牛街礼拜寺',
        detailIntro: '北京著名清真寺，历史悠久。',
        detailQuote: '“清真建筑在胡同里静静生长。”',
        detailBody: [
            '建筑细节有伊斯兰风格特色。',
            '周边有清真美食聚集。',
            '请尊重宗教礼仪。'
        ]
    },
    olympic: {
        detailTitle: '奥林匹克公园',
        detailIntro: '大型体育设施集群，现代感强。',
        detailQuote: '“钢结构与广场，写下现代序章。”',
        detailBody: [
            '鸟巢与水立方是主要景观。',
            '夜景灯光效果更突出。',
            '场地开阔，适合散步。'
        ]
    },
    quanjude: {
        detailTitle: '全聚德烤鸭',
        detailIntro: '北京烤鸭代表品牌之一。',
        detailQuote: '“一卷一口，是城市味觉记忆。”',
        detailBody: [
            '传统片鸭服务是特色。',
            '高峰时段需排队。',
            '适合与朋友共享体验。'
        ]
    },
    sanlitun: {
        detailTitle: '三里屯',
        detailIntro: '潮流商业与夜生活聚集区。',
        detailQuote: '“霓虹与街头，是这里的语言。”',
        detailBody: [
            '夜晚氛围更浓厚。',
            '适合购物、餐饮与街拍。',
            '注意人流与交通秩序。'
        ]
    },
    shejitan: {
        detailTitle: '社稷坛',
        detailIntro: '明清皇家祭祀土地与谷物之所。',
        detailQuote: '“祭坛承载着国家的农业记忆。”',
        detailBody: [
            '坛面色彩分明，象征五方。',
            '空间秩序简洁而庄重。',
            '适合安静参观。'
        ]
    },
    shichahai: {
        detailTitle: '什刹海',
        detailIntro: '湖面与胡同相连的休闲水域。',
        detailQuote: '“水面一静，胡同也变得安静。”',
        detailBody: [
            '傍晚光线柔和，适合拍照。',
            '可体验摇橹船或湖畔步道。',
            '周边胡同历史氛围浓。'
        ]
    },
    tanzhe: {
        detailTitle: '潭柘寺',
        detailIntro: '古寺名胜，环境幽深。',
        detailQuote: '“一寺一松，岁月静好。”',
        detailBody: [
            '古银杏是主要看点。',
            '寺院规模大，适合慢步。',
            '注意山地行走安全。'
        ]
    },
    tiananmen: {
        detailTitle: '天安门',
        detailIntro: '城市象征性地标，空间尺度宏大。',
        detailQuote: '“广场与城楼，是时代的舞台。”',
        detailBody: [
            '视野开阔，适合广角拍摄。',
            '游客较多，注意安全与秩序。',
            '建议结合周边景点联动游览。'
        ]
    },
    tiantan: {
        detailTitle: '天坛',
        detailIntro: '皇家祭天建筑群，空间与比例严谨。',
        detailQuote: '“圆与方，是天地关系的隐喻。”',
        detailBody: [
            '祈年殿与圜丘坛是核心景点。',
            '建议观察台阶数量与建筑比例。',
            '清晨人少，体验更佳。'
        ]
    },
    wangfujing: {
        detailTitle: '王府井小吃街',
        detailIntro: '热门美食街区，选择丰富。',
        detailQuote: '“街头味道，是城市最直接的表达。”',
        detailBody: [
            '适合尝试多样小吃。',
            '人流密集，注意随身物品。',
            '夜晚更具氛围感。'
        ]
    },
    wudaoying: {
        detailTitle: '五道营胡同',
        detailIntro: '文艺小店与咖啡馆聚集的胡同。',
        detailQuote: '“慢下来，胡同就有了故事。”',
        detailBody: [
            '店铺小巧，适合慢逛。',
            '较为安静，适合拍照。',
            '建议选择下午时段。'
        ]
    },
    xiangshan: {
        detailTitle: '香山',
        detailIntro: '著名登山景点，秋色尤佳。',
        detailQuote: '“山色一层层，秋意也一层层。”',
        detailBody: [
            '秋季红叶最美，游客较多。',
            '山路较长，需准备体力。',
            '注意天气变化。'
        ]
    },
    yandaixie: {
        detailTitle: '烟袋斜街',
        detailIntro: '老北京胡同商业街，短而精致。',
        detailQuote: '“一条斜街，藏着旧时烟火。”',
        detailBody: [
            '街巷狭窄，适合步行。',
            '小店多，适合边走边看。',
            '人多时注意行走秩序。'
        ]
    },
    yiheyuan: {
        detailTitle: '颐和园',
        detailIntro: '皇家园林代表作，湖山相映。',
        detailQuote: '“长廊尽头，是一湖风景。”',
        detailBody: [
            '昆明湖与长廊是核心区域。',
            '适合长时间游览与拍照。',
            '建议规划路线避免走冤路。'
        ]
    },
    yonghegong: {
        detailTitle: '雍和宫',
        detailIntro: '藏传佛教寺院，色彩浓烈。',
        detailQuote: '“香火缭绕，屋顶映金。”',
        detailBody: [
            '游客多，保持安静与尊重。',
            '建筑细节丰富，适合观察。',
            '可搭配周边胡同游览。'
        ]
    },
    yuanmingyuan: {
        detailTitle: '圆明园',
        detailIntro: '园林遗址，残垣断壁承载历史记忆。',
        detailQuote: '“残缺也有力量。”',
        detailBody: [
            '遗址区开阔，适合慢走。',
            '建议阅读历史背景后参观。',
            '适合拍摄具有叙事感的画面。'
        ]
    },
    zhongshan: {
        detailTitle: '中山公园',
        detailIntro: '城市中心公园，环境清雅。',
        detailQuote: '“绿意在城中流动。”',
        detailBody: [
            '适合散步与休息。',
            '建筑与绿地结合紧凑。',
            '适合短暂停留。'
        ]
    }
};

/**
 * 将后端 stop 数据映射为 Map 页使用的 attraction 结构
 * @param {Object} stop - 后端返回的 stop 对象
 * @param {Number} index - 在 stops 数组中的索引（用于生成 markerId）
 * @returns {Object} Map 页使用的 attraction 对象
 */
function mapStopToMapAttraction(stop, index) {
    // 优先使用后端直接返回的 lat/lon 字段
    let latitude = stop.lat || stop.latitude;
    let longitude = stop.lon || stop.longitude;
    
    console.log(`[mapStopToMapAttraction] 处理 stop[${index}]: ${stop.name || stop.poi_id}`);
    console.log(`  - stopId (UUID): ${stop.id}, typeof: ${typeof stop.id}`);
    console.log(`  - 初始坐标: lat=${latitude}, lon=${longitude}`);
    
    // 如果后端没有返回，尝试从 poi.location 提取
    if (!latitude || !longitude) {
        console.log(`  - 坐标缺失，尝试从嵌套字段提取...`);
        if (stop.poi) {
            const loc = stop.poi.location || stop.poi.coordinates;
            if (loc) {
                if (loc.lat !== undefined && (loc.lon !== undefined || loc.lng !== undefined)) {
                    latitude = loc.lat;
                    longitude = loc.lon || loc.lng;
                    console.log(`  - 从 poi.location 提取: lat=${latitude}, lon=${longitude}`);
                } else if (loc.latitude !== undefined && loc.longitude !== undefined) {
                    latitude = loc.latitude;
                    longitude = loc.longitude;
                    console.log(`  - 从 poi.location 提取: latitude=${latitude}, longitude=${longitude}`);
                }
            }
        } else if (stop.location) {
            if (stop.location.lat !== undefined && (stop.location.lon !== undefined || stop.location.lng !== undefined)) {
                latitude = stop.location.lat;
                longitude = stop.location.lon || stop.location.lng;
                console.log(`  - 从 stop.location 提取: lat=${latitude}, lon=${longitude}`);
            } else if (stop.location.latitude !== undefined && stop.location.longitude !== undefined) {
                latitude = stop.location.latitude;
                longitude = stop.location.longitude;
                console.log(`  - 从 stop.location 提取: latitude=${latitude}, longitude=${longitude}`);
            }
        }
    }
    
    // 确保 latitude/longitude 是数字类型
    latitude = latitude ? Number(latitude) : null;
    longitude = longitude ? Number(longitude) : null;
    
    console.log(`  - 最终坐标: lat=${latitude}, lon=${longitude}`);
    
    // 验证坐标有效性
    if (latitude === null || longitude === null || isNaN(latitude) || isNaN(longitude)) {
        console.warn(`  ⚠️ 坐标无效！lat=${latitude}, lon=${longitude}`);
    }

    const mockDetail = MOCK_DETAILS[stop.poi_id] || {
        detailTitle: stop.name || '未命名景点',
        detailIntro: stop.brief || stop.category || '城市地标',
        detailHighlights: [
            '历史与当代交错',
            '空间尺度清晰',
            '适合慢步观察'
        ],
        detailQuote: '“每一次驻足，都是与城市对话。”',
        detailBody: [
            '这处景点保留了清晰的空间秩序，适合边走边观察细节变化。',
            '建议留意建筑材质与视线引导，能够更好理解场所特质。',
            '停留 15-30 分钟即可获得完整体验。'
        ]
    };

    const attraction = {
        id: stop.id,                                    // UUID 作为主键（保留兼容性）
        stopId: String(stop.id),                        // 🔥 stopId: UUID string（用于跨 Tab 聚焦匹配）
        markerId: index + 1,                            // 🔥 markerId: number（用于地图 marker.id）
        poiId: stop.poi_id || 'placeholder',           // POI ID（用于图片映射）
        name: stop.name || '未命名景点',
        latitude: latitude,
        longitude: longitude,
        desc: stop.category || stop.poi?.category || '',
        distance: stop.distance_m ? `${stop.distance_m}m` : '--',
        status: stop.status || 'UPCOMING',
        userLogs: stop.user_logs || [],
        aiSummary: stop.ai_summary || null,
        imageUrl: `/image/attractions/${stop.poi_id || 'placeholder'}.png`, // 图片路径
        ...mockDetail
    };
    
    console.log(`  ✅ 生成 attraction: stopId=${attraction.stopId}, markerId=${attraction.markerId}`);
    
    return attraction;
}

Page({
    data: {
        latitude: 39.916527,
        longitude: 116.397128,
        scale: 13,
        markers: [],
        markerIdToIndex: {}, // marker ID 到 attraction index 的映射
        polyline: [],
        userLocation: null,

        attractions: [], // 从后端 trip stops 加载，不再使用静态数据
        tripId: null,     // 当前行程 ID

        viewMode: 'mini',
        activeCardIndex: 0,
        selectedAttraction: null,
        touchStartX: 0,
        touchStartY: 0,
        cardStyles: [], // Pre-calculated card styles
        statusBarHeight: 20
    },

    // 待处理的聚焦请求（用于异步加载后聚焦）
    _pendingFocusStopId: null,

    onLoad() {
        const sysInfo = wx.getSystemInfoSync();
        this.setData({
            statusBarHeight: sysInfo.statusBarHeight
        });
        this.initAmapSDK();
        this.initUserLocation();
        
        // 尝试从 storage 获取 tripId
        const lastTripId = wx.getStorageSync('last_trip_id') || '';
        if (lastTripId) {
            this.setData({ tripId: lastTripId });
            this.fetchTrip(lastTripId);
        }
    },

    onShow() {
        console.log('[Map onShow] Map 页面显示');
        
        // 更新 tabBar 选中状态
        if (typeof this.getTabBar === 'function' && this.getTabBar()) {
            this.getTabBar().setData({
                selected: 1
            });
        }

        // 优先处理跨 Tab 聚焦指令
        this.applyPendingFocus();
        
        // 如果有待处理的聚焦请求，并且数据已加载，立即执行
        if (this._pendingFocusStopId && this.data.attractions && this.data.attractions.length > 0) {
            console.log('[onShow] 数据已加载，执行待处理的聚焦:', this._pendingFocusStopId);
            this.focusToStop(this._pendingFocusStopId);
            this._pendingFocusStopId = null;
        }
    },

    /**
     * 从后端获取行程数据
     * @param {String} tripId - 行程 ID
     */
    fetchTrip(tripId) {
        if (!tripId) {
            console.error('[fetchTrip] ❌ 缺少 tripId');
            return;
        }

        console.log('[fetchTrip] 开始获取行程数据:', tripId);

        wx.request({
            url: `${API_BASE_URL}/api/trips/${tripId}`,
            method: 'GET',
            success: (res) => {
                if (res.statusCode === 200 && res.data) {
                    console.log('[fetchTrip] ✅ 成功获取行程数据');
                    console.log('[fetchTrip] 完整响应数据:', JSON.stringify(res.data, null, 2));
                    
                    const trip = res.data;
                    
                    // 将 stops 转换为 attractions
                    const stops = trip.stops || [];
                    console.log('[fetchTrip] stops 数量:', stops.length);
                    console.log('[fetchTrip] stops 原始数据:', JSON.stringify(stops, null, 2));
                    
                    // 🔥 传递 index 参数给 mapStopToMapAttraction
                    const attractions = stops.map((stop, index) => mapStopToMapAttraction(stop, index));
                    
                    console.log('[fetchTrip] 转换后的 attractions 数量:', attractions.length);
                    console.log('[fetchTrip] attractions 数据:', JSON.stringify(attractions, null, 2));

                    this.setData({
                        attractions: attractions,
                        selectedAttraction: attractions[0] || null
                    }, () => {
                        // 数据加载完成后，重新绘制地图
                        this.applyOptimizedOrder();
                        this.updateCardStyles();
                        
                        // 如果有待处理的聚焦请求，现在执行
                        if (this._pendingFocusStopId) {
                            console.log('[fetchTrip] 数据加载完成，执行待处理的聚焦:', this._pendingFocusStopId);
                            this.focusToStop(this._pendingFocusStopId);
                            this._pendingFocusStopId = null;
                        }
                    });
                } else {
                    console.error('[fetchTrip] ❌ 获取失败:', res);
                    wx.showToast({
                        title: '加载行程失败',
                        icon: 'none'
                    });
                }
            },
            fail: (err) => {
                console.error('[fetchTrip] ❌ 网络错误:', err);
                wx.showToast({
                    title: '网络错误',
                    icon: 'none'
                });
            }
        });
    },

    /**
     * 应用跨 Tab 聚焦指令（deck 模式）
     */
    applyPendingFocus() {
        const pendingFocus = wx.getStorageSync('pending_focus');
        
        if (!pendingFocus) {
            return;
        }

        console.log('[applyPendingFocus] 🔍 检测到聚焦指令:', pendingFocus);
        console.log('[applyPendingFocus] 详细信息:', {
            tripId: pendingFocus.tripId,
            stopId: pendingFocus.stopId,
            stopIdType: typeof pendingFocus.stopId,
            action: pendingFocus.action,
            ts: pendingFocus.ts,
            age: `${Date.now() - pendingFocus.ts}ms`
        });

        // 校验时间戳，避免重复触发（超过 30 秒的忽略）
        const now = Date.now();
        if (now - pendingFocus.ts > 30000) {
            console.log('[applyPendingFocus] ⏰ 指令已过期，忽略');
            wx.removeStorageSync('pending_focus');
            return;
        }

        // 🔥 强制转换 stopId 为 string（确保匹配成功）
        const stopId = String(pendingFocus.stopId);
        console.log('[applyPendingFocus] ✅ 标准化 stopId:', stopId, 'typeof:', typeof stopId);
        
        // 清除聚焦指令（去重），但先保存 stopId
        wx.removeStorageSync('pending_focus');

        // 校验 tripId 一致
        if (pendingFocus.tripId !== this.data.tripId) {
            console.log('[applyPendingFocus] 🔄 tripId 不一致，重新加载行程');
            this.setData({ tripId: pendingFocus.tripId });
            
            // 保存待聚焦的 stopId，等数据加载完成后执行
            this._pendingFocusStopId = stopId;
            
            // 加载对应的 trip 数据
            wx.request({
                url: `${API_BASE_URL}/api/trips/${pendingFocus.tripId}`,
                method: 'GET',
                success: (res) => {
                    if (res.statusCode === 200 && res.data) {
                        const trip = res.data;
                        const stops = trip.stops || [];
                        const attractions = stops.map((stop, index) => mapStopToMapAttraction(stop, index));
                        
                        this.setData({
                            attractions: attractions,
                            selectedAttraction: attractions[0] || null
                        }, () => {
                            this.drawMarkers();
                            this.drawWalkingRoute(this.data.attractions);
                            this.updateCardStyles();
                            
                            // 数据加载完成后，执行聚焦
                            if (this._pendingFocusStopId) {
                                console.log('[applyPendingFocus] 📍 数据加载完成，执行聚焦:', this._pendingFocusStopId);
                                this.focusToStop(this._pendingFocusStopId);
                                this._pendingFocusStopId = null;
                            }
                        });
                    }
                },
                fail: (err) => {
                    console.error('[applyPendingFocus] ❌ 加载 trip 失败:', err);
                    this._pendingFocusStopId = null;
                }
            });
            return;
        }

        // tripId 一致，检查数据是否已加载
        if (!this.data.attractions || this.data.attractions.length === 0) {
            console.log('[applyPendingFocus] ⏳ 数据尚未加载，保存待聚焦请求');
            this._pendingFocusStopId = stopId;
            return;
        }

        // 数据已加载，直接聚焦
        console.log('[applyPendingFocus] 🎯 数据已加载，立即聚焦 stopId:', stopId);
        this.focusToStop(stopId);
    },

    /**
     * 聚焦到指定 stop（切换到 browse 模式、居中卡片、并缩放地图到该 POI）
     * 注意：不使用 moveToLocation，避免触发用户定位权限请求
     * @param {String} stopId - stop ID (UUID)
     */
    focusToStop(stopId) {
        const { attractions } = this.data;
        
        // 🔥 强制转换为 string，确保匹配成功
        const targetStopId = String(stopId);
        
        console.log('[focusToStop] 🎯 开始聚焦');
        console.log('[focusToStop] 目标 stopId:', targetStopId, 'typeof:', typeof targetStopId);
        console.log('[focusToStop] attractions 总数:', attractions.length);
        
        // 🔥 打印所有 attractions 的 stopId 用于对比
        console.log('[focusToStop] 所有 attractions 的 stopId:', 
            attractions.map((a, i) => `[${i}] ${a.stopId} (${a.name})`).join(', '));
        
        // 🔥 使用 String() 强制转换后匹配
        const idx = attractions.findIndex(a => String(a.stopId) === targetStopId);
        
        if (idx < 0) {
            console.error('[focusToStop] ❌ 未找到对应的 attraction!');
            console.error('[focusToStop] 查找失败详情:', {
                targetStopId: targetStopId,
                targetStopIdType: typeof targetStopId,
                availableStopIds: attractions.map(a => ({ stopId: a.stopId, type: typeof a.stopId, name: a.name }))
            });
            return;
        }

        const targetAttraction = attractions[idx];
        console.log('[focusToStop] ✅ 找到目标 attraction!');
        console.log('[focusToStop] 详情:', {
            index: idx,
            stopId: targetAttraction.stopId,
            markerId: targetAttraction.markerId,
            name: targetAttraction.name,
            latitude: targetAttraction.latitude,
            longitude: targetAttraction.longitude
        });

        // 切换到 browse 模式，并设置 activeCardIndex
        this.setData({
            viewMode: 'browse',
            activeCardIndex: idx,
            selectedAttraction: targetAttraction
        }, () => {
            console.log('[focusToStop] 📱 setData 完成: viewMode=browse, activeCardIndex=' + idx);
            
            // 更新卡片样式，让目标卡片居中
            this.updateCardStyles();
            
            // 检查目标是否有有效坐标
            if (targetAttraction.latitude && targetAttraction.longitude &&
                targetAttraction.latitude !== 0 && targetAttraction.longitude !== 0 &&
                !isNaN(targetAttraction.latitude) && !isNaN(targetAttraction.longitude)) {
                
                console.log('[focusToStop] 🗺️ 准备移动地图中心到:', {
                    lat: targetAttraction.latitude,
                    lon: targetAttraction.longitude,
                    name: targetAttraction.name,
                    scale: 16
                });
                
                // 🔥 直接设置地图中心和缩放级别，不使用 moveToLocation
                // 这样可以避免触发用户定位权限请求
                this.setData({
                    latitude: targetAttraction.latitude,
                    longitude: targetAttraction.longitude,
                    scale: 16  // 16 级可以看清楚建筑物
                }, () => {
                    console.log('[focusToStop] ✅ 地图中心已更新（不依赖用户定位权限）');
                    
                    // 🔥 兜底方案：使用 includePoints 再次确保地图聚焦
                    setTimeout(() => {
                        const mapCtx = wx.createMapContext('tripMap', this);
                        mapCtx.includePoints({
                            points: [{
                                latitude: targetAttraction.latitude,
                                longitude: targetAttraction.longitude
                            }],
                            padding: [80, 80, 80, 80],
                            success: () => {
                                console.log('[focusToStop] ✅ includePoints 聚焦成功（兜底）');
                            },
                            fail: (err) => {
                                console.warn('[focusToStop] ⚠️ includePoints 失败:', err);
                            }
                        });
                    }, 300);
                });
            } else {
                console.warn('[focusToStop] ⚠️ 目标 attraction 缺少有效坐标:', {
                    name: targetAttraction.name,
                    lat: targetAttraction.latitude,
                    lon: targetAttraction.longitude
                });
            }
            
            // 显示一个轻量提示
            wx.showToast({
                title: `已到达 ${targetAttraction.name}`,
                icon: 'success',
                duration: 2000
            });
        });
    },

    /**
     * 处理待展示的到达信息（从 Plan 页自动跳转过来）
     * @deprecated 已替换为 applyPendingFocus
     */
    handlePendingStop() {
        const pendingStop = wx.getStorageSync('pending_stop');
        
        if (!pendingStop) {
            return;
        }

        console.log('[handlePendingStop] 检测到待展示 stop:', pendingStop);

        // 检查时间戳，避免重复展示（超过 5 秒的忽略）
        const now = Date.now();
        if (now - pendingStop.ts > 5000) {
            console.log('[handlePendingStop] 信息已过期，忽略');
            wx.removeStorageSync('pending_stop');
            return;
        }

        // 清除 storage（去重）
        wx.removeStorageSync('pending_stop');

        // 显示到达弹窗
        wx.showModal({
            title: '已到达景点',
            content: `欢迎来到 ${pendingStop.name}！开始探索吧`,
            showCancel: false,
            confirmText: '开始导览',
            success: (res) => {
                if (res.confirm) {
                    // 可选：切换到详情页或特定卡片
                    // 这里简单地切换到 browse 模式
                    this.setData({
                        viewMode: 'browse'
                    });
                }
            }
        });
    },

    updateCardStyles() {
        const { activeCardIndex, attractions } = this.data;
        console.log('Updating Card Styles. Active Index:', activeCardIndex);

        const cardStyles = attractions.map((item, index) => {
            const diff = index - activeCardIndex;
            const absDiff = Math.abs(diff);
            return {
                transform: `translateX(${diff * 500}rpx) translateY(${absDiff * 40}rpx) rotate(${diff * 5}deg) scale(${1 - absDiff * 0.1})`,
                opacity: absDiff > 1 ? 0.4 : 1,
                zIndex: 100 - absDiff
            };
        });
        this.setData({ cardStyles }, () => {
            console.log('Card Styles Updated in View');
        });
    },

    initAmapSDK() {
        this.myAmapFun = new amapFile.AMapWX({ key: 'e97b34e523a66789c086668bdeab0371' });
    },

    drawMarkers() {
        const { attractions } = this.data;
        
        console.log('[drawMarkers] 🎨 开始绘制 markers');
        console.log('[drawMarkers] attractions 总数:', attractions.length);
        
        // 过滤掉无坐标的景点
        const validAttractions = attractions.filter(item => 
            item.latitude && item.longitude && 
            item.latitude !== 0 && item.longitude !== 0 &&
            !isNaN(item.latitude) && !isNaN(item.longitude)
        );
        
        console.log('[drawMarkers] 有效坐标的 attractions 数量:', validAttractions.length);
        
        if (validAttractions.length === 0) {
            console.warn('[drawMarkers] ⚠️ 没有有效坐标的景点');
            console.warn('[drawMarkers] 请检查后端返回的 stops 是否包含 lat/lon 字段');
            return;
        }
        
        // 构建 markerIdToIndex 映射
        const markerIdToIndex = {};
        
        // 🔥 生成所有 markers（使用 attraction.markerId）
        const markers = validAttractions.map((item) => {
            // 找到该 attraction 在原 attractions 数组中的索引
            const originalIndex = attractions.findIndex(a => a.stopId === item.stopId);
            
            // 🔥 使用 attraction 自带的 markerId（数字）
            const markerId = item.markerId;
            markerIdToIndex[markerId] = originalIndex;
            
            const marker = {
                id: markerId,           // 🔥 数字 ID（从 attraction.markerId）
                latitude: item.latitude,
                longitude: item.longitude,
                iconPath: '/image/marker.png',
                width: 32,
                height: 32,
                stopId: item.stopId,    // 存储 stopId 用于回查
                callout: {
                    content: item.name,
                    color: '#333',
                    fontSize: 12,
                    borderRadius: 8,
                    bgColor: '#FFF8F0',
                    padding: 8,
                    display: 'ALWAYS'
                }
            };
            
            console.log(`[drawMarkers] 生成 marker:`, {
                markerId: markerId,
                stopId: item.stopId,
                name: item.name,
                poiId: item.poiId,
                lat: marker.latitude,
                lon: marker.longitude,
                originalIndex: originalIndex
            });
            
            return marker;
        });
        
        console.log('[drawMarkers] ✅ 最终生成的 markers 数量:', markers.length);
        console.log('[drawMarkers] markerIdToIndex 映射:', JSON.stringify(markerIdToIndex, null, 2));
        
        this.setData({ markers, markerIdToIndex }, () => {
            console.log('[drawMarkers] ✅ setData 完成，已生成', markers.length, '个 markers');
            
            // 调整地图视野框住所有点
            if (markers.length > 0 || this.data.userLocation) {
                const mapCtx = wx.createMapContext('tripMap', this);
                const points = markers.map(m => ({
                    latitude: m.latitude,
                    longitude: m.longitude
                }));

                const includeUser = this.data.includeUserInViewport === true;
                if (includeUser && this.data.userLocation) {
                    points.push({
                        latitude: this.data.userLocation.latitude,
                        longitude: this.data.userLocation.longitude
                    });
                }
                
                console.log('[drawMarkers] 🗺️ 调整地图视野，包含', points.length, '个点');
                
                mapCtx.includePoints({
                    points: points,
                    padding: [60, 60, 260, 60] // 上右下左留白（底部留出卡片区域）
                });
            }
        });
    },

    drawWalkingRoute(waypoints) {
        if (!waypoints || waypoints.length < 2) return;

        const routePromises = [];
        for (let i = 0; i < waypoints.length - 1; i++) {
            const origin = `${waypoints[i].longitude},${waypoints[i].latitude}`;
            const destination = `${waypoints[i + 1].longitude},${waypoints[i + 1].latitude}`;
            routePromises.push(
                new Promise((resolve) => {
                    this.myAmapFun.getWalkingRoute({
                        origin,
                        destination,
                        success: (data) => resolve(data?.paths?.[0]?.steps || []),
                        fail: () => resolve([])
                    });
                })
            );
        }

        Promise.all(routePromises).then((allSegmentSteps) => {
            const allSteps = allSegmentSteps.flat();
            const allPoints = [];
            allSteps.forEach(step => {
                if (step.polyline) {
                    step.polyline.split(';').forEach(coord => {
                        const [lng, lat] = coord.split(',');
                        if (lng && lat) allPoints.push({ longitude: parseFloat(lng), latitude: parseFloat(lat) });
                    });
                }
            });
            if (allPoints.length > 0) {
                this.setData({
                    polyline: [{ points: allPoints, color: '#8B4513', width: 4, dottedLine: true }]
                });
            }
        });
    },

    initUserLocation() {
        checkLocationPermission().then((hasPermission) => {
            if (!hasPermission) {
                console.log('[initUserLocation] 用户未授权定位，使用景点间最短路线');
                return;
            }

            wx.getLocation({
                type: 'gcj02',
                success: (res) => {
                    const latitude = Number(res.latitude);
                    const longitude = Number(res.longitude);
                    console.log('[initUserLocation] 获取用户定位成功:', { latitude, longitude });
                    this.setData({
                        latitude,
                        longitude,
                        userLocation: { latitude, longitude },
                        includeUserInViewport: false
                    }, () => {
                        this.applyOptimizedOrder();
                    });
                },
                fail: (err) => {
                    console.warn('[initUserLocation] 获取定位失败，改用景点间最短路线:', err);
                }
            });
        });
    },

    applyOptimizedOrder() {
        if (!this.data.attractions || this.data.attractions.length === 0) {
            return;
        }
        const ordered = buildOptimizedRoute(this.data.attractions, this.data.userLocation);
        const currentStopId = this.data.selectedAttraction?.stopId;
        let activeIndex = 0;
        if (currentStopId) {
            const idx = ordered.findIndex(item => String(item.stopId) === String(currentStopId));
            if (idx >= 0) {
                activeIndex = idx;
            }
        }

        wx.setStorageSync('optimized_stop_ids', ordered.map(item => item.stopId));
        this.setData({
            attractions: ordered,
            activeCardIndex: activeIndex,
            selectedAttraction: ordered[activeIndex] || null
        }, () => {
            this.updateCardStyles();
            this.drawMarkers();
            this.drawWalkingRoute(ordered);
        });
    },

    onMarkerTap(e) {
        console.log('Marker Tapped!', e.detail);

        // 1. SET LOCK: Prevent onMapTap from executing immediately after this
        this.isMarkerTapAction = true;

        // 2. RELEASE LOCK: After a short delay (300ms), allow map taps again
        setTimeout(() => {
            this.isMarkerTapAction = false;
        }, 300);

        const markerId = e.detail.markerId;
        
        // 使用 markerIdToIndex 映射查找对应的 attraction index
        const index = this.data.markerIdToIndex[markerId];

        if (index !== undefined && index >= 0 && index < this.data.attractions.length) {
            console.log('[onMarkerTap] ✅ 找到 marker:', markerId, '-> attraction index:', index);
            this.setData({
                activeCardIndex: index,
                selectedAttraction: this.data.attractions[index],
                viewMode: 'browse' // Force card visible
            }, () => {
                this.updateCardStyles();
            });
        } else {
            console.warn('[onMarkerTap] ⚠️ 未找到 marker ID:', markerId);
        }
    },

    onMiniButtonTap() {
        console.log('Expanding from Mini Button');
        this.setData({
            viewMode: 'browse' // Switch state to show the card deck
        });
    },

    onMapTap() {
        // 1. CHECK LOCK: If we just tapped a marker, ignore this map tap
        if (this.isMarkerTapAction) {
            console.log('Map tap ignored due to marker interaction.');
            return;
        }

        // 2. Standard Logic: Click empty map space to collapse card
        if (this.data.viewMode === 'browse') {
            this.setData({ viewMode: 'mini' });
        }
    },

    onCardTap(e) {
        const index = e.currentTarget.dataset.index;
        if (index === this.data.activeCardIndex) {
            this.setData({
                selectedAttraction: this.data.attractions[index],
                viewMode: 'detail'
            });
        } else {
            this.setData({ activeCardIndex: index }, () => this.updateCardStyles());
        }
    },

    /**
     * 图片加载失败时的回退处理
     */
    onImgError(e) {
        const index = e.currentTarget.dataset.index;
        console.warn('[onImgError] 图片加载失败，index:', index);
        
        if (index !== undefined && index >= 0) {
            const attractions = this.data.attractions;
            if (attractions[index]) {
                console.log('[onImgError] 使用 placeholder 图片替换:', attractions[index].name);
                // 修改 imageKey 为 'default'，让 WXML 使用 placeholder.png
                attractions[index].imageKey = 'default';
                attractions[index].imageUrl = '/image/attractions/placeholder.png';
                this.setData({ attractions });
            }
        }
    },

    onDetailClose() {
        this.setData({ viewMode: 'browse' });
    },

    onNavigateToAttraction() {
        const attraction = this.data.selectedAttraction;
        if (attraction) {
            wx.openLocation({
                latitude: attraction.latitude,
                longitude: attraction.longitude,
                name: attraction.name,
                address: attraction.desc,
                scale: 18
            });
        }
    },

    onBackTap() {
        wx.navigateBack();
    },

    onCardTouchStart(e) {
        this.setData({
            touchStartX: e.touches[0].clientX,
            touchStartY: e.touches[0].clientY
        });
    },

    onCardTouchMove(e) { },

    onCardTouchEnd(e) {
        const deltaX = e.changedTouches[0].clientX - this.data.touchStartX;
        const deltaY = e.changedTouches[0].clientY - this.data.touchStartY;

        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
            if (deltaX > 0 && this.data.activeCardIndex > 0) {
                this.setData({ activeCardIndex: this.data.activeCardIndex - 1 }, () => this.updateCardStyles());
            } else if (deltaX < 0 && this.data.activeCardIndex < this.data.attractions.length - 1) {
                this.setData({ activeCardIndex: this.data.activeCardIndex + 1 }, () => this.updateCardStyles());
            }
        }
    }
});
