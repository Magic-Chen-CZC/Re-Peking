Component({
    properties: {
        attraction: Object,
        status: String, // 'visited' | 'planned'
        index: Number,
        isReordering: Boolean,
        isFirst: Boolean,
        isLast: Boolean
    },
    data: {
        isExpanded: false,
        isAddingLog: false,
        newLogText: ''
    },
    methods: {
        /**
         * 空方法，用于阻止事件冒泡
         * 用于 catchtap="noop" 的场景（如输入框区域，防止点击触发外层事件）
         */
        noop() {
            // 什么都不做，仅用于阻止事件冒泡
        },

        handleCardClick() {
            if (this.data.status === 'visited') {
                this.setData({
                    isExpanded: !this.data.isExpanded
                });
            }
        },
        onInputLog(e) {
            this.setData({
                newLogText: e.detail.value
            });
        },
        startAddLog() {
            this.setData({
                isAddingLog: true
            });
        },
        submitLog() {
            if (this.data.newLogText.trim()) {
                this.triggerEvent('addLog', {
                    id: this.data.attraction.id,
                    text: this.data.newLogText
                });
                this.setData({
                    newLogText: '',
                    isAddingLog: false
                });
            }
        },
        cancelAddLog() {
            if (!this.data.newLogText) {
                this.setData({
                    isAddingLog: false
                });
            }
        },
        onDelete(e) {
            this.triggerEvent('delete', { id: this.data.attraction.id });
        },
        onMoveUp(e) {
            this.triggerEvent('moveUp', { index: this.data.index });
        },
        onMoveDown(e) {
            this.triggerEvent('moveDown', { index: this.data.index });
        }
    }
})
