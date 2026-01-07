Component({
    properties: {
        index: {
            type: Number,
            value: 0
        },
        type: {
            type: String,
            value: 'planned' // 'visited' | 'planned'
        }
    },
    data: {
        bgClass: '',
        shape: '',
        fgColor: '',
        numColor: ''
    },
    observers: {
        'index, type': function (index, type) {
            this.updateGraphics(index, type);
        }
    },
    methods: {
        updateGraphics(index, type) {
            const bgColors = ['bg-dark-1', 'bg-dark-2', 'bg-dark-3', 'bg-black'];
            const shapes = ['circle', 'triangle', 'grid', 'arch'];

            const bgClass = type === 'visited' ? bgColors[index % bgColors.length] : 'bg-light';
            const shape = shapes[index % shapes.length];
            const fgColor = type === 'visited' ? 'stroke-white-20' : 'stroke-gray-300';
            const numColor = type === 'visited' ? 'text-white-10' : 'text-gray-200';

            this.setData({
                bgClass,
                shape,
                fgColor,
                numColor
            });
        }
    }
})
