const { API_BASE_URL } = require('../../utils/config.js');

Page({
    data: {
        tripId: '',
        tripDetail: null,
        
        // 表单数据
        title: '',
        reflection: '',
        coverLocalPath: '',  // 本地临时路径
        coverUrl: '',        // 上传后的 URL
        coverPoiId: '',      // 备选封面 POI ID（第一站）
        
        // 状态
        isPublishing: false,
        isLoading: true
    },

    /**
     * 页面加载
     */
    onLoad(options) {
        console.log('[share_edit] onLoad, options:', options);
        
        const tripId = options.trip_id;
        
        if (!tripId) {
            console.error('[share_edit] ❌ trip_id 缺失');
            wx.showToast({
                title: 'trip_id 缺失',
                icon: 'none',
                duration: 2000
            });
            
            // 返回上一页
            setTimeout(() => {
                wx.navigateBack();
            }, 2000);
            return;
        }
        
        this.setData({ tripId });
        
        // 加载行程详情
        this.fetchTripDetail(tripId);
    },

    /**
     * 加载行程详情
     */
    fetchTripDetail(tripId) {
        console.log('[fetchTripDetail] 开始加载 trip 详情, tripId:', tripId);
        
        wx.showLoading({ title: '加载中...', mask: true });
        
        const url = `${API_BASE_URL}/api/trips/${tripId}`;
        console.log('[fetchTripDetail] 📤 请求 URL:', url);
        
        wx.request({
            url: url,
            method: 'GET',
            success: (res) => {
                console.log('[fetchTripDetail] 📥 响应 statusCode:', res.statusCode);
                console.log('[fetchTripDetail] 📥 响应 data:', res.data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const tripDetail = res.data;
                    
                    // 生成默认标题
                    const stopsCount = tripDetail.stops ? tripDetail.stops.length : 0;
                    let defaultTitle = `Trip · ${stopsCount} stops`;
                    
                    // 尝试从 request_json 提取主题
                    if (tripDetail.request_json && tripDetail.request_json.selected_themes) {
                        const themes = tripDetail.request_json.selected_themes;
                        if (themes.length > 0) {
                            const themesStr = themes.slice(0, 3).join(' & ');
                            defaultTitle = `${themesStr} · ${stopsCount} stops`;
                        }
                    }
                    
                    // 获取第一站作为封面 POI
                    let coverPoiId = '';
                    if (tripDetail.stops && tripDetail.stops.length > 0) {
                        coverPoiId = tripDetail.stops[0].poi_id || '';
                    }
                    
                    this.setData({
                        tripDetail: tripDetail,
                        title: defaultTitle,
                        coverPoiId: coverPoiId,
                        isLoading: false
                    });
                    
                    console.log('[fetchTripDetail] ✅ trip 详情加载成功');
                } else {
                    console.error('[fetchTripDetail] ❌ 加载失败:', res);
                    wx.showToast({
                        title: `加载失败 (${res.statusCode})`,
                        icon: 'none',
                        duration: 2000
                    });
                    
                    this.setData({ isLoading: false });
                }
            },
            fail: (err) => {
                console.error('[fetchTripDetail] ❌ 网络错误:', err);
                wx.showToast({
                    title: '网络错误，请稍后重试',
                    icon: 'none',
                    duration: 2000
                });
                
                this.setData({ isLoading: false });
            },
            complete: () => {
                wx.hideLoading();
            }
        });
    },

    /**
     * 标题输入
     */
    onTitleInput(e) {
        this.setData({
            title: e.detail.value
        });
    },

    /**
     * 感想输入
     */
    onReflectionInput(e) {
        this.setData({
            reflection: e.detail.value
        });
    },

    /**
     * 选择图片
     */
    chooseImage() {
        console.log('[chooseImage] 选择图片');
        
        wx.chooseImage({
            count: 1,
            sizeType: ['compressed'],
            sourceType: ['album', 'camera'],
            success: (res) => {
                const tempFilePath = res.tempFilePaths[0];
                console.log('[chooseImage] ✅ 选择成功，临时路径:', tempFilePath);
                
                this.setData({
                    coverLocalPath: tempFilePath
                });
                
                wx.showToast({
                    title: '图片已选择',
                    icon: 'success',
                    duration: 1000
                });
            },
            fail: (err) => {
                console.error('[chooseImage] ❌ 选择失败:', err);
                wx.showToast({
                    title: '选择失败，请重试',
                    icon: 'none',
                    duration: 2000
                });
            }
        });
    },

    /**
     * 上传图片
     */
    uploadImage() {
        return new Promise((resolve, reject) => {
            const { coverLocalPath } = this.data;
            
            if (!coverLocalPath) {
                resolve(null);
                return;
            }
            
            console.log('[uploadImage] 开始上传图片, localPath:', coverLocalPath);
            
            wx.uploadFile({
                url: `${API_BASE_URL}/api/uploads/image`,
                filePath: coverLocalPath,
                name: 'file',
                success: (res) => {
                    console.log('[uploadImage] 📥 响应 statusCode:', res.statusCode);
                    console.log('[uploadImage] 📥 响应 data:', res.data);
                    
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        try {
                            const data = JSON.parse(res.data);
                            const coverUrl = data.url;
                            
                            console.log('[uploadImage] ✅ 上传成功，URL:', coverUrl);
                            resolve(coverUrl);
                        } catch (e) {
                            console.error('[uploadImage] ❌ 解析响应失败:', e);
                            reject(new Error('解析响应失败'));
                        }
                    } else {
                        console.error('[uploadImage] ❌ 上传失败:', res);
                        reject(new Error(`上传失败 (${res.statusCode})`));
                    }
                },
                fail: (err) => {
                    console.error('[uploadImage] ❌ 网络错误:', err);
                    reject(err);
                }
            });
        });
    },

    /**
     * 发布到社区
     */
    async publish() {
        console.log('[publish] 🚀 开始发布到社区');
        
        const { tripId, title, reflection, coverLocalPath, coverPoiId, isPublishing } = this.data;
        
        // 防止重复提交
        if (isPublishing) {
            console.log('[publish] ⚠️ 正在发布中，忽略重复请求');
            return;
        }
        
        // 验证标题
        if (!title || title.trim() === '') {
            wx.showToast({
                title: '请输入标题',
                icon: 'none',
                duration: 2000
            });
            return;
        }
        
        this.setData({ isPublishing: true });
        wx.showLoading({ title: '发布中...', mask: true });
        
        try {
            // 1. 如果有本地图片，先上传
            let coverUrl = null;
            if (coverLocalPath) {
                console.log('[publish] 📤 上传图片中...');
                coverUrl = await this.uploadImage();
                console.log('[publish] ✅ 图片上传成功:', coverUrl);
            }
            
            // 2. 创建 post
            console.log('[publish] 📤 创建 post...');
            const postData = {
                trip_id: tripId,
                title: title.trim(),
                reflection: reflection.trim() || null,
                cover_image_url: coverUrl,
                cover_poi_id: coverPoiId || null
            };
            
            console.log('[publish] 📤 请求数据:', postData);
            
            const postResponse = await this.createPost(postData);
            
            console.log('[publish] ✅ post 创建成功:', postResponse);
            
            // 3. 写入 pending_post_focus
            const pendingPostFocus = {
                postId: postResponse.post_id,
                ts: Date.now()
            };
            wx.setStorageSync('pending_post_focus', pendingPostFocus);
            console.log('[publish] 📝 pending_post_focus 已写入:', pendingPostFocus);
            
            // 4. 显示成功提示
            wx.showToast({
                title: '发布成功！',
                icon: 'success',
                duration: 2000
            });
            
            // 5. 延迟后跳转到社区页
            setTimeout(() => {
                wx.switchTab({
                    url: '/pages/community/index',
                    success: () => {
                        console.log('[publish] ✅ 成功切换到社区页');
                    },
                    fail: (err) => {
                        console.error('[publish] ❌ switchTab 失败:', err);
                    }
                });
            }, 1000);
            
        } catch (err) {
            console.error('[publish] ❌ 发布失败:', err);
            wx.showToast({
                title: err.message || '发布失败，请重试',
                icon: 'none',
                duration: 3000
            });
        } finally {
            this.setData({ isPublishing: false });
            wx.hideLoading();
        }
    },

    /**
     * 创建 post（Promise 包装）
     */
    createPost(postData) {
        return new Promise((resolve, reject) => {
            const url = `${API_BASE_URL}/api/posts`;
            console.log('[createPost] 📤 请求 URL:', url);
            console.log('[createPost] 📤 请求 body:', postData);
            
            wx.request({
                url: url,
                method: 'POST',
                header: {
                    'Content-Type': 'application/json'
                },
                data: postData,
                success: (res) => {
                    console.log('[createPost] 📥 响应 statusCode:', res.statusCode);
                    console.log('[createPost] 📥 响应 data:', res.data);
                    
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(res.data);
                    } else {
                        reject(new Error(`创建失败 (${res.statusCode})`));
                    }
                },
                fail: (err) => {
                    console.error('[createPost] ❌ 网络错误:', err);
                    reject(err);
                }
            });
        });
    },

    /**
     * 取消发布（返回上一页）
     */
    cancel() {
        console.log('[cancel] 取消发布');
        wx.navigateBack();
    }
})
