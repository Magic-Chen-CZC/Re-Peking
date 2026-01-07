const { API_BASE_URL } = require('../../utils/config.js');
const { normalizeImageSrc, getPoiCoverImage, cleanTempImageUrl } = require('../../utils/imageUtils.js');

// 🔥 样例数据（兜底使用，至少 3 条）
const SAMPLE_POSTS = [
    {
        id: 'sample-001',
        trip_id: null,
        userName: 'Alex Explorer',
        userAvatar: '🎭',
        title: '故宫深度游 · 5 stops',
        reflection: '在故宫的每一步都是历史的回响，太和殿的壮观让我印象深刻。建议早上 8 点前入园，可以避开人流高峰。',
        summary: '在故宫的每一步都是历史的回响，太和殿的壮观让我印象深刻。建议早上 8 点前入园，可以避开人流高峰。',
        content: '在故宫的每一步都是历史的回响，太和殿的壮观让我印象深刻。建议早上 8 点前入园，可以避开人流高峰。',
        cover_poi_id: 'gugong',
        cover_image_url: null,
        imageUrl: '/image/attractions/gugong.png',
        created_at: '2024-01-05T08:00:00+00:00',
        timestamp: '2天前',
        archetype: 'NT',
        likes: 0,
        route: [],
        comments: [],
        tags: []
    },
    {
        id: 'sample-002',
        trip_id: null,
        userName: 'Luna Traveler',
        userAvatar: '🌸',
        title: 'Historical & Cultural · 4 stops',
        reflection: '天坛的建筑设计体现了古人的智慧，回音壁的声学效果令人惊叹。推荐下午去，光线很好适合拍照。',
        summary: '天坛的建筑设计体现了古人的智慧，回音壁的声学效果令人惊叹。推荐下午去，光线很好适合拍照。',
        content: '天坛的建筑设计体现了古人的智慧，回音壁的声学效果令人惊叹。推荐下午去，光线很好适合拍照。',
        cover_poi_id: 'tiantan',
        cover_image_url: null,
        imageUrl: '/image/attractions/tiantan.png',
        created_at: '2024-01-04T14:30:00+00:00',
        timestamp: '3天前',
        archetype: 'NF',
        likes: 0,
        route: [],
        comments: [],
        tags: []
    },
    {
        id: 'sample-003',
        trip_id: null,
        userName: 'David Historian',
        userAvatar: '📚',
        title: '颐和园半日游 · 3 stops',
        reflection: '颐和园的湖光山色美不胜收，长廊的彩绘值得细细品味。建议预留至少 3 小时游览。',
        summary: '颐和园的湖光山色美不胜收，长廊的彩绘值得细细品味。建议预留至少 3 小时游览。',
        content: '颐和园的湖光山色美不胜收，长廊的彩绘值得细细品味。建议预留至少 3 小时游览。',
        cover_poi_id: 'yiheyuan',
        cover_image_url: null,
        imageUrl: '/image/attractions/yiheyuan.png',
        created_at: '2024-01-03T10:00:00+00:00',
        timestamp: '4天前',
        archetype: 'SJ',
        likes: 0,
        route: [],
        comments: [],
        tags: []
    }
];

