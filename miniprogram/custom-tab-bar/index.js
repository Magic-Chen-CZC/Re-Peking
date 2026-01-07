Component({
    data: {
        selected: 1,
        color: "#7A7E83",
        selectedColor: "#4A90E2",
        list: [{
            pagePath: "/pages/plan/index",
            iconPath: "/image/icon_component.png",
            selectedIconPath: "/image/icon_component_HL.png",
            text: "Plan"
        }, {
            pagePath: "/pages/map/index",
            iconPath: "/image/icon_API.png",
            selectedIconPath: "/image/icon_API_HL.png",
            text: "Guide"
        }, {
            pagePath: "/pages/community/index",
            iconPath: "/image/icon_component.png",
            selectedIconPath: "/image/icon_component_HL.png",
            text: "Share"
        }]
    },
    attached() {
    },
    methods: {
        switchTab(e) {
            const data = e.currentTarget.dataset
            const url = data.path
            wx.switchTab({ url })
            this.setData({
                selected: data.index
            })
        }
    }
})
