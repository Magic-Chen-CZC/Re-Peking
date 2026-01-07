Page({
    data: {
        selectedMbti: null,
        bubbles: [
            {
                id: 'INTJ',
                color: 'blue',
                codes: ['INTJ', 'ISTJ', 'ISFJ'],
                desc: '可靠、高效、有计划且符合预期的旅行'
            },
            {
                id: 'ESFP',
                color: 'yellow',
                codes: ['ESFP', 'ESTP', 'ENFP'],
                desc: '充满乐趣、随心所欲、可以亲身参与的旅行'
            },
            {
                id: 'INFJ',
                color: 'green',
                codes: ['INFJ', 'INFP', 'ENFJ', 'ENFP'],
                desc: '满足精神需求、注重内心体验的旅行方式'
            },
            {
                id: 'ENTP',
                color: 'purple',
                codes: ['INTP', 'ENTJ', 'ENTP'],
                desc: '在旅行中理解事物背后的原理和逻辑'
            }
        ]
    },

    onLoad() {
        const savedMbti = wx.getStorageSync('user_mbti');
        if (savedMbti) {
            this.setData({ selectedMbti: savedMbti });
        }
    },

    onSelectMbti(e) {
        const mbti = e.currentTarget.dataset.mbti;

        this.setData({
            selectedMbti: mbti
        });

        // Save to local storage
        wx.setStorageSync('user_mbti', mbti);

        // Visual feedback delay before navigation
        setTimeout(() => {
            this.navigateToNext();
        }, 300);
    },

    onSkip() {
        // Clear or set null
        wx.setStorageSync('user_mbti', null);
        this.navigateToNext();
    },

    navigateToNext() {
        wx.navigateTo({
            url: '/pages/interests/interests',
            fail: (err) => {
                console.error('Navigation failed (target page might not exist yet):', err);
                wx.showToast({
                    title: '即将前往兴趣页',
                    icon: 'none'
                });
            }
        });
    }
});