Page({
    data: {
        posts: [],
        layoutConfigs: [],
        focusedIndex: null,
        selectedPost: null,
        detailRouteExpanded: false,
        detailStopsExpanded: false,
        detailShowCommentInput: false,
        detailRouteDisplay: [],
        detailStopsDisplay: [],
        detailRouteTotal: 0,
        detailStopsTotal: 0,
        detailCommentText: '',
        userOpenId: 'dev_openid_001',
        tripHistory: [],
        tripHistoryLabels: [],
        selectedTripIndex: 0,
        isRefreshing: false,
        showPublishModal: false,
        newPost: {
            title: '',
            content: '',
            imageUrl: '',
            tripId: '',
            tripContent: [],
            lockTripSelection: false,
            tripLabel: ''
        }
    },

    onLoad() {
        console.log('[Community] onLoad 页面加载');
    },

    onShow() {
        console.log('[Community] onShow 页面显示');
        
        // 设置 TabBar 选中状态
        if (typeof this.getTabBar === 'function' && this.getTabBar()) {
            this.getTabBar().setData({
                selected: 2
            })
        }

        // 🔥 拉取真实的社区分享数据
        this.fetchPosts();

        // 🔥 应用待聚焦的 post（如果有）
        this.applyPendingPostFocus();

        // 🔥 检查是否有待发布的 draft
        this.applyPendingPostDraft();
    },

    /**
     * 拉取社区分享列表
     */
    fetchPosts() {
        console.log('[fetchPosts] 🚀 开始拉取社区分享列表');

        const url = `${API_BASE_URL}/api/posts?limit=20`;
        console.log('[fetchPosts] 📤 请求 URL:', url);

        wx.request({
            url: url,
            method: 'GET',
            success: (res) => {
                console.log('[fetchPosts] 📥 响应 statusCode:', res.statusCode);
                console.log('[fetchPosts] 📥 响应 data:', res.data);

                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const posts = res.data || [];
                    console.log('[fetchPosts] ✅ 成功获取', posts.length, '条分享');

                    if (posts.length === 0) {
                        console.log('[fetchPosts] ⚠️ 数据为空，使用样例数据');
                        this.renderSamplePosts();
                        return;
                    }

                    // 🔥 转换后端数据格式为前端展示格式
                    const formattedPosts = posts.map((post, index) => {
                        // 🔥 优先使用 cover_poi_id 的本地图片作为兜底
                        const fallbackImage = getPoiCoverImage(post.cover_poi_id);
                        
                        // 🔥 规范化图片 URL：
                        // - 如果 cover_image_url 为空/null，使用 fallbackImage
                        // - 如果是临时路径，使用 fallbackImage
                        // - 如果是完整 URL 或本地路径，正常显示
                        const imageUrl = normalizeImageSrc(post.cover_image_url, fallbackImage);

                        // 🔥 使用 reflection 作为摘要
                        const summary = post.reflection || post.title || '暂无摘要';

                        return {
                            id: post.id,
                            trip_id: post.trip_id, // 🔥 保留 trip_id 用于点击跳转到详情页
                            userName: 'Explorer', // 默认用户名（后续可从 user_id 查询）
                            userAvatar: '🧳',
                            title: post.title,
                            content: summary,
                            summary: summary,
                            reflection: post.reflection, // 🔥 保留原始 reflection
                            cover_poi_id: post.cover_poi_id || 'gugong',
                            cover_image_url: post.cover_image_url, // 🔥 保留原始 cover_image_url
                            imageUrl: imageUrl,  // 🔥 规范化后的图片 URL，用于渲染
                            timestamp: this.formatTimestamp(post.created_at),
                            created_at: post.created_at, // 🔥 保留原始时间戳
                            likes: 0,
                            route: [],
                            comments: [],
                            tags: [],
                            comments_count: post.comments_count || 0,
                            likes_count: post.likes_count || 0,
                            archetype: 'NT' // 默认 archetype
                        };
                    });

                    // 生成布局配置
                    const layoutConfigs = formattedPosts.map(() => ({
                        rotate: Math.random() * 12 - 6,
                        x: Math.random() * 16 - 8,
                        y: 0
                    }));

                    this.setData({
                        posts: formattedPosts,
                        layoutConfigs: layoutConfigs
                    });

                    console.log('[fetchPosts] ✅ 数据已设置到 data.posts');
                } else {
                    console.error('[fetchPosts] ❌ 获取失败:', res);
                    // 失败时显示样例数据
                    this.renderSamplePosts();
                }
            },
            fail: (err) => {
                console.error('[fetchPosts] ❌ 网络错误:', err);
                // 网络错误时显示样例数据
                this.renderSamplePosts();
            }
        });
    },

    /**
     * 渲染样例数据
     */
    renderSamplePosts() {
        console.log('[renderSamplePosts] 使用样例数据');
        
        const layoutConfigs = SAMPLE_POSTS.map(() => ({
            rotate: Math.random() * 12 - 6,
            x: Math.random() * 16 - 8,
            y: 0
        }));

        this.setData({
            posts: SAMPLE_POSTS,
            layoutConfigs: layoutConfigs
        });
    },

    /**
     * 应用待聚焦的 post
     */
    applyPendingPostFocus() {
        console.log('[applyPendingPostFocus] 检查待聚焦的 post');

        try {
            const pendingPostFocus = wx.getStorageSync('pending_post_focus');
            
            if (pendingPostFocus && pendingPostFocus.postId) {
                console.log('[applyPendingPostFocus] 📌 找到待聚焦的 post:', pendingPostFocus);

                const postId = pendingPostFocus.postId;

                // 🔥 查找对应的 post 索引
                const postIndex = this.data.posts.findIndex(post => post.id === postId);

                if (postIndex !== -1) {
                    console.log('[applyPendingPostFocus] ✅ 找到对应 post，索引:', postIndex);

                    // 🔥 高亮该 post（设置为 focused）
                    this.setData({
                        focusedIndex: postIndex
                    });

                    // 🔥 滚动到该 post（延迟一下确保渲染完成）
                    setTimeout(() => {
                        wx.pageScrollTo({
                            selector: `.scattered-ticket:nth-child(${postIndex + 1})`,
                            duration: 300,
                            success: () => {
                                console.log('[applyPendingPostFocus] ✅ 已滚动到目标 post');
                            },
                            fail: (err) => {
                                console.warn('[applyPendingPostFocus] ⚠️ 滚动失败，尝试按索引滚动:', err);
                                // 备选方案：按估算的位置滚动
                                const scrollTop = postIndex * 200; // 假设每个卡片约 200px
                                wx.pageScrollTo({
                                    scrollTop: scrollTop,
                                    duration: 300
                                });
                            }
                        });
                    }, 500);

                    // 🔥 3秒后取消高亮
                    setTimeout(() => {
                        this.setData({
                            focusedIndex: null
                        });
                    }, 3000);
                } else {
                    console.warn('[applyPendingPostFocus] ⚠️ 未找到对应的 post，可能还未加载');
                }

                // 🔥 清除 storage
                wx.removeStorageSync('pending_post_focus');
                console.log('[applyPendingPostFocus] ✅ 已清除 pending_post_focus');
            } else {
                console.log('[applyPendingPostFocus] 没有待聚焦的 post');
            }
        } catch (err) {
            console.error('[applyPendingPostFocus] ❌ 错误:', err);
        }
    },

    /**
     * 应用待发布的 post draft
     * 从 Plan 页跳转过来时会带有 draft
     */
    applyPendingPostDraft() {
        console.log('[applyPendingPostDraft] 检查待发布的 draft');

        try {
            const draft = wx.getStorageSync('pending_post_draft');
            
            if (draft && draft.ts && draft.tripId) {
                console.log('[applyPendingPostDraft] 📌 找到待发布的 draft:', draft);

                // 检查是否过期（30秒）
                const now = Date.now();
                const age = now - draft.ts;
                
                if (age > 30000) {
                    console.warn('[applyPendingPostDraft] ⚠️ draft 已过期（>30s），忽略');
                    wx.removeStorageSync('pending_post_draft');
                    return;
                }

                const tripLabel = draft.tripLabel || `本次行程 · ${draft.tripContent.length || 0} 个地点`;

                // 🔥 自动打开发布弹窗（锁定地点选择）
                this.setData({
                    showPublishModal: true,
                    newPost: {
                        tripId: draft.tripId,
                        tripContent: draft.tripContent || [],
                        title: '',
                        content: '',
                        imageUrl: '',
                        lockTripSelection: true,
                        tripLabel: tripLabel
                    },
                    tripHistory: [],
                    tripHistoryLabels: [tripLabel],
                    selectedTripIndex: 0
                });

                console.log('[applyPendingPostDraft] ✅ 已打开发布弹窗');

                // 🔥 清除 storage，防止重复触发
                wx.removeStorageSync('pending_post_draft');
                console.log('[applyPendingPostDraft] ✅ 已清除 pending_post_draft');
            } else {
                console.log('[applyPendingPostDraft] 没有待发布的 draft');
            }
        } catch (err) {
            console.error('[applyPendingPostDraft] ❌ 错误:', err);
        }
    },

    /**
     * 格式化时间戳
     * @param {string} isoString - ISO 8601 时间字符串
     * @returns {string} 格式化后的时间（如 "2小时前"）
     */
    formatTimestamp(isoString) {
        if (!isoString) return '';

        try {
            const date = new Date(isoString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);

            if (diffMins < 1) return '刚刚';
            if (diffMins < 60) return `${diffMins}分钟前`;
            if (diffHours < 24) return `${diffHours}小时前`;
            if (diffDays < 7) return `${diffDays}天前`;

            // 超过7天显示日期
            const month = date.getMonth() + 1;
            const day = date.getDate();
            return `${month}月${day}日`;
        } catch (err) {
            console.error('[formatTimestamp] 错误:', err);
            return '';
        }
    },

    onPullDownRefresh() {
        this.setData({
            isRefreshing: true,
            focusedIndex: null,
            selectedPost: null
        });
        setTimeout(() => {
            this.fetchPosts();
            this.setData({ isRefreshing: false });
        }, 1000);
    },

    // --- Publish Logic ---
    openPublishModal() {
        this.setData({
            showPublishModal: true,
            newPost: {
                title: '',
                content: '',
                imageUrl: '',
                tripId: '',
                tripContent: [],
                lockTripSelection: false,
                tripLabel: ''
            }
        }, () => {
            this.fetchTripHistory();
        });
    },

    closePublishModal() {
        this.setData({ showPublishModal: false });
    },

    handleImageUpload() {
        wx.chooseMedia({
            count: 1,
            mediaType: ['image'],
            sourceType: ['album', 'camera'],
            success: (res) => {
                const tempFilePath = res.tempFiles[0].tempFilePath;
                wx.showLoading({
                    title: '上传中...',
                    mask: true
                });

                wx.uploadFile({
                    url: `${API_BASE_URL}/api/uploads/image`,
                    filePath: tempFilePath,
                    name: 'file',
                    success: (uploadRes) => {
                        wx.hideLoading();
                        try {
                            const data = JSON.parse(uploadRes.data || '{}');
                            if (uploadRes.statusCode >= 200 && uploadRes.statusCode < 300 && data.url) {
                                this.setData({
                                    'newPost.imageUrl': data.url
                                });
                                wx.showToast({ title: '上传成功', icon: 'success' });
                            } else {
                                wx.showToast({ title: '上传失败', icon: 'none' });
                            }
                        } catch (err) {
                            wx.showToast({ title: '上传失败', icon: 'none' });
                        }
                    },
                    fail: () => {
                        wx.hideLoading();
                        wx.showToast({ title: '上传失败', icon: 'none' });
                    }
                });
            }
        });
    },

    fetchTripHistory() {
        const { userOpenId } = this.data;
        const url = `${API_BASE_URL}/api/trips/history?user_openid=${userOpenId}&limit=20`;
        console.log('[fetchTripHistory] 📤 请求 URL:', url);

        wx.request({
            url,
            method: 'GET',
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300 && Array.isArray(res.data)) {
                    const tripHistory = res.data;
                    const labels = tripHistory.map((trip) => {
                        const stopCount = Array.isArray(trip.stops) ? trip.stops.length : 0;
                        return `${trip.title || '我的旅程'} · ${stopCount} 个地点`;
                    });
                    const selectedTripIndex = 0;
                    const selectedTrip = tripHistory[selectedTripIndex];

                    this.setData({
                        tripHistory,
                        tripHistoryLabels: labels,
                        selectedTripIndex,
                        'newPost.tripId': selectedTrip ? selectedTrip.trip_id : '',
                        'newPost.tripContent': selectedTrip ? selectedTrip.stops : []
                    });
                } else {
                    console.warn('[fetchTripHistory] ⚠️ 获取历史失败:', res);
                    this.setData({
                        tripHistory: [],
                        tripHistoryLabels: [],
                        selectedTripIndex: 0,
                        'newPost.tripId': '',
                        'newPost.tripContent': []
                    });
                }
            },
            fail: (err) => {
                console.warn('[fetchTripHistory] ⚠️ 网络错误:', err);
                this.setData({
                    tripHistory: [],
                    tripHistoryLabels: [],
                    selectedTripIndex: 0,
                    'newPost.tripId': '',
                    'newPost.tripContent': []
                });
            }
        });
    },

    handleTripPickerChange(e) {
        const index = Number(e.detail.value) || 0;
        const selectedTrip = this.data.tripHistory[index];
        this.setData({
            selectedTripIndex: index,
            'newPost.tripId': selectedTrip ? selectedTrip.trip_id : '',
            'newPost.tripContent': selectedTrip ? selectedTrip.stops : []
        });
    },

    handleTitleInput(e) {
        this.setData({ 'newPost.title': e.detail.value });
    },

    handleContentInput(e) {
        this.setData({ 'newPost.content': e.detail.value });
    },

    handleSubmitPost() {
        const { tripId, tripContent, title, content, imageUrl } = this.data.newPost;

        console.log('[handleSubmitPost] 🚀 开始发布文章');
        console.log('[handleSubmitPost] 数据:', { tripId, tripContent, title, content, imageUrl });

        // 🔥 校验必填字段
        if (!title || !content) {
            wx.showToast({ 
                title: '请填写标题和感想', 
                icon: 'none',
                duration: 2000
            });
            return;
        }

        if (!tripId) {
            wx.showToast({ 
                title: 'tripId 缺失', 
                icon: 'none',
                duration: 2000
            });
            return;
        }

        // 🔥 选择一个代表性的 POI 作为封面
        let coverPoiId = 'default';
        if (tripContent && tripContent.length > 0) {
            const firstStop = tripContent[0];
            if (firstStop.poi_id) {
                coverPoiId = firstStop.poi_id;
            }
        }

        // 🔥 清理临时图片路径（wxfile:// 或 http://tmp/）
        const cleanedImageUrl = cleanTempImageUrl(imageUrl);
        
        // 🔥 构造请求 payload
        const payload = {
            trip_id: tripId,
            title: title,
            reflection: content, // 用户感想
            cover_image_url: cleanedImageUrl || null, // 封面图片（临时路径已清理）
            cover_poi_id: coverPoiId // 封面 POI
        };

        console.log('[handleSubmitPost] 📤 请求 payload:', payload);
        if (imageUrl && !cleanedImageUrl) {
            console.log('[handleSubmitPost] ⚠️ 临时图片路径已清理:', imageUrl, '→', cleanedImageUrl);
        }

        // 显示加载提示
        wx.showLoading({
            title: '发布中...',
            mask: true
        });

        // 🔥 调用后端 API
        const url = `${API_BASE_URL}/api/posts`;
        console.log('[handleSubmitPost] 📤 请求 URL:', url);

        wx.request({
            url: url,
            method: 'POST',
            header: {
                'Content-Type': 'application/json'
            },
            data: payload,
            success: (res) => {
                wx.hideLoading();
                console.log('[handleSubmitPost] 📥 响应 statusCode:', res.statusCode);
                console.log('[handleSubmitPost] 📥 响应 data:', res.data);

                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log('[handleSubmitPost] ✅ 发布成功');

                    // 关闭弹窗
                    this.setData({
                        showPublishModal: false,
                        focusedIndex: null
                    });

                    // 提示成功
                    wx.showToast({ 
                        title: '发布成功！', 
                        icon: 'success',
                        duration: 2000
                    });

                    // 重新拉取列表
                    setTimeout(() => {
                        this.fetchPosts();
                        // 滚动到顶部
                        wx.pageScrollTo({ scrollTop: 0 });
                    }, 500);
                } else {
                    console.error('[handleSubmitPost] ❌ 发布失败:', res);
                    
                    // 🔥 显示详细错误信息（从 detail 字段）
                    const errorDetail = res.data?.detail || '发布失败，请重试';
                    wx.showModal({
                        title: `发布失败 (${res.statusCode})`,
                        content: errorDetail,
                        showCancel: false,
                        confirmText: '知道了'
                    });
                }
            },
            fail: (err) => {
                wx.hideLoading();
                console.error('[handleSubmitPost] ❌ 网络错误:', err);
                
                wx.showModal({
                    title: '网络错误',
                    content: '请检查网络连接后重试',
                    showCancel: false,
                    confirmText: '知道了'
                });
            }
        });
    },
    // --- End Publish Logic ---

    /**
     * 点击 post 卡片 - 打开详情弹窗
     * @param {Object} e - 事件对象
     */
    handlePostClick(e) {
        const post = e.detail.post;
        console.log('[handlePostClick] 🎯 点击 post:', post);

        const postId = post.id;
        if (!postId) {
            console.error('[handlePostClick] ❌ post 缺少 id:', post);
            wx.showToast({
                title: 'postId 缺失',
                icon: 'none',
                duration: 2000
            });
            return;
        }

        console.log('[handlePostClick] 📍 打开详情弹窗，postId:', postId);

        // 先用卡片数据占位，再拉详情
        const basePost = this.formatPostPreview(post);
        this.setDetailState(basePost);

        this.fetchPostDetail(postId);
    },

    handlePostLongPress(e) {
        const index = e.detail.index;
        // Toggle focus: if already focused, unfocus; otherwise focus
        if (this.data.focusedIndex === index) {
            this.setData({ focusedIndex: null });
        } else {
            this.setData({ focusedIndex: index });
        }
    },

    closeModal() {
        this.setData({
            selectedPost: null,
            detailCommentText: '',
            detailShowCommentInput: false
        });
    },

    // Prevent bubbling
    noop() { },

    /**
     * 详情弹窗：折叠/展开路线
     */
    toggleRouteExpanded() {
        this.setData(
            { detailRouteExpanded: !this.data.detailRouteExpanded },
            () => this.updateDetailDisplays()
        );
    },

    /**
     * 详情弹窗：折叠/展开地点详情
     */
    toggleStopsExpanded() {
        this.setData(
            { detailStopsExpanded: !this.data.detailStopsExpanded },
            () => this.updateDetailDisplays()
        );
    },

    /**
     * 详情弹窗：显示/隐藏评论输入
     */
    toggleCommentInput() {
        this.setData({ detailShowCommentInput: !this.data.detailShowCommentInput });
    },

    handleDetailCommentInput(e) {
        this.setData({ detailCommentText: e.detail.value });
    },

    submitDetailComment() {
        const post = this.data.selectedPost;
        const content = (this.data.detailCommentText || '').trim();
        if (!post || !post.id) {
            return;
        }
        if (!content) {
            wx.showToast({ title: '请输入评论内容', icon: 'none' });
            return;
        }

        const payload = {
            user_openid: this.data.userOpenId,
            content
        };

        wx.request({
            url: `${API_BASE_URL}/api/posts/${post.id}/comments`,
            method: 'POST',
            header: { 'Content-Type': 'application/json' },
            data: payload,
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300 && res.data) {
                    const newComment = {
                        id: res.data.id,
                        user: '游客',
                        text: res.data.content,
                        created_at: res.data.created_at
                    };
                    const updatedComments = [...(post.comments || []), newComment];
                    this.setData({
                        'selectedPost.comments': updatedComments,
                        'selectedPost.commentCount': updatedComments.length,
                        detailCommentText: ''
                    });
                    wx.showToast({ title: '评论已发布', icon: 'success' });
                } else {
                    wx.showToast({ title: '评论失败', icon: 'none' });
                }
            },
            fail: () => {
                wx.showToast({ title: '网络错误', icon: 'none' });
            }
        });
    },

    toggleLike() {
        const post = this.data.selectedPost;
        if (!post || !post.id) {
            return;
        }

        const liked = !!post.liked;
        const method = liked ? 'DELETE' : 'POST';
        const url = `${API_BASE_URL}/api/posts/${post.id}/likes?user_openid=${this.data.userOpenId}`;

        wx.request({
            url,
            method,
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300 && res.data) {
                    this.setData({
                        'selectedPost.liked': res.data.liked,
                        'selectedPost.likeCount': res.data.likes_count
                    });
                } else {
                    wx.showToast({ title: '点赞失败', icon: 'none' });
                }
            },
            fail: () => {
                wx.showToast({ title: '网络错误', icon: 'none' });
            }
        });
    },

    /**
     * 拉取详情并更新弹窗
     * @param {string} postId
     */
    fetchPostDetail(postId) {
        const { userOpenId } = this.data;
        const url = `${API_BASE_URL}/api/posts/${postId}?user_openid=${userOpenId}`;
        console.log('[fetchPostDetail] 📤 请求 URL:', url);

        wx.request({
            url,
            method: 'GET',
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300 && res.data) {
                    const formatted = this.formatPostDetail(res.data);
                    this.setDetailState(formatted);
                } else {
                    console.warn('[fetchPostDetail] ⚠️ 详情获取失败，保留预览数据:', res);
                }
            },
            fail: (err) => {
                console.warn('[fetchPostDetail] ⚠️ 网络错误，保留预览数据:', err);
            }
        });
    },

    /**
     * 详情弹窗：设置数据并刷新显示列表
     * @param {Object} post
     */
    setDetailState(post) {
        this.setData(
            {
                selectedPost: post,
                detailRouteExpanded: false,
                detailStopsExpanded: false,
                detailShowCommentInput: false
            },
            () => this.updateDetailDisplays()
        );
    },

    /**
     * 详情弹窗：更新折叠显示列表
     */
    updateDetailDisplays() {
        const previewCount = 3;
        const post = this.data.selectedPost || {};
        const route = Array.isArray(post.route) ? post.route : [];
        const stops = Array.isArray(post.tripStops) ? post.tripStops : [];

        const routeDisplay = this.data.detailRouteExpanded ? route : route.slice(0, previewCount);
        const stopsDisplay = this.data.detailStopsExpanded ? stops : stops.slice(0, previewCount);

        this.setData({
            detailRouteDisplay: routeDisplay,
            detailStopsDisplay: stopsDisplay,
            detailRouteTotal: route.length,
            detailStopsTotal: stops.length
        });
    },

    /**
     * 预览卡片数据 -> 详情弹窗基础格式
     * @param {Object} post
     */
    formatPostPreview(post) {
        const fallbackImage = getPoiCoverImage(post.cover_poi_id);
        const imageUrl = normalizeImageSrc(post.cover_image_url, fallbackImage);
        const summary = post.reflection || post.title || '暂无简介';

        return {
            id: post.id,
            title: post.title || '无标题',
            reflection: summary,
            imageUrl,
            cover_poi_id: post.cover_poi_id || '',
            route: [],
            tripStops: [],
            comments: [],
            commentCount: post.comments_count || 0,
            likeCount: post.likes_count || 0,
            liked: false
        };
    },

    /**
     * 详情接口数据 -> 详情弹窗格式
     * @param {Object} postData
     */
    formatPostDetail(postData) {
        const fallbackImage = getPoiCoverImage(postData.cover_poi_id);
        const imageUrl = normalizeImageSrc(postData.cover_image_url, fallbackImage);

        const manifest = postData.manifest_json || {};
        const stops = Array.isArray(manifest.stops) ? manifest.stops : [];

        const tripStops = stops.map((stop, index) => ({
            seq: stop.seq || index + 1,
            poi_id: stop.poi_id || '',
            name: stop.name || '未知地点',
            aiSummary: stop.ai_summary || '',
            userLogs: stop.user_logs || []
        }));

        const route = tripStops.map((stop) => stop.name);
        const comments = Array.isArray(postData.comments) ? postData.comments : [];

        return {
            id: postData.id,
            title: postData.title || '无标题',
            reflection: postData.reflection || '暂无简介',
            imageUrl,
            cover_poi_id: postData.cover_poi_id || '',
            route,
            tripStops,
            comments: comments.map((c) => ({
                id: c.id,
                user: '游客',
                text: c.content,
                created_at: c.created_at
            })),
            commentCount: postData.comments_count || comments.length || 0,
            likeCount: postData.likes_count || 0,
            liked: !!postData.user_liked
        };
    }
})
