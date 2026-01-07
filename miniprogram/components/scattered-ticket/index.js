Component({
    properties: {
        post: Object,
        index: Number,
        isFocused: Boolean,
        layoutConfig: {
            type: Object,
            value: { x: 0, y: 0, rotate: 0 }
        }
    },
    data: {
        theme: {},
        safeLayout: { x: 0, y: 0, rotate: 0 }
    },
    observers: {
        'post.archetype': function (archetype) {
            this.updateTheme(archetype);
        },
        'layoutConfig': function (cfg) {
            const safe = (cfg && typeof cfg === 'object')
                ? { x: Number(cfg.x) || 0, y: Number(cfg.y) || 0, rotate: Number(cfg.rotate) || 0 }
                : { x: 0, y: 0, rotate: 0 };
            this.setData({ safeLayout: safe });
        }
    },
    methods: {
        updateTheme(archetype) {
            let theme = {};
            switch (archetype) {
                case 'NT': theme = { bg: 'bg-indigo-600', text: 'text-white' }; break;
                case 'NF': theme = { bg: 'bg-emerald-600', text: 'text-white' }; break;
                case 'SJ': theme = { bg: 'bg-sky-600', text: 'text-white' }; break;
                case 'SP': theme = { bg: 'bg-rose-600', text: 'text-white' }; break;
                default: theme = { bg: 'bg-gray-800', text: 'text-white' }; break;
            }
            this.setData({ theme });
        },
        onTap() {
            this.triggerEvent('click', { post: this.properties.post });
        },
        onLongPress() {
            this.triggerEvent('longpress', { index: this.properties.index });
        },
        onImageError(e) {
            // 图片加载失败时的处理：替换为兜底图片
            console.warn('[scattered-ticket] 图片加载失败:', e.detail);
            console.warn('[scattered-ticket] 当前图片 URL:', this.properties.post.imageUrl);
            
            // 使用故宫图片作为兜底
            const fallbackImage = '/image/attractions/gugong.png';
            
            // 更新 post 的 imageUrl
            const updatedPost = {
                ...this.properties.post,
                imageUrl: fallbackImage
            };
            
            this.setData({
                post: updatedPost
            });
            
            console.log('[scattered-ticket] 已替换为兜底图片:', fallbackImage);
        }
    }
})
