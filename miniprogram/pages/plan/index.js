const { API_BASE_URL } = require('../../utils/config.js');
const geoUtils = require('../../utils/geoUtils.js');

// GPS 围栏判定常量
const GEO_CONFIG = {
    ARRIVE_RADIUS: 100,          // 到达半径（米）
    LEAVE_RADIUS: 150,           // 离开半径（米，带滞后）
    UPDATE_INTERVAL: 5000,       // 定位更新间隔（毫秒）
    COOLDOWN_ARRIVE: 30000,      // 到达冷却时间（毫秒，避免重复触发）
    COOLDOWN_LEAVE: 30000        // 离开冷却时间（毫秒）
};

// 获取连续命中次数要求（根据测试模式动态调整）
function getHitRequired(page) {
    return page.data.testMode ? 1 : 2;
}

const ATTRACTIONS = [
    {
        id: '1',
        name: 'Hall of Supreme Harmony',
        distance: '100m',
        description: 'The largest hall within the Forbidden City.',
        history: 'Built in the 15th century, the Hall of Supreme Harmony is the heart of the Forbidden City.',
        imageUrl: 'https://picsum.photos/seed/harmony/800/1200',
        location: { lat: 39.9175, lng: 116.3972 },
        type: 'IMPERIAL HALL',
        userLogs: ['The roof beasts are fascinating.', 'Crowded but majestic.'],
        aiSummary: 'The architectural symmetry here represents supreme imperial power. You spent 45 minutes focusing on the caisson ceiling details.'
    },
    {
        id: '2',
        name: 'Palace of Heavenly Purity',
        distance: '250m',
        description: 'The primary residence of the Emperor.',
        history: 'The Palace of Heavenly Purity was the residence of emperors in the Ming and early Qing dynasties.',
        imageUrl: 'https://picsum.photos/seed/purity/800/1200',
        location: { lat: 39.9185, lng: 116.3975 },
        type: 'RESIDENCE',
        userLogs: ['Saw the "Justice & Brightness" plaque.'],
        aiSummary: 'This location marks the transition from the outer court to the inner living quarters. Your pace slowed down significantly here.'
    },
    {
        id: '3',
        name: 'Meridian Gate',
        distance: '450m',
        description: 'The grand southern entrance.',
        history: 'The Meridian Gate is the southern and main entrance to the Forbidden City.',
        imageUrl: 'https://picsum.photos/seed/meridian/800/1200',
        type: 'GATEWAY',
        location: { lat: 39.9145, lng: 116.3970 },
        userLogs: [],
        aiSummary: 'The massive U-shaped structure was designed to amplify the drum sounds during ceremonies.'
    },
    {
        id: '4',
        name: 'Gate of Divine Prowess',
        distance: '800m',
        description: 'The northern gate of the palace.',
        history: 'The Gate of Divine Prowess is the northern gate of the Forbidden City.',
        imageUrl: 'https://picsum.photos/seed/prowess/800/1200',
        type: 'EXIT GATE',
        location: { lat: 39.9220, lng: 116.3978 },
        userLogs: [],
        aiSummary: 'Exit point facing Jingshan Park.'
    }
];

const RECOMMENDED_ATTRACTIONS = [
    {
        id: '5',
        name: 'The Imperial Garden',
        distance: '600m',
        description: 'Classic Chinese garden design.',
        history: 'A retreat for the imperial family.',
        imageUrl: '',
        location: { lat: 0, lng: 0 },
        type: 'GARDEN',
        userLogs: [],
        aiSummary: 'Famous for its rockeries and ancient cypresses.'
    },
    {
        id: '6',
        name: 'Treasure Gallery',
        distance: '500m',
        description: 'Display of imperial artifacts.',
        history: 'Houses the Nine-Dragon Wall.',
        imageUrl: '',
        location: { lat: 0, lng: 0 },
        type: 'MUSEUM',
        userLogs: [],
        aiSummary: 'Contains the finest jade and gold collections.'
    }
];

/**
 * 将后端 stop 数据映射为前端 attraction 结构
 * @param {Object} stop - 后端返回的 stop 对象
 * @param {Boolean} devMode - 是否开发者模式（用于控制日志）
 * @returns {Object} 前端 attraction 对象
 */
function mapStopToAttraction(stop, devMode = false) {
    const stopId = stop.id || '';
    const poiId = stop.poi_id || '';
    const name = stop.name || 'Unknown';
    const category = stop.category || '';
    const distance_m = stop.distance_m;
    const type = category ? category.toUpperCase() : 'WAYPOINT';
    const status = stop.status || 'UPCOMING';
    
    // 🔥 提取坐标（支持多种字段结构）
    let lat = 0;
    let lon = 0;
    
    // 优先级1: 直接字段 lat/lon
    if (stop.lat != null && stop.lon != null) {
        lat = Number(stop.lat);
        lon = Number(stop.lon);
    }
    // 优先级2: 直接字段 latitude/longitude
    else if (stop.latitude != null && stop.longitude != null) {
        lat = Number(stop.latitude);
        lon = Number(stop.longitude);
    }
    // 优先级3: location 对象
    else if (stop.location) {
        if (stop.location.lat != null && stop.location.lng != null) {
            lat = Number(stop.location.lat);
            lon = Number(stop.location.lng);
        } else if (stop.location.lat != null && stop.location.lon != null) {
            lat = Number(stop.location.lat);
            lon = Number(stop.location.lon);
        } else if (stop.location.latitude != null && stop.location.longitude != null) {
            lat = Number(stop.location.latitude);
            lon = Number(stop.location.longitude);
        }
    }
    // 优先级4: coords 对象
    else if (stop.coords) {
        if (stop.coords.lat != null && stop.coords.lon != null) {
            lat = Number(stop.coords.lat);
            lon = Number(stop.coords.lon);
        }
    }
    
    // 距离格式化：大于 1000m 转换为 km
    let distance = '—';
    if (distance_m != null && distance_m > 0) {
        if (distance_m >= 1000) {
            distance = `${(distance_m / 1000).toFixed(1)} km`;
        } else {
            distance = `${distance_m} m`;
        }
    }
    
    const imageUrl = `https://picsum.photos/seed/${poiId || stopId}/800/1200`;
    
    const result = {
        id: stopId, // 使用 stop.id 作为唯一标识
        name,
        distance,
        description: '',
        history: '',
        imageUrl,
        // 🔥 统一写入多种坐标字段（确保都是 number 类型）
        lat: lat,
        lon: lon,
        latitude: lat,
        longitude: lon,
        location: { lat: lat, lng: lon },
        coords: { lat: lat, lon: lon },
        type,
        userLogs: stop.user_logs || [],
        aiSummary: stop.ai_summary || '',
        _stopId: stopId,  // ⚠️ 关键：用于调用后端接口
        _status: status,
        _seq: stop.seq || 0,
        _poiId: poiId
    };
    
    // 开发者模式下打印映射详情
    if (devMode) {
        console.log('[mapStopToAttraction] Mapping:', {
            stopId,
            poiId,
            name,
            status,
            坐标: { lat, lon },
            '_stopId (用于接口调用)': result._stopId
        });
    }
    
    return result;
}

