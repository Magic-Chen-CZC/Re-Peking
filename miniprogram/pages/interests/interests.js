Page({
    data: {
        // Categories
        categories: [
            { id: 'scenic', name: '京城名胜' },
            { id: 'culture', name: '京华墨韵' },
            { id: 'temple', name: '京祀胜迹' },
            { id: 'sacred', name: '和合圣境' },
            { id: 'food', name: '燕飨百味' },
            { id: 'festival', name: '岁时庙会' }
        ],
        activeCategory: 0,

        // All attractions data (organized by category) - simplified without images
        allAttractions: {
            scenic: [
                { id: 'gugong', name: '故宫' },
                { id: 'tiantan', name: '天坛' },
                { id: 'tiananmen', name: '天安门' },
                { id: 'yiheyuan', name: '颐和园' },
                { id: 'changcheng', name: '长城' },
                { id: 'yuanmingyuan', name: '圆明园' },
                { id: 'ditan', name: '地坛' },
                { id: 'zhongshan', name: '中山公园' },
                { id: 'shejitan', name: '社稷坛' }
            ],
            culture: [
                { id: 'guozijian', name: '国子监' },
                { id: 'kongmiao', name: '孔庙' },
                { id: 'liulichang', name: '琉璃厂' },
                { id: 'nanluogu', name: '南锣鼓巷' },
                { id: 'shichahai', name: '什刹海' },
                { id: 'houhai', name: '后海' },
                { id: 'yandaixie', name: '烟袋斜街' }
            ],
            temple: [
                { id: 'lama', name: '雍和宫' },
                { id: 'biyun', name: '碧云寺' },
                { id: 'tanzhe', name: '潭柘寺' },
                { id: 'fayuan', name: '法源寺' },
                { id: 'jietai', name: '戒台寺' }
            ],
            sacred: [
                { id: 'baiyun', name: '白云观' },
                { id: 'dongyue', name: '东岳庙' },
                { id: 'niujie', name: '牛街礼拜寺' },
                { id: 'guangji', name: '广济寺' }
            ],
            food: [
                { id: 'quanjude', name: '全聚德烤鸭' },
                { id: 'donglaishun', name: '东来顺涮肉' },
                { id: 'huguo', name: '护国寺小吃' },
                { id: 'gui', name: '簋街美食' },
                { id: 'wangfujing', name: '王府井小吃街' },
                { id: 'luzhu', name: '卤煮火烧' }
            ],
            festival: [
                { id: 'ditan_mh', name: '地坛庙会' },
                { id: 'longtan', name: '龙潭庙会' },
                { id: 'changdian', name: '厂甸庙会' },
                { id: 'baiyun_mh', name: '白云观庙会' }
            ]
        },

        currentAttractions: [],
        selectedTags: [],
        dockExpanded: false,
        maxSelection: 6,

        // Fixed Routes
        fixedRoutes: [
            { id: 'zhongzhou', name: '中轴线一日游', desc: '故宫-天安门-景山-鼓楼', poiIds: ['gugong', 'tiananmen', 'zhongshan'] },
            { id: 'hutong', name: '胡同深度游', desc: '南锣鼓巷-什刹海-烟袋斜街', poiIds: ['nanluogu', 'shichahai', 'yandaixie'] },
            { id: 'royal', name: '皇家园林游', desc: '颐和园-圆明园-香山', poiIds: ['yiheyuan', 'yuanmingyuan'] },
            { id: 'temple', name: '古刹祈福游', desc: '雍和宫-潭柘寺-戒台寺', poiIds: ['lama', 'tanzhe', 'jietai'] },
            { id: 'culture', name: '文化探索游', desc: '国子监-孔庙-琉璃厂', poiIds: ['guozijian', 'kongmiao', 'liulichang'] },
            { id: 'food', name: '美食寻味游', desc: '簋街-护国寺-王府井', poiIds: ['gui', 'huguo', 'wangfujing'] }
        ],
        selectedRouteId: null,
        selectedRouteName: '',

        // Dialogs
        showRouteDialog: false,
        showTextModal: false,

        // Text Input
        userTextInput: ''
    },

    onLoad() {
        // Initialize with first category
        this.switchCategory(0);

        this.attractionMap = this.buildAttractionMap();
        this.setData({
            selectedTags: [],
            userTextInput: '',
            selectedRouteId: null,
            selectedRouteName: ''
        });

        this.updateCurrentAttractions();
        this.syncDockState();
    },

    // Switch category
    onCategoryTap(e) {
        const index = e.currentTarget.dataset.index;
        this.switchCategory(index);
    },

    switchCategory(index) {
        const categoryId = this.data.categories[index].id;
        const attractions = this.data.allAttractions[categoryId] || [];

        // Mark selected items
        const markedAttractions = attractions.map(item => ({
            ...item,
            selected: this.data.selectedTags.some(tag => tag.id === item.id)
        }));

        this.setData({
            activeCategory: index,
            currentAttractions: markedAttractions
        });
    },

    // Tag selection
    onTagTap(e) {
        const { id, name } = e.currentTarget.dataset;

        let selectedTags = [...this.data.selectedTags];
        const existingIndex = selectedTags.findIndex(tag => tag.id === id);

        if (existingIndex > -1) {
            // Remove if already selected
            selectedTags.splice(existingIndex, 1);
        } else {
            if (selectedTags.length >= this.data.maxSelection) {
                wx.showToast({
                    title: '最多选择6个',
                    icon: 'none'
                });
                return;
            }
            // Add to selection
            selectedTags.push({ id, name });
        }

        this.setData({ selectedTags });
        this.updateCurrentAttractions();
        this.syncDockState();
    },

    onRemoveTag(e) {
        const { id } = e.currentTarget.dataset;
        const selectedTags = this.data.selectedTags.filter(tag => tag.id !== id);
        this.setData({ selectedTags });
        this.updateCurrentAttractions();
        this.syncDockState();
    },

    onRemoveRoute() {
        this.setData({
            selectedRouteId: null,
            selectedRouteName: ''
        });
        this.syncDockState();
    },

    updateCurrentAttractions() {
        const currentAttractions = this.data.currentAttractions.map(item => ({
            ...item,
            selected: this.data.selectedTags.some(tag => tag.id === item.id)
        }));
        this.setData({ currentAttractions });
    },

    // Route selection dialog
    onRouteSelectTap() {
        this.setData({ showRouteDialog: true });
    },

    onRouteDialogClose() {
        this.setData({ showRouteDialog: false });
    },

    onRouteItemTap(e) {
        const { id, name } = e.currentTarget.dataset;
        const route = this.data.fixedRoutes.find(item => item.id === id);
        const routePoiIds = route && route.poiIds ? route.poiIds : [];
        const attractionMap = this.attractionMap || this.buildAttractionMap();
        const nextSelected = [];
        const existingIds = new Set();
        let addedCount = 0;

        for (const poiId of routePoiIds) {
            if (nextSelected.length >= this.data.maxSelection) {
                break;
            }
            if (!existingIds.has(poiId) && attractionMap[poiId]) {
                nextSelected.push({ id: poiId, name: attractionMap[poiId] });
                existingIds.add(poiId);
                addedCount += 1;
            }
        }

        this.setData({
            selectedRouteId: id,
            selectedRouteName: name,
            showRouteDialog: false,
            selectedTags: nextSelected
        });
        this.updateCurrentAttractions();
        this.syncDockState();

        if (routePoiIds.length > 0 && addedCount < routePoiIds.length) {
            wx.showToast({
                title: '已填充至上限',
                icon: 'none'
            });
        }
    },

    // Refresh attractions (shuffle)
    onRefresh() {
        const currentAttractions = [...this.data.currentAttractions];
        // Simple shuffle
        for (let i = currentAttractions.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [currentAttractions[i], currentAttractions[j]] = [currentAttractions[j], currentAttractions[i]];
        }
        this.setData({ currentAttractions });
    },

    // Text input modal
    onTextLinkTap() {
        this.setData({ showTextModal: true });
    },

    onTextInput(e) {
        this.setData({ userTextInput: e.detail.value });
    },

    onModalClose() {
        this.setData({ showTextModal: false });
    },

    onModalConfirm() {
        this.setData({ showTextModal: false });
        if (this.data.userTextInput) {
            wx.showToast({
                title: '已保存您的想法',
                icon: 'success'
            });
        }
    },

    toggleDock() {
        const hasSelection = this.data.selectedTags.length > 0 || this.data.selectedRouteId;
        if (!hasSelection) {
            return;
        }
        this.setData({ dockExpanded: !this.data.dockExpanded });
    },

    clearSelection() {
        this.setData({
            selectedTags: [],
            selectedRouteId: null,
            selectedRouteName: '',
            dockExpanded: false
        });
        this.updateCurrentAttractions();
    },

    syncDockState() {
        const hasSelection = this.data.selectedTags.length > 0 || this.data.selectedRouteId;
        if (!hasSelection && this.data.dockExpanded) {
            this.setData({ dockExpanded: false });
        }
    },

    buildAttractionMap() {
        const map = {};
        const categories = this.data.allAttractions || {};
        Object.keys(categories).forEach((key) => {
            (categories[key] || []).forEach((item) => {
                map[item.id] = item.name;
            });
        });
        return map;
    },

    // Next step - 直接生成行程（移除 setup 页面）
    async onNextStep() {
        const { API_BASE_URL } = require('../../utils/config.js');
        
        // Validate
        if (this.data.selectedTags.length === 0 && !this.data.selectedRouteId && !this.data.userTextInput) {
            wx.showToast({
                title: '请至少选择一项',
                icon: 'none'
            });
            return;
        }

        // 确定模式和参数
        let mode = '';
        let planRequest = {
            time_budget: 'half_day',  // 默认半天
            transportation: 'walking',  // 默认步行
            pace_preference: 'medium',  // 默认中速
            mbti: wx.getStorageSync('user_mbti') || null
        };

        if (this.data.selectedTags.length > 0) {
            // 模式1: PICK_POIS - 用户手选景点
            mode = 'PICK_POIS';
            planRequest.mode = mode;
            planRequest.selected_poi_ids = this.data.selectedTags.map(t => t.id);
            planRequest.keep_order = false;  // 允许优化顺序
            planRequest.allow_auto_fill = false;  // 不自动补充
        } else if (this.data.selectedRouteId) {
            // 模式2: PRESET_ROUTE - 预设路线
            mode = 'PRESET_ROUTE';
            planRequest.mode = mode;
            planRequest.preset_route_id = this.data.selectedRouteId;
        } else if (this.data.userTextInput) {
            // 模式3: FREE_TEXT - 自然语言输入
            mode = 'FREE_TEXT';
            planRequest.mode = mode;
            planRequest.user_text_input = this.data.userTextInput;
        }

        console.log('[onNextStep] ========== 开始生成行程 ==========');
        console.log('[onNextStep] Mode:', mode);
        console.log('[onNextStep] Plan request:', JSON.stringify(planRequest, null, 2));

        wx.showLoading({
            title: '生成中...',
            mask: true
        });

        try {
            // 1. 调用 /api/plan/v2 生成路线规划
            const planData = await this.generatePlanV2(planRequest);
            console.log('[onNextStep] Plan response:', JSON.stringify(planData, null, 2));

            // 2. 验证 plan
            const plan = planData.plan;
            if (!plan || !plan.stops || plan.stops.length === 0) {
                throw new Error('后端未返回有效的 plan');
            }

            console.log('[onNextStep] ✅ Plan 验证通过，包含', plan.stops.length, '个站点');

            wx.showLoading({
                title: '创建行程...',
                mask: true
            });

            // 3. 调用 /api/trips 创建行程
            const tripRequest = {
                user_openid: 'dev_openid_001',
                request_json: planRequest,
                plan: plan,
                run_id: planData.run_id || null
            };

            console.log('[onNextStep] Trip request:', JSON.stringify(tripRequest, null, 2));

            const tripData = await this.createTrip(tripRequest);
            console.log('[onNextStep] Trip response:', JSON.stringify(tripData, null, 2));

            const tripId = tripData.trip_id;
            if (!tripId) {
                throw new Error('后端未返回 trip_id');
            }

            console.log('[onNextStep] ✅ 行程创建成功，trip_id:', tripId);

            // 4. 保存 trip_id 到 storage（plan 是 tabBar 页面，switchTab 不能带参数）
            wx.setStorageSync('last_trip_id', tripId);
            console.log('[onNextStep] 📝 已保存 trip_id 到 storage:', tripId);

            wx.hideLoading();
            wx.showToast({
                title: '行程创建成功',
                icon: 'success',
                duration: 1500
            });

            // 5. 跳转到 Plan 页面（使用 switchTab，因为 plan 是 tabBar 页面）
            setTimeout(() => {
                console.log('[onNextStep] 准备切换到 Plan 页面...');
                wx.switchTab({
                    url: '/pages/plan/index',
                    success: () => {
                        console.log('[onNextStep] ✅ 成功切换到 Plan 页面（tabBar）');
                    },
                    fail: (err) => {
                        console.error('[onNextStep] ❌ switchTab 失败:', err);
                        wx.showToast({
                            title: '跳转失败',
                            icon: 'none'
                        });
                    }
                });
            }, 1500);

        } catch (error) {
            console.error('[onNextStep] ❌ 错误:', error);
            wx.hideLoading();
            wx.showToast({
                title: error.message || '生成失败',
                icon: 'none',
                duration: 3000
            });
        }
    },

    // 调用 /api/plan/v2
    generatePlanV2(planRequest) {
        const { API_BASE_URL } = require('../../utils/config.js');
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE_URL}/api/plan/v2`,
                method: 'POST',
                data: planRequest,
                success: (res) => {
                    if (res.statusCode === 200 && res.data) {
                        resolve(res.data);
                    } else {
                        reject(new Error(`后端返回错误: ${res.statusCode}`));
                    }
                },
                fail: (err) => {
                    reject(new Error(`网络请求失败: ${err.errMsg}`));
                }
            });
        });
    },

    // 调用 /api/trips
    createTrip(tripRequest) {
        const { API_BASE_URL } = require('../../utils/config.js');
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE_URL}/api/trips`,
                method: 'POST',
                data: tripRequest,
                success: (res) => {
                    if (res.statusCode === 200 && res.data) {
                        resolve(res.data);
                    } else {
                        reject(new Error(`后端返回错误: ${res.statusCode}`));
                    }
                },
                fail: (err) => {
                    reject(new Error(`网络请求失败: ${err.errMsg}`));
                }
            });
        });
    }
});
