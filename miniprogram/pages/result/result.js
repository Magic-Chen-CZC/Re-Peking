// 引入高德地图 SDK
var amapFile = require('../../libs/amap-wx.130.js');

Page({
    data: {
        latitude: 39.916527,
        longitude: 116.397128,
        scale: 13,
        markers: [],
        polyline: [],

        attractions: [
            { id: 1, name: '故宫', latitude: 39.916527, longitude: 116.397128, desc: '明清两代的皇家宫殿，世界文化遗产', distance: '100m' },
            { id: 2, name: '景山公园', latitude: 39.927750, longitude: 116.395170, desc: '紫禁城北面的皇家园林，登高远眺的好去处', distance: '250m' },
            { id: 3, name: '北海公园', latitude: 39.926387, longitude: 116.386546, desc: '中国现存最古老的皇家园林之一', distance: '450m' },
            { id: 4, name: '南锣鼓巷', latitude: 39.938350, longitude: 116.402920, desc: '北京最古老的街区之一，胡同文化的代表', distance: '800m' }
        ],

        viewMode: 'mini',
        activeCardIndex: 0,
        selectedAttraction: null,
        touchStartX: 0,
        touchStartY: 0,
        cardStyles: [], // Pre-calculated card styles
        statusBarHeight: 20
    },

    onLoad() {
        const sysInfo = wx.getSystemInfoSync();
        this.setData({
            statusBarHeight: sysInfo.statusBarHeight,
            selectedAttraction: this.data.attractions[0]
        });
        this.initAmapSDK();
        this.drawMarkers();
        this.drawWalkingRoute(this.data.attractions);
        this.updateCardStyles();
    },

    updateCardStyles() {
        const { activeCardIndex, attractions } = this.data;
        const cardStyles = attractions.map((item, index) => {
            const diff = index - activeCardIndex;
            const absDiff = Math.abs(diff);
            return {
                transform: `translateX(${diff * 500}rpx) translateY(${absDiff * 40}rpx) rotate(${diff * 5}deg) scale(${1 - absDiff * 0.1})`,
                opacity: absDiff > 1 ? 0.4 : 1,
                zIndex: 100 - absDiff
            };
        });
        this.setData({ cardStyles });
    },

    initAmapSDK() {
        this.myAmapFun = new amapFile.AMapWX({ key: 'e97b34e523a66789c086668bdeab0371' });
    },

    drawMarkers() {
        const markers = this.data.attractions.map(item => ({
            id: item.id,
            latitude: item.latitude,
            longitude: item.longitude,
            iconPath: '/image/marker.png',
            width: 32,
            height: 32,
            callout: {
                content: item.name,
                color: '#333',
                fontSize: 12,
                borderRadius: 8,
                bgColor: '#FFF8F0',
                padding: 8,
                display: 'ALWAYS'
            }
        }));
        this.setData({ markers });
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

    onMarkerTap(e) {
        const attraction = this.data.attractions.find(item => item.id === e.detail.markerId);
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

    onMiniButtonTap() {
        this.setData({ viewMode: 'browse' });
    },

    onMapTap() {
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