Page({
    data: {
        visitedList: [],
        plannedList: [],
        showRecommendations: false,
        isReordering: false,
        isOptimizing: false,
        recommendations: RECOMMENDED_ATTRACTIONS,
        tripId: null,
        devMode: false, // 开发者模式开关
        headerTapCount: 0, // 用于连续点击计数
        showLocationInjector: false, // 定位注入弹窗
        testLat: '39.9175', // 测试纬度
        testLon: '116.3972', // 测试经度
        testMode: false, // 测试模式（HIT_REQUIRED=1）

        // GPS 定位相关
        currentLocation: { lat: 0, lng: 0 }, // 当前定位
        arriveStatus: 'UNKNOWN', // 到达状态：UNKNOWN / ARRIVED / NOT_ARRIVED
        leaveStatus: 'UNKNOWN',  // 离开状态：UNKNOWN / LEFT / NOT_LEFT
        continuousArriveCount: 0, // 连续到达计数
        continuousLeaveCount: 0,   // 连续离开计数
        lastArriveTime: 0,         // 上次到达时间戳
        lastLeaveTime: 0,          // 上次离开时间戳
        isMonitoring: false         // 是否正在监控定位
    },

    // ============== GPS 围栏状态 ==============
    _geoWatcherId: null,           // 定位监听器 ID
    _geoFenceState: {
        currentTarget: null,         // 当前目标 stop (含坐标)
        lastStatus: 'OUTSIDE',       // 'OUTSIDE' | 'INSIDE'
        arriveHitCount: 0,           // 进入围栏连续命中次数
        leaveHitCount: 0,            // 离开围栏连续命中次数
        lastArrive: 0,               // 上次到达时间戳（冷却控制）
        lastLeave: 0                 // 上次离开时间戳（冷却控制）
    },

    onLoad(options) {
        // 初始化开发者模式
        const devMode = wx.getStorageSync('dev_mode') || false;
        this.setData({ devMode });
        console.log('[onLoad] 开发者模式:', devMode ? '开启' : '关闭');
        
        // 兼容三种情况：
        // 1. URL 参数 tripId (navigateTo 传递)
        // 2. URL 参数 trip_id (兼容旧代码)
        // 3. 从 storage 读取 last_trip_id (switchTab 场景)
        let tripId = options.tripId || options.trip_id || '';
        
        console.log('[onLoad] options:', options);
        
        if (!tripId) {
            // 尝试从 storage 读取
            tripId = wx.getStorageSync('last_trip_id') || '';
            console.log('[onLoad] 从 storage 读取 tripId:', tripId);
        } else {
            console.log('[onLoad] 从 URL 参数读取 tripId:', tripId);
        }
        
        if (!tripId) {
            console.error('[onLoad] ❌ 无法获取 tripId（URL 参数和 storage 均为空）');
            wx.showToast({
                title: '请先创建行程',
                icon: 'none',
                duration: 2000
            });
            return;
        }
        
        // 保存到 data 并立即调用 fetchTrip
        this.setData({ tripId }, () => {
            console.log('[onLoad] ✅ tripId 已设置，开始获取行程数据');
            this.fetchTrip();
        });
    },

    /**
     * 工具函数：从参数中解析 stopId
     * 兼容两种调用方式：
     * 1. 直接传入 stopId 字符串：resolveStopId('abc-123')
     * 2. 从事件对象中提取：resolveStopId(e) -> e.currentTarget.dataset.stopId
     * 
     * @param {string|Object} arg - stopId 字符串或事件对象
     * @returns {string|null} 解析出的 stopId，失败返回 null
     */
    resolveStopId(arg) {
        // 情况1: 参数本身就是 string
        if (typeof arg === 'string') {
            console.log('[resolveStopId] ✅ 参数是 string:', arg);
            return arg;
        }
        
        // 情况2: 参数是对象（事件对象），尝试从 currentTarget.dataset 提取
        if (arg && typeof arg === 'object') {
            // 标准的 bindtap 事件对象
            if (arg.currentTarget && arg.currentTarget.dataset && arg.currentTarget.dataset.stopId) {
                const stopId = arg.currentTarget.dataset.stopId;
                console.log('[resolveStopId] ✅ 从 currentTarget.dataset 提取:', stopId);
                return String(stopId); // 确保返回 string
            }
            
            // 备用：尝试从 target.dataset
            if (arg.target && arg.target.dataset && arg.target.dataset.stopId) {
                const stopId = arg.target.dataset.stopId;
                console.log('[resolveStopId] ✅ 从 target.dataset 提取:', stopId);
                return String(stopId);
            }
        }
        
        // 无法解析
        console.warn('[resolveStopId] ⚠️ 无法解析 stopId，参数:', arg);
        console.warn('[resolveStopId] 参数类型:', typeof arg);
        if (arg && typeof arg === 'object') {
            console.warn('[resolveStopId] 参数结构:', JSON.stringify(arg, null, 2));
        }
        return null;
    },

    /**
     * 空方法，用于阻止事件冒泡
     * 用于 catchtap="noop" 的场景（如模态框内容区域，防止点击关闭）
     */
    noop() {
        // 什么都不做，仅用于阻止事件冒泡
    },

    onShow() {
        console.log('[onShow] Plan 页面显示');
        
        // 初始化开发者模式（从 storage 读取）
        const devMode = wx.getStorageSync('dev_mode') || false;
        this.setData({ devMode });
        
        // 更新 tabBar 选中状态
        if (typeof this.getTabBar === 'function' && this.getTabBar()) {
            this.getTabBar().setData({
                selected: 0
            });
        }
        
        // 🔥 处理 tripId 传递（兼容多种场景）
        const storageTripId = wx.getStorageSync('last_trip_id') || '';
        const currentTripId = this.data.tripId;
        
        console.log('[onShow] 当前 tripId:', currentTripId);
        console.log('[onShow] storage tripId:', storageTripId);
        
        // 场景1: 如果 storage 有新的 tripId，且与当前不同，更新并刷新
        if (storageTripId && storageTripId !== currentTripId) {
            console.log('[onShow] 🔄 检测到新的 tripId，更新数据');
            this.setData({ tripId: storageTripId }, () => {
                console.log('[onShow] ✅ tripId 已更新为:', storageTripId);
                this.fetchTrip().then(() => {
                    // 数据刷新后，启动 GPS 监听
                    this.startGeoWatcher();
                });
            });
        }
        // 场景2: 如果已有 tripId，刷新数据
        else if (currentTripId) {
            console.log('[onShow] ♻️  已有 tripId，刷新行程数据');
            this.fetchTrip().then(() => {
                // 数据刷新后，启动 GPS 监听
                this.startGeoWatcher();
            });
        }
        // 场景3: 如果没有 tripId，但 storage 有，读取并加载
        else if (storageTripId) {
            console.log('[onShow] 📥 从 storage 读取 tripId 并加载数据');
            this.setData({ tripId: storageTripId }, () => {
                this.fetchTrip().then(() => {
                    this.startGeoWatcher();
                });
            });
        }
        // 场景4: 完全没有 tripId
        else {
            console.log('[onShow] ⚠️  无 tripId，等待用户创建行程');
        }
    },

    onHide() {
        console.log('[onHide] Plan 页面隐藏');
        // 页面隐藏时停止定位监听（省电）
        this.stopGeoWatcher();
    },

    onUnload() {
        console.log('[onUnload] Plan 页面卸载');
        // 页面卸载时确保停止定位监听
        this.stopGeoWatcher();
    },

    /**
     * 从后端获取行程详情
     * @returns {Promise} 返回行程数据或错误
     */
    fetchTrip() {
        const tripId = this.data.tripId;
        if (!tripId) return Promise.reject('Missing tripId');

        console.log('[fetchTrip] 开始获取行程，tripId:', tripId);

        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE_URL}/api/trips/${tripId}`,
                method: 'GET',
                success: (res) => {
                    console.log('[fetchTrip] Response statusCode:', res.statusCode);
                    
                    if (res.statusCode === 200) {
                        const data = res.data || {};
                        const stops = data.stops || [];
                        
                        console.log('[fetchTrip] ✅ 获取成功，stops 数量:', stops.length);
                        if (stops.length > 0) {
                            console.log('[fetchTrip] 第一个 stop:', {
                                id: stops[0].id,
                                name: stops[0].name,
                                status: stops[0].status
                            });
                        }
                        
                        // 按 seq 升序排序
                        const sortedStops = stops.sort((a, b) => (a.seq || 0) - (b.seq || 0));
                        
                        // 显示完整行程数据（调试用）
                        console.log('[fetchTrip] 完整行程数据:', JSON.stringify(res.data, null, 2));
                        
                        // 映射为前端 attraction 结构（传入 devMode）
                        const attractions = sortedStops.map(stop =>
                            mapStopToAttraction(stop, this.data.devMode)
                        );
                        
                        const orderedAttractions = this.getOptimizedAttractions(attractions);
                        
                        // 分组：visitedList 只包含 COMPLETED，plannedList 包含其他状态
                        const visitedList = [];
                        const plannedList = [];
                        orderedAttractions.forEach((item) => {
                            if (item._status === 'COMPLETED') {
                                visitedList.push(item);
                            } else {
                                plannedList.push(item);
                            }
                        });
                        
                        this.setData({ visitedList, plannedList });
                        console.log('[fetchTrip] 数据分组完成 - Completed:', visitedList.length, ', Upcoming:', plannedList.length);
                        resolve(data);
                    } else if (res.statusCode === 404) {
                        console.error('[fetchTrip] ❌ Trip not found:', res);
                        wx.showToast({
                            title: 'Trip not found',
                            icon: 'none'
                        });
                        reject({ statusCode: 404, message: 'Trip not found', data: res.data });
                    } else if (res.statusCode >= 500) {
                        console.error('[fetchTrip] ❌ Server error:', res);
                        wx.showToast({
                            title: 'Server error',
                            icon: 'none'
                        });
                        reject({ statusCode: res.statusCode, message: 'Server error', data: res.data });
                    } else {
                        console.error('[fetchTrip] ❌ Failed:', res);
                        wx.showToast({
                            title: 'Failed to load trip',
                            icon: 'none'
                        });
                        reject({ statusCode: res.statusCode, message: 'Failed to load trip', data: res.data });
                    }
                },
                fail: (err) => {
                    console.error('[fetchTrip] ❌ Network error:', err);
                    wx.showToast({
                        title: 'Network error',
                        icon: 'none'
                    });
                    reject({ message: 'Network error', error: err });
                }
            });
        });
    },

    getPlanUserLocation() {
        const location = this.data.currentLocation;
        if (!location) {
            return null;
        }
        const lat = Number(location.lat != null ? location.lat : location.latitude);
        const lon = Number(location.lng != null ? location.lng : location.longitude);
        if (isNaN(lat) || isNaN(lon) || lat === 0 || lon === 0) {
            return null;
        }
        return { lat, lon };
    },

    getOptimizedAttractions(attractions) {
        const storedOrder = wx.getStorageSync('optimized_stop_ids');
        if (Array.isArray(storedOrder) && storedOrder.length > 0) {
            const map = new Map(
                attractions.map(item => [String(item._stopId || item.id), item])
            );
            const ordered = [];
            const usedIds = new Set();
            storedOrder.forEach((id) => {
                const key = String(id);
                const item = map.get(key);
                if (item) {
                    ordered.push(item);
                    usedIds.add(key);
                }
            });
            const remaining = attractions.filter(item => {
                const key = String(item._stopId || item.id);
                return !usedIds.has(key);
            });
            return [...ordered, ...remaining];
        }

        const userLocation = this.getPlanUserLocation();
        return geoUtils.buildOptimizedRoute(attractions, userLocation);
    },

    handleDeletePlanned(e) {
        const { id } = e.detail;
        this.setData({
            plannedList: this.data.plannedList.filter(item => item.id !== id)
        });
    },

    handleAddLog(e) {
        const { id, text } = e.detail;
        const tripId = this.data.tripId;
        
        const allItems = [...this.data.visitedList, ...this.data.plannedList];
        const item = allItems.find(a => a.id === id);
        if (!item || !item._stopId) {
            console.error('Stop not found or missing _stopId');
            return;
        }
        
        const stopId = item._stopId;
        
        wx.request({
            url: `${API_BASE_URL}/api/trips/${tripId}/stops/${stopId}/memories`,
            method: 'POST',
            data: {
                type: 'USER_NOTE',
                text: text
            },
            success: (res) => {
                if (res.statusCode === 200) {
                    wx.showToast({ title: 'Log added', icon: 'success' });
                    this.fetchTrip();
                } else {
                    console.error('Failed to add log:', res);
                    wx.showToast({ title: 'Failed to add log', icon: 'none' });
                }
            },
            fail: (err) => {
                console.error('Request failed:', err);
                wx.showToast({ title: 'Network error', icon: 'none' });
            }
        });
    },

    toggleReordering() {
        this.setData({
            isReordering: !this.data.isReordering
        });
    },

    handleAutoOptimize() {
        this.setData({ isOptimizing: true });
        wx.showToast({
            title: 'Optimizing...',
            icon: 'loading',
            duration: 1200
        });

        setTimeout(() => {
            const shuffled = [...this.data.plannedList].sort(() => Math.random() - 0.5);
            this.setData({
                plannedList: shuffled,
                isOptimizing: false
            });
        }, 1200);
    },

    moveItem(e) {
        const { index } = e.detail;
    },

    handleMoveUp(e) {
        const globalIndex = e.detail.index;
        const plannedIndex = globalIndex - this.data.visitedList.length;

        if (plannedIndex > 0) {
            const newList = [...this.data.plannedList];
            [newList[plannedIndex], newList[plannedIndex - 1]] = [newList[plannedIndex - 1], newList[plannedIndex]];
            this.setData({ plannedList: newList });
        }
    },

    handleMoveDown(e) {
        const globalIndex = e.detail.index;
        const plannedIndex = globalIndex - this.data.visitedList.length;

        if (plannedIndex < this.data.plannedList.length - 1) {
            const newList = [...this.data.plannedList];
            [newList[plannedIndex], newList[plannedIndex + 1]] = [newList[plannedIndex + 1], newList[plannedIndex]];
            this.setData({ plannedList: newList });
        }
    },

    showRecommendationsModal() {
        this.setData({ showRecommendations: true });
    },

    hideRecommendationsModal() {
        this.setData({ showRecommendations: false });
    },

    handleAddAttraction(e) {
        const item = e.currentTarget.dataset.item;
        this.setData({
            plannedList: [...this.data.plannedList, item],
            showRecommendations: false
        });
    },

    /**
     * 手动到达 stop（从 UI 按钮触发）
     * @param {Object} e - 事件对象，从 dataset 读取 stopId
     */
    arriveStop(e) {
        // 🔥 使用统一解析逻辑，兼容 stopId/camelCase
        const stopId = this.resolveStopId(e);
        
        console.log('[arriveStop] 🚀 手动到达按钮触发');
        console.log('[arriveStop] 📥 从 dataset 读取 stopId:', stopId);
        
        if (!stopId) {
            console.error('[arriveStop] ❌ 缺少 stopId');
            wx.showToast({
                title: 'stopId 缺失',
                icon: 'none',
                duration: 2000
            });
            return;
        }

        // 调用统一的到达方法
        this.arriveStopById(stopId, 'manual');
    },

    /**
     * 到达 stop 的统一方法（不依赖 event）
     * @param {string} stopId - stop ID
     * @param {string} reason - 触发原因：'manual'(手动), 'geo'(地理围栏)
     */
    arriveStopById(stopId, reason = 'manual') {
        const tripId = this.data.tripId;
        
        console.log('[arriveStopById] 🚀 开始执行 ARRIVE');
        console.log('[arriveStopById] 📥 触发原因:', reason);
        console.log('[arriveStopById] 🔍 stopId:', stopId);
        console.log('[arriveStopById] tripId:', tripId);
        
        // 验证必要参数
        if (!tripId || !stopId) {
            console.error('[arriveStopById] ❌ 缺少必要参数:', { tripId, stopId });
            wx.showToast({
                title: 'stopId 缺失',
                icon: 'none',
                duration: 2000
            });
            return;
        }

        const url = `${API_BASE_URL}/api/trips/${tripId}/stops/${stopId}/arrive`;
        console.log('[arriveStopById] 📤 请求 URL:', url);

        wx.showLoading({ title: '更新中...', mask: true });

        wx.request({
            url: url,
            method: 'POST',
            success: (res) => {
                console.log('[arriveStopById] Response statusCode:', res.statusCode);
                console.log('[arriveStopById] Response data:', res.data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log('[arriveStopById] ✅ 成功');
                    wx.showToast({ 
                        title: '已标记到达', 
                        icon: 'success',
                        duration: 1500
                    });
                    
                    // 🔥 刷新行程数据
                    this.fetchTrip();

                    // 🔥 写入 pending_focus 并跳转到 Map 页
                    setTimeout(() => {
                        const pendingFocusData = {
                            tripId: tripId,
                            stopId: String(stopId),
                            action: 'ARRIVE',
                            reason: reason,
                            ts: Date.now()
                        };
                        
                        wx.setStorageSync('pending_focus', pendingFocusData);

                        console.log('[arriveStopById] 📝 准备跳转到 Map 页');
                        console.log('[arriveStopById] pending_focus 内容:', pendingFocusData);

                        // 切换到 Map 页
                        wx.switchTab({
                            url: '/pages/map/index',
                            success: () => {
                                console.log('[arriveStopById] ✅ 已成功切换到 Map 页');
                            },
                            fail: (err) => {
                                console.error('[arriveStopById] ❌ switchTab 失败:', err);
                            }
                        });
                    }, 500);
                } else {
                    console.error('[arriveStopById] ❌ 失败:', res);
                    wx.showToast({ 
                        title: `更新失败 (${res.statusCode})`, 
                        icon: 'none',
                        duration: 2000
                    });
                }
            },
            fail: (err) => {
                console.error('[arriveStopById] ❌ 网络错误:', err);
                wx.showToast({ 
                    title: '网络错误', 
                    icon: 'none',
                    duration: 2000
                });
            },
            complete: () => {
                wx.hideLoading();
            }
        });
    },

    completeStop(arg) {
        // 🔥 使用 resolveStopId 工具函数解析 stopId（兼容两种调用方式）
        const stopId = this.resolveStopId(arg);
        const tripId = this.data.tripId;
        
        console.log('[completeStop] 🚀 开始执行 COMPLETE');
        console.log('[completeStop] 📥 输入参数类型:', typeof arg);
        console.log('[completeStop] 🔍 解析后的 stopId:', stopId);
        console.log('[completeStop] tripId:', tripId);
        
        // 验证必要参数
        if (!tripId || !stopId) {
            console.error('[completeStop] ❌ 缺少必要参数:', { tripId, stopId });
            wx.showToast({
                title: 'stopId 缺失',
                icon: 'none',
                duration: 2000
            });
            return;
        }

        const url = `${API_BASE_URL}/api/trips/${tripId}/stops/${stopId}/complete`;
        console.log('[completeStop] 📤 请求 URL:', url);

        wx.showLoading({ title: '完成中...', mask: true });

        wx.request({
            url: url,
            method: 'POST',
            success: (res) => {
                console.log('[completeStop] Response statusCode:', res.statusCode);
                console.log('[completeStop] Response data:', res.data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log('[completeStop] ✅ 成功');
                    wx.showToast({ 
                        title: '已标记完成', 
                        icon: 'success',
                        duration: 1500
                    });
                    // 刷新行程数据
                    this.fetchTrip();
                } else {
                    console.error('[completeStop] ❌ 失败:', res);
                    wx.showToast({ 
                        title: `更新失败 (${res.statusCode})`, 
                        icon: 'none',
                        duration: 2000
                    });
                }
            },
            fail: (err) => {
                console.error('[completeStop] ❌ 网络错误:', err);
                wx.showToast({ 
                    title: '网络错误', 
                    icon: 'none',
                    duration: 2000
                });
            },
            complete: () => {
                wx.hideLoading();
            }
        });
    },

    /**
     * 长按 header 切换开发者模式
     */
    handleHeaderLongPress() {
        console.log('[handleHeaderLongPress] 长按 header');
        
        wx.showActionSheet({
            itemList: [
                this.data.devMode ? '切换到用户模式' : '切换到开发者模式'
            ],
            success: (res) => {
                if (res.tapIndex === 0) {
                    this.toggleDevMode();
                }
            },
            fail: (err) => {
                console.log('[handleHeaderLongPress] ActionSheet 取消');
            }
        });
    },

    /**
     * 切换开发者模式
     */
    toggleDevMode() {
        const newDevMode = !this.data.devMode;
        
        console.log('[toggleDevMode] 切换开发者模式:', newDevMode ? '开启' : '关闭');
        
        // 保存到 storage
        wx.setStorageSync('dev_mode', newDevMode);
        
        // 更新 data
        this.setData({ devMode: newDevMode });
        
        // 显示提示
        wx.showToast({
            title: newDevMode ? '开发者模式已开启' : '用户模式已开启',
            icon: 'success',
            duration: 2000
        });
    },

    /**
     * 分享到社区（V3 - 一键分享闭环）
     * 检查已完成的 stops，如果有则跳转到 Community Tab 并自动弹窗
     */
    shareToCommunity() {
        const tripId = this.data.tripId;
        
        console.log('[shareToCommunity] 🚀 准备分享到社区');
        console.log('[shareToCommunity] tripId:', tripId);
        
        if (!tripId) {
            console.error('[shareToCommunity] ❌ tripId 缺失');
            wx.showToast({
                title: 'tripId 缺失',
                icon: 'none',
                duration: 2000
            });
            return;
        }

        // 🔥 Step 1: 筛选已完成的 stops
        const completedStops = [];
        
        // 从 visitedList 中筛选
        if (this.data.visitedList && this.data.visitedList.length > 0) {
            this.data.visitedList.forEach(stop => {
                if (stop._status === 'COMPLETED' || stop._status === 'VISITED') {
                    completedStops.push({
                        stopId: stop._stopId || stop.id,
                        poi_id: stop._poiId || '',
                        name: stop.name,
                        userLogs: stop.userLogs || [],
                        aiSummary: stop.aiSummary || ''
                    });
                }
            });
        }
        
        // 也检查 plannedList 中状态为 COMPLETED 的（如果有）
        if (this.data.plannedList && this.data.plannedList.length > 0) {
            this.data.plannedList.forEach(stop => {
                if (stop._status === 'COMPLETED') {
                    completedStops.push({
                        stopId: stop._stopId || stop.id,
                        poi_id: stop._poiId || '',
                        name: stop.name,
                        userLogs: stop.userLogs || [],
                        aiSummary: stop.aiSummary || ''
                    });
                }
            });
        }

        console.log('[shareToCommunity] 已完成的 stops:', completedStops.length, completedStops);

        // 🔥 Step 2: 检查是否有已完成的 stops
        if (completedStops.length === 0) {
            wx.showModal({
                title: '还未完成旅行',
                content: '请先完成至少一个景点的游览，才能分享到社区哦！',
                showCancel: false,
                confirmText: '知道了'
            });
            return;
        }

        // 🔥 Step 3: 组装 draft 数据
        const draft = {
            ts: Date.now(),
            tripId: tripId,
            tripContent: completedStops,
            tripLabel: `本次行程 · ${completedStops.length} 个地点`
        };

        console.log('[shareToCommunity] 准备发布的 draft:', draft);

        // 🔥 Step 4: 存储到 storage
        try {
            wx.setStorageSync('pending_post_draft', draft);
            console.log('[shareToCommunity] ✅ draft 已存储到 storage');
        } catch (err) {
            console.error('[shareToCommunity] ❌ 存储 draft 失败:', err);
            wx.showToast({
                title: '存储失败，请重试',
                icon: 'none',
                duration: 2000
            });
            return;
        }

        // 🔥 Step 5: 跳转到 Community Tab
        wx.switchTab({
            url: '/pages/community/index',
            success: () => {
                console.log('[shareToCommunity] ✅ 成功跳转到 Community 页面');
            },
            fail: (err) => {
                console.error('[shareToCommunity] ❌ 跳转失败:', err);
                wx.showToast({
                    title: '跳转失败，请重试',
                    icon: 'none',
                    duration: 2000
                });
            }
        });
    },

    /**
     * 根据 stopId 查找 stop 对象
     * @param {String} stopId - stop ID
     * @returns {Object|null} - stop 对象或 null
     */
    findStopById(stopId) {
        const allStops = [...this.data.visitedList, ...this.data.plannedList];
        return allStops.find(stop => stop._stopId === stopId) || null;
    },

    // ============== 开发者模式功能 ==============

    /**
     * 切换测试模式（HIT_REQUIRED=1）
     */
    toggleTestMode() {
        const newTestMode = !this.data.testMode;
        this.setData({ testMode: newTestMode });
        
        wx.showToast({
            title: newTestMode ? '测试模式开启（命中=1）' : '测试模式关闭（命中=2）',
            icon: 'none',
            duration: 2000
        });
        
        console.log('[toggleTestMode] 测试模式:', newTestMode ? '开启' : '关闭');
    },

    /**
     * 显示定位注入弹窗
     */
    showLocationInjector() {
        // 预填充当前目标的坐标（如果有）
        const target = this._geoFenceState.currentTarget;
        if (target && target.coords) {
            this.setData({
                testLat: target.coords.lat.toString(),
                testLon: target.coords.lon.toString(),
                showLocationInjector: true
            });
        } else {
            this.setData({ showLocationInjector: true });
        }
    },

    /**
     * 隐藏定位注入弹窗
     */
    hideLocationInjector() {
        this.setData({ showLocationInjector: false });
    },

    /**
     * 更新测试纬度
     */
    onTestLatInput(e) {
        this.setData({ testLat: e.detail.value });
    },

    /**
     * 更新测试经度
     */
    onTestLonInput(e) {
        this.setData({ testLon: e.detail.value });
    },

    /**
     * 执行定位注入
     */
    injectLocation() {
        const lat = parseFloat(this.data.testLat);
        const lon = parseFloat(this.data.testLon);

        if (isNaN(lat) || isNaN(lon)) {
            wx.showToast({
                title: '坐标格式错误',
                icon: 'none'
            });
            return;
        }

        console.log('[injectLocation] 注入坐标:', { lat, lon });

        // 🔥 使用统一的 geo-fence 目标初始化逻辑（策略：最近未完成的 stop）
        const initResult = this.initGeoFenceTarget("NEAREST_TO_INJECTED", lat, lon);
        if (!initResult) {
            console.warn('[injectLocation] ⚠️ 无法初始化 geo-fence 目标，无法处理注入定位');
            wx.showToast({
                title: '没有可用的目标站点',
                icon: 'none'
            });
            return;
        }

        console.log('[injectLocation] ✅ Geo-fence 目标已初始化，准备处理位置更新');

        // 调用位置更新处理函数
        this.handleLocationUpdate({
            latitude: lat,
            longitude: lon
        });

        // 关闭弹窗
        this.hideLocationInjector();

        wx.showToast({
            title: '已注入定位',
            icon: 'success',
            duration: 1500
        });
    },

    // ============== GPS 围栏监听逻辑 ==============

    /**
     * 初始化地理围栏目标
     * @param {string} strategy - 选择策略："FIRST_UNFINISHED" 或 "NEAREST_TO_INJECTED"
     * @param {number} injectedLat - 注入的纬度（仅 NEAREST_TO_INJECTED 策略使用）
     * @param {number} injectedLon - 注入的经度（仅 NEAREST_TO_INJECTED 策略使用）
     * @returns {Object|null} 目标 stop 或 null
     */
    initGeoFenceTarget(strategy = "FIRST_UNFINISHED", injectedLat = null, injectedLon = null) {
        console.log('[initGeoFenceTarget] 🎯 开始初始化围栏目标');
        console.log('[initGeoFenceTarget] 策略:', strategy);
        
        // 1. 合并所有 stops
        const allStops = [...this.data.visitedList, ...this.data.plannedList];
        console.log('[initGeoFenceTarget] 总 stops 数量:', allStops.length);
        console.log('[initGeoFenceTarget] visitedList:', this.data.visitedList.length);
        console.log('[initGeoFenceTarget] plannedList:', this.data.plannedList.length);
        
        if (allStops.length === 0) {
            console.warn('[initGeoFenceTarget] ⚠️ allStops 为空，无法初始化目标');
            return null;
        }

        // 2. 根据策略选择目标 stop
        let targetStop = null;
        
        if (strategy === "FIRST_UNFINISHED") {
            console.log('[initGeoFenceTarget] 使用策略: FIRST_UNFINISHED');
            targetStop = geoUtils.getCurrentTargetStop(allStops);
        } 
        else if (strategy === "NEAREST_TO_INJECTED") {
            console.log('[initGeoFenceTarget] 使用策略: NEAREST_TO_INJECTED');
            console.log('[initGeoFenceTarget] 参考坐标:', { lat: injectedLat, lon: injectedLon });
            
            if (injectedLat != null && injectedLon != null) {
                targetStop = geoUtils.getNearestTargetStop(allStops, injectedLat, injectedLon);
            } else {
                console.warn('[initGeoFenceTarget] ⚠️ NEAREST_TO_INJECTED 策略需要提供坐标，回退到 FIRST_UNFINISHED');
                targetStop = geoUtils.getCurrentTargetStop(allStops);
            }
        }
        else {
            console.error('[initGeoFenceTarget] ❌ 未知策略:', strategy);
            return null;
        }

        if (!targetStop) {
            console.warn('[initGeoFenceTarget] ⚠️ 未找到目标 stop');
            console.warn('[initGeoFenceTarget] allStops 详情:', allStops.map(s => ({
                name: s.name,
                stopId: s._stopId || s.id,
                status: s.status || s._status
            })));
            return null;
        }

        // 3. 提取坐标（支持 lat/lon 和 latitude/longitude）
        const coords = geoUtils.extractStopCoordinates(targetStop);
        if (!coords) {
            console.warn('[initGeoFenceTarget] ⚠️ 目标 stop 无有效坐标:', {
                name: targetStop.name,
                stopId: targetStop._stopId || targetStop.id,
                rawStop: targetStop
            });
            return null;
        }

        console.log('[initGeoFenceTarget] ✅ 成功找到目标 stop:', {
            name: targetStop.name,
            stopId: targetStop._stopId || targetStop.id,
            status: targetStop._status || targetStop.status,
            coords: coords
        });

        // 4. 初始化 _geoFenceState
        this._geoFenceState = {
            currentTarget: { ...targetStop, coords },
            lastStatus: 'OUTSIDE',
            arriveHitCount: 0,
            leaveHitCount: 0,
            lastArrive: 0,
            lastLeave: 0
        };

        console.log('[initGeoFenceTarget] 🎉 围栏状态已初始化:', {
            target名称: this._geoFenceState.currentTarget.name,
            target_stopId: this._geoFenceState.currentTarget._stopId,
            target坐标: this._geoFenceState.currentTarget.coords,
            初始状态: this._geoFenceState.lastStatus
        });

        return targetStop;
    },

    /**
     * 启动 GPS 定位监听
     */
    async startGeoWatcher() {
        // 如果已启动，跳过
        if (this._geoWatcherId !== null) {
            console.log('[startGeoWatcher] 监听已启动，跳过');
            return;
        }

        console.log('[startGeoWatcher] 开始启动 GPS 监听');

        // 检查并请求定位权限
        const hasPermission = await geoUtils.checkLocationPermission();
        if (!hasPermission) {
            const granted = await geoUtils.requestLocationPermission();
            if (!granted) {
                console.warn('[startGeoWatcher] 用户拒绝定位权限，无法启动监听');
                return;
            }
        }

        // 🔥 使用统一的 geo-fence 目标初始化逻辑（策略：第一个未完成的 stop）
        const initResult = this.initGeoFenceTarget("FIRST_UNFINISHED");
        if (!initResult) {
            console.log('[startGeoWatcher] 无法初始化 geo-fence 目标，跳过监听');
            return;
        }

        // 🔥 确认目标和坐标已正确初始化
        console.log('[startGeoWatcher] ✅ Geo-fence 目标已初始化:', {
            targetName: this._geoFenceState.currentTarget.name,
            targetStopId: this._geoFenceState.currentTarget._stopId,
            coords: this._geoFenceState.currentTarget.coords,
            '坐标是否为null': this._geoFenceState.currentTarget.coords === null
        });

        // 启动定位监听
        this._geoWatcherId = wx.startLocationUpdate({
            success: () => {
                console.log('[startGeoWatcher] ✅ 定位监听启动成功');
                
                // 监听位置变化
                wx.onLocationChange((location) => {
                    this.handleLocationUpdate(location);
                });
            },
            fail: (err) => {
                console.error('[startGeoWatcher] ❌ 启动失败:', err);
                this._geoWatcherId = null;
            }
        });
    },

    /**
     * 停止 GPS 定位监听
     */
    stopGeoWatcher() {
        if (this._geoWatcherId === null) {
            return;
        }

        console.log('[stopGeoWatcher] 停止 GPS 监听');

        wx.stopLocationUpdate();
        wx.offLocationChange(); // 移除位置变化监听
        this._geoWatcherId = null;

        // 重置围栏状态
        this._geoFenceState = {
            currentTarget: null,
            lastStatus: 'OUTSIDE',
            arriveHitCount: 0,
            leaveHitCount: 0,
            lastArrive: 0,
            lastLeave: 0
        };
    },

    /**
     * 处理位置更新（围栏判定 + 状态机）
     * @param {Object} location - 位置对象 { latitude, longitude, ... } 或 { lat, lon, ... }
     */
    handleLocationUpdate(location) {
        const state = this._geoFenceState;
        const target = state.currentTarget;

        // 🔥 如果没有目标 stop，尝试初始化 geo-fence 目标
        if (!target || !target.coords) {
            console.warn('[handleLocationUpdate] ⚠️ 没有目标 stop，尝试初始化 geo-fence 目标');
            
            const initResult = this.initGeoFenceTarget("FIRST_UNFINISHED");
            if (!initResult) {
                const allStops = [...this.data.visitedList, ...this.data.plannedList];
                console.error('[handleLocationUpdate] ❌ 无法初始化 geo-fence 目标，跳过处理', {
                    allStopsCount: allStops.length,
                    visitedCount: this.data.visitedList.length,
                    plannedCount: this.data.plannedList.length
                });
                return;
            }
            
            console.log('[handleLocationUpdate] ✅ Geo-fence 目标已初始化，继续处理位置更新');
            // 重新获取状态和目标
            const newTarget = this._geoFenceState.currentTarget;
            if (!newTarget || !newTarget.coords) {
                console.error('[handleLocationUpdate] ❌ 初始化后仍无有效目标，跳过处理');
                return;
            }
        }

        // 重新获取最新的 state 和 target（可能已经更新）
        const currentState = this._geoFenceState;
        const currentTarget = currentState.currentTarget;

        // 🔥 兼容多种坐标字段命名（latitude/longitude 或 lat/lon）
        const userLat = Number(location.latitude || location.lat);
        const userLon = Number(location.longitude || location.lon);
        if (!isNaN(userLat) && !isNaN(userLon)) {
            this.setData({
                currentLocation: { lat: userLat, lng: userLon }
            });
        }
        const targetLat = Number(currentTarget.coords.lat || currentTarget.coords.latitude);
        const targetLon = Number(currentTarget.coords.lon || currentTarget.coords.longitude);

        // 验证坐标有效性
        if (isNaN(userLat) || isNaN(userLon) || isNaN(targetLat) || isNaN(targetLon)) {
            console.error('[handleLocationUpdate] ❌ 坐标无效:', {
                userLat, userLon, targetLat, targetLon,
                location: location,
                targetCoords: currentTarget.coords
            });
            return;
        }

        // 计算距离
        const distance = geoUtils.haversineDistance(userLat, userLon, targetLat, targetLon);
        
        // 🔥 判断是否在围栏内
        const inside = distance <= GEO_CONFIG.ARRIVE_RADIUS;
        
        // 🔥 动态获取命中次数要求
        const hitsRequired = this.data.devMode ? 1 : 3;

        // 🔥 增强日志：打印距离、围栏状态、命中计数
        console.log('[handleLocationUpdate] 📍 位置更新:', {
            用户位置: { lat: userLat, lon: userLon },
            目标名称: currentTarget.name,
            目标stopId: currentTarget._stopId || currentTarget.stopId,
            目标状态: currentTarget._status,
            目标坐标: { lat: targetLat, lon: targetLon },
            距离: `${distance.toFixed(1)}m`,
            inside: inside,
            围栏半径: `${GEO_CONFIG.ARRIVE_RADIUS}m`,
            当前状态: currentState.lastStatus,
            arriveHitCount: currentState.arriveHitCount,
            hitsRequired: hitsRequired,
            devMode: this.data.devMode
        });

        const now = Date.now();

        // ===== 判定逻辑：进入围栏 =====
        if (inside) {
            currentState.arriveHitCount++;
            currentState.leaveHitCount = 0; // 重置离开计数

            console.log(`[handleLocationUpdate] 🟢 进入围栏 (${currentState.arriveHitCount}/${hitsRequired}) ${this.data.devMode ? '[开发模式]' : ''}`);

            // 🔥 lastStatus=OUTSIDE 且 inside 且 hitCount>=hitsRequired => 触发到达
            if (
                currentState.lastStatus === 'OUTSIDE' &&
                currentState.arriveHitCount >= hitsRequired &&
                (now - currentState.lastArrive) > GEO_CONFIG.COOLDOWN_ARRIVE
            ) {
                console.log('[handleLocationUpdate] ✅ 触发自动到达');
                
                // 🔥 确保 stopId 字段统一（兼容 _stopId 或 stopId）
                const currentTargetStopId = String(currentTarget._stopId || currentTarget.stopId || currentTarget.id || '');
                if (!currentTargetStopId) {
                    console.error('[handleLocationUpdate] ❌ 无法获取 stopId:', currentTarget);
                    return;
                }
                
                console.log('[handleLocationUpdate] 🔍 准备调用 arriveStopById，stopId:', currentTargetStopId);
                
                // 🔥 调用统一的到达方法
                this.arriveStopById(currentTargetStopId, 'geo');
                
                // 🔥 更新围栏状态
                currentState.lastStatus = 'INSIDE';
                currentState.lastArrive = now;
                currentState.arriveHitCount = 0;
            }
        }
        // ===== 判定逻辑：离开围栏 =====
        else if (distance > GEO_CONFIG.LEAVE_RADIUS) {
            currentState.leaveHitCount++;
            currentState.arriveHitCount = 0; // 重置到达计数

            console.log(`[handleLocationUpdate] 🔴 离开围栏 (${currentState.leaveHitCount}/${hitsRequired}) ${this.data.devMode ? '[开发模式]' : ''}`);

            // 连续命中 + 状态为 INSIDE + 冷却结束 => 触发离开
            if (
                currentState.leaveHitCount >= hitsRequired &&
                currentState.lastStatus === 'INSIDE' &&
                (now - currentState.lastLeave) > GEO_CONFIG.COOLDOWN_LEAVE
            ) {
                console.log('[handleLocationUpdate] ✅ 触发自动离开');
                
                // 🔥 确保 stopId 字段统一（兼容 _stopId 或 stopId）
                const currentTargetStopId = String(currentTarget._stopId || currentTarget.stopId || currentTarget.id || '');
                if (!currentTargetStopId) {
                    console.error('[handleLocationUpdate] ❌ 无法获取 stopId:', currentTarget);
                    return;
                }
                
                console.log('[handleLocationUpdate] 🔍 准备调用 autoCompleteStop，stopId:', currentTargetStopId);
                
                this.autoCompleteStop({ ...currentTarget, _stopId: currentTargetStopId });
                currentState.lastStatus = 'OUTSIDE';
                currentState.lastLeave = now;
                currentState.leaveHitCount = 0;
            }
        }
        // ===== 滞后区间：保持当前状态，重置计数 =====
        else {
            currentState.arriveHitCount = 0;
            currentState.leaveHitCount = 0;
        }
    },

    /**
     * 自动到达 stop（调用后端 arrive 接口）
     * @param {Object} stop - 目标 stop（必须包含 _stopId）
     */
    autoArriveStop(stop) {
        const tripId = this.data.tripId;
        // 🔥 确保 stopId 是 string 类型
        const stopId = String(stop._stopId || stop.id || '');

        console.log('[autoArriveStop] 🚀 开始自动到达');
        console.log('[autoArriveStop] 🔍 stop 详情:', {
            name: stop.name,
            _stopId: stop._stopId,
            id: stop.id,
            解析后stopId: stopId,
            stopId类型: typeof stopId
        });

        if (!tripId || !stopId) {
            console.error('[autoArriveStop] ❌ 缺少必要参数:', {
                tripId: tripId,
                stopId: stopId,
                stop: stop
            });
            return;
        }

        console.log('[autoArriveStop] 自动标记到达:', stop.name);
        
        const url = `${API_BASE_URL}/api/trips/${tripId}/stops/${stopId}/arrive`;
        console.log('[autoArriveStop] 📤 请求 URL:', url);

        wx.request({
            url: url,
            method: 'POST',
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log('[autoArriveStop] ✅ 成功');
                    
                    // 刷新行程数据
                    this.fetchTrip();

                    // 显示到达提示
                    wx.showToast({
                        title: `已到达 ${stop.name}`,
                        icon: 'success',
                        duration: 2000
                    });

                    // 延迟 500ms 后自动切换到 Map 页（Tab2）
                    setTimeout(() => {
                        // 保存跨 Tab 聚焦指令
                        wx.setStorageSync('pending_focus', {
                            tripId: tripId,
                            stopId: stopId,
                            action: 'ARRIVE',
                            ts: Date.now()
                        });

                        // 切换到 Map 页
                        wx.switchTab({
                            url: '/pages/map/index',
                            success: () => {
                                console.log('[autoArriveStop] ✅ 已切换到 Map 页');
                            },
                            fail: (err) => {
                                console.error('[autoArriveStop] ❌ switchTab 失败:', err);
                            }
                        });
                    }, 500);
                } else {
                    console.error('[autoArriveStop] ❌ 失败:', res);
                }
            },
            fail: (err) => {
                console.error('[autoArriveStop] ❌ 网络错误:', err);
            }
        });
    },

    /**
     * 自动完成 stop（调用后端 complete 接口）
     * @param {Object} stop - 目标 stop（必须包含 _stopId）
     */
    autoCompleteStop(stop) {
        const tripId = this.data.tripId;
        // 🔥 确保 stopId 是 string 类型
        const stopId = String(stop._stopId || stop.id || '');

        console.log('[autoCompleteStop] 🚀 开始自动完成');
        console.log('[autoCompleteStop] 🔍 stop 详情:', {
            name: stop.name,
            _stopId: stop._stopId,
            id: stop.id,
            解析后stopId: stopId,
            stopId类型: typeof stopId
        });

        if (!tripId || !stopId) {
            console.error('[autoCompleteStop] ❌ 缺少必要参数:', {
                tripId: tripId,
                stopId: stopId,
                stop: stop
            });
            return;
        }

        console.log('[autoCompleteStop] 自动标记完成:', stop.name);
        
        const url = `${API_BASE_URL}/api/trips/${tripId}/stops/${stopId}/complete`;
        console.log('[autoCompleteStop] 📤 请求 URL:', url);

        wx.request({
            url: url,
            method: 'POST',
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log('[autoCompleteStop] ✅ 成功');
                    
                    // 刷新行程数据
                    this.fetchTrip().then(() => {
                        // 数据刷新后，重新启动监听（下一个目标）
                        this.stopGeoWatcher();
                        this.startGeoWatcher();
                    });

                    // 显示完成提示
                    wx.showToast({
                        title: `已离开 ${stop.name}`,
                        icon: 'success',
                        duration: 2000
                    });
                } else {
                    console.error('[autoCompleteStop] ❌ 失败:', res);
                }
            },
            fail: (err) => {
                console.error('[autoCompleteStop] ❌ 网络错误:', err);
            }
        });
    }
})
