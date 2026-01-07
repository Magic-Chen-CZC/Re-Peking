const { API_BASE_URL } = require('../../utils/config.js');

Page({
    data: {
        // MBTI Data
        mbtiCode: '',
        mbtiName: '探索者',
        mbtiTheme: 'grey',  // 'blue' | 'yellow' | 'green' | 'purple' | 'grey'

        // Interest Data
        selectedTags: [],
        selectedRouteName: '',
        userTextInput: '',

        // Preferences
        timeBudget: 'half',  // 'half' | 'full'
        transportation: 'walk',  // 'walk' | 'car'
        pacePreference: 'medium',  // 'slow' | 'medium' | 'fast'

        // Loading state
        isLoading: false
    },

    onLoad() {
        // Get MBTI data
        const userMbti = wx.getStorageSync('user_mbti');
        if (userMbti) {
            this.setData({
                mbtiCode: userMbti,
                mbtiName: this.getMbtiName(userMbti),
                mbtiTheme: this.getMbtiTheme(userMbti)
            });
        }

        // Get interest data
        const interestData = wx.getStorageSync('interest_data');
        if (interestData) {
            this.setData({
                selectedTags: interestData.tags || [],
                selectedRouteName: interestData.routeName || '',
                userTextInput: interestData.text || ''
            });
        }
    },

    // Convert MBTI code to friendly name
    getMbtiName(code) {
        const mbtiNames = {
            'INTJ': '理性规划者',
            'INTP': '逻辑探索者',
            'ENTJ': '高效领航者',
            'ENTP': '创意先锋',
            'INFJ': '精神追寻者',
            'INFP': '诗意漫游者',
            'ENFJ': '热情引领者',
            'ENFP': '浪漫冒险家',
            'ISTJ': '可靠守护者',
            'ISFJ': '温情守护者',
            'ESTJ': '务实执行者',
            'ESFJ': '贴心管家',
            'ISTP': '冷静观察者',
            'ISFP': '自由艺术家',
            'ESTP': '活力探险家',
            'ESFP': '欢乐体验家'
        };
        return mbtiNames[code] || '探索者';
    },

    // Get MBTI theme color based on type
    getMbtiTheme(code) {
        if (!code) return 'grey';

        // NT types - Blue (理性分析型)
        if (code.includes('NT')) return 'blue';
        // NF types - Green (精神追求型)
        if (code.includes('NF')) return 'green';
        // SF types - Yellow (感性体验型)
        if (code.includes('SF')) return 'yellow';
        // ST types - Purple (务实高效型)
        if (code.includes('ST')) return 'purple';

        return 'grey';
    },

    // Time selection
    onTimeSelect(e) {
        const value = e.currentTarget.dataset.value;
        this.setData({ timeBudget: value });
    },

    // Transportation selection
    onTransportSelect(e) {
        const value = e.currentTarget.dataset.value;
        this.setData({ transportation: value });
    },

    // Submit - 完整闭环：生成 plan -> 创建 trip -> 跳转
    async onSubmit() {
        if (this.data.isLoading) return;

        // 验证
        if (this.data.selectedTags.length === 0 && !this.data.selectedRouteName && !this.data.userTextInput) {
            wx.showToast({
                title: '请先选择兴趣点',
                icon: 'none'
            });
            return;
        }

        wx.showLoading({
            title: '生成中...',
            mask: true
        });

        this.setData({ isLoading: true });

        try {
            // 1. 从 storage 读取 interest_data（兼容 tags 可能为景点ID）
            const interestData = wx.getStorageSync('interest_data') || {};
            const tags = interestData.tags || this.data.selectedTags || [];
            const routeName = interestData.routeName || this.data.selectedRouteName || '';
            const text = interestData.text || this.data.userTextInput || '';

            // 2. 组装请求参数
            const planRequest = {
                selected_themes: tags.map(t => t.id || t.name || t), // 支持 id/name/string
                time_budget: this.data.timeBudget === 'half' ? 'half_day' : 'full_day',
                mbti: this.data.mbtiCode || null,
                transportation: this.data.transportation === 'walk' ? 'walking' : 'driving',
                user_text_input: text,
                selected_route_name: routeName,
                pace_preference: this.data.pacePreference || 'medium'
            };

            console.log('[onSubmit] ========== 开始生成行程 ==========');
            console.log('[onSubmit] Plan request:', JSON.stringify(planRequest, null, 2));

            // 3. 调用 /api/plan 生成路线规划
            const planData = await this.generatePlan(planRequest);
            console.log('[onSubmit] Plan response (完整):', JSON.stringify(planData, null, 2));

            // 4. 兼容多种字段名，提取 plan
            const plan = planData.plan || planData.route_plan || (planData.data && planData.data.plan) || null;
            
            console.log('[onSubmit] 提取到的 plan:', plan ? '存在' : '不存在');
            if (plan) {
                console.log('[onSubmit] plan.mode:', plan.mode);
                console.log('[onSubmit] plan.stops 数量:', plan.stops ? plan.stops.length : 0);
                if (plan.stops && plan.stops.length > 0) {
                    console.log('[onSubmit] plan.stops[0]:', JSON.stringify(plan.stops[0], null, 2));
                }
            }

            // 5. 验证 plan 和 stops
            if (!plan) {
                console.error('[onSubmit] ❌ plan 为空！完整响应:', planData);
                wx.showToast({
                    title: '后端未返回 plan，请检查接口',
                    icon: 'none',
                    duration: 3000
                });
                throw new Error('后端未返回 plan 字段');
            }

            if (!plan.stops || !Array.isArray(plan.stops)) {
                console.error('[onSubmit] ❌ plan.stops 不存在或不是数组！plan:', plan);
                wx.showToast({
                    title: '后端未返回 stops，请检查 /api/plan 返回结构',
                    icon: 'none',
                    duration: 3000
                });
                throw new Error('plan.stops 不存在或格式不正确');
            }

            if (plan.stops.length === 0) {
                console.error('[onSubmit] ❌ plan.stops 为空数组！plan:', plan);
                wx.showToast({
                    title: 'stops 为空，请重新选择兴趣点',
                    icon: 'none',
                    duration: 3000
                });
                throw new Error('plan.stops 为空');
            }

            console.log('[onSubmit] ✅ plan 验证通过，包含', plan.stops.length, '个站点');

            wx.showLoading({
                title: '创建行程...',
                mask: true
            });

            // 6. 调用 /api/trips 创建行程
            const tripRequest = {
                user_openid: 'dev_openid_001', // 开发阶段使用固定值，后续接入微信登录
                request_json: planRequest,
                plan: plan,
                run_id: planData.run_id || planData.runId || null  // 兼容多种字段名
            };

            console.log('[onSubmit] Trip request:', JSON.stringify(tripRequest, null, 2));

            const tripData = await this.createTrip(tripRequest);
            console.log('[onSubmit] Trip response (完整):', JSON.stringify(tripData, null, 2));

            // 7. 提取 trip_id（兼容多种字段名）
            const tripId = tripData.trip_id || tripData.tripId || tripData.id || null;
            
            if (!tripId) {
                console.error('[onSubmit] ❌ 未返回 trip_id！完整响应:', tripData);
                wx.showToast({
                    title: '创建行程失败：未返回 trip_id',
                    icon: 'none',
                    duration: 3000
                });
                throw new Error('创建行程失败：未返回 trip_id');
            }

            console.log('[onSubmit] ✅ 行程创建成功！trip_id:', tripId);

            // 8. 保存 trip_id 到本地存储
            wx.setStorageSync('last_trip_id', tripId);
            
            wx.hideLoading();
            wx.showToast({
                title: '行程创建成功',
                icon: 'success',
                duration: 1500
            });

            // 9. 跳转到 plan 页面
            // plan 页面是 tabBar 页面，使用 switchTab，它会自动读取 last_trip_id
            console.log('[onSubmit] ✅ 即将跳转到 plan 页面，tripId 已保存到 storage');
            setTimeout(() => {
                wx.switchTab({
                    url: '/pages/plan/index',
                    success: () => {
                        console.log('[onSubmit] ✅ switchTab 成功');
                    },
                    fail: (err) => {
                        console.error('[onSubmit] ❌ switchTab 失败:', err);
                        wx.showToast({
                            title: '跳转失败',
                            icon: 'none'
                        });
                    }
                });
            }, 1500);

        } catch (error) {
            wx.hideLoading();
            console.error('[onSubmit] ========== 错误详情 ==========');
            console.error('[onSubmit] Error message:', error.message);
            console.error('[onSubmit] Error stack:', error.stack);
            console.error('[onSubmit] =====================================');
            
            wx.showToast({
                title: error.message || '生成失败，请重试',
                icon: 'none',
                duration: 3000
            });
        } finally {
            this.setData({ isLoading: false });
        }
    },

    /**
     * 调用后端生成规划
     * @param {Object} requestData - 请求参数
     * @returns {Promise<Object>} plan 数据
     */
    generatePlan(requestData) {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE_URL}/api/plan`,
                method: 'POST',
                data: requestData,
                header: {
                    'Content-Type': 'application/json'
                },
                success: (res) => {
                    console.log('[generatePlan] Response:', res);
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(res.data);
                    } else {
                        console.error('[generatePlan] Failed:', res.data);
                        reject(new Error(`生成规划失败 (${res.statusCode})`));
                    }
                },
                fail: (err) => {
                    console.error('[generatePlan] Network error:', err);
                    reject(new Error('网络错误，请检查连接'));
                }
            });
        });
    },

    /**
     * 调用后端创建行程
     * @param {Object} requestData - 请求参数（含 user_openid, request_json, plan）
     * @returns {Promise<Object>} trip 数据
     */
    createTrip(requestData) {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE_URL}/api/trips`,
                method: 'POST',
                data: requestData,
                header: {
                    'Content-Type': 'application/json'
                },
                success: (res) => {
                    console.log('[createTrip] Response:', res);
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(res.data);
                    } else {
                        console.error('[createTrip] Failed:', res.data);
                        reject(new Error(`创建行程失败 (${res.statusCode})`));
                    }
                },
                fail: (err) => {
                    console.error('[createTrip] Network error:', err);
                    reject(new Error('网络错误，请检查连接'));
                }
            });
        });
    }
});
