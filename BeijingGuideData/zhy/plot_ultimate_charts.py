import pandas as pd
from pyecharts.charts import Bar, Pie, WordCloud as PyWordCloud, Funnel, Line, Radar, Gauge, Liquid, Page
from pyecharts import options as opts
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import platform
from datetime import datetime

# =================交互式输入配置=================
print("=" * 60)
print("🎨 关键词终极图表生成工具 Ultimate Edition")
print("=" * 60)

# 获取用户输入的数据文件名
default_data = "word_frequency.csv"
data_file_input = input(f"请输入词频统计文件名 (直接回车使用默认: {default_data}): ").strip()
DATA_FILE = data_file_input if data_file_input else default_data

# 检查文件是否存在
if not os.path.exists(DATA_FILE):
    print(f"\n❌ 错误：找不到文件 '{DATA_FILE}'")
    print("请先运行 word_frequency.py 生成词频统计文件！")
    exit(1)

# 创建输出文件夹
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"图表输出_{timestamp}"
os.makedirs(output_dir, exist_ok=True)
print(f"\n📁 输出目录: {output_dir}/")

# 自动检测操作系统并设置字体路径
system = platform.system()
if system == "Darwin":  # macOS
    possible_fonts = [
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    FONT_PATH = None
    for font in possible_fonts:
        if os.path.exists(font):
            FONT_PATH = font
            break
    if not FONT_PATH:
        FONT_PATH = "/System/Library/Fonts/STHeiti Light.ttc"
elif system == "Windows":
    FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
else:  # Linux
    FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

# 检查字体文件是否存在
if not os.path.exists(FONT_PATH):
    print(f"\n⚠️  警告：字体文件不存在")
    FONT_PATH = None

print(f"\n正在读取统计数据: {DATA_FILE} ...")
try:
    df = pd.read_csv(DATA_FILE)
    print(f"✅ 成功读取 {len(df)} 条词频数据\n")
except FileNotFoundError:
    print(f"❌ 错误：没找到 {DATA_FILE}，请先运行 word_frequency.py！")
    exit(1)

# 准备数据
top_30 = df.head(30)
top_20 = df.head(20)
top_15 = df.head(15)
top_10 = df.head(10)
words_30 = top_30['Word'].tolist()
counts_30 = top_30['Count'].tolist()
words_20 = top_20['Word'].tolist()
counts_20 = top_20['Count'].tolist()
words_15 = top_15['Word'].tolist()
counts_15 = top_15['Count'].tolist()
words_10 = top_10['Word'].tolist()
counts_10 = top_10['Count'].tolist()

# 选择要生成的图表
print("请选择要生成的图表类型（可多选，用逗号分隔）：")
print("1. 渐变色柱状图（美化版）")
print("2. 环形饼图（Top 20）")
print("3. 南丁格尔玫瑰图（Top 20）")
print("4. 漏斗图（Top 15）✨修复版")
print("5. 折线图（趋势展示）")
print("6. Pyecharts词云图（交互式）")
print("7. 横向柱状图（Top 20）")
print("8. 艺术词云图（多种配色）")
print("9. 🔥 3D柱状图（超炫酷）")
print("10. 🔥 动态水球图（覆盖率展示）")
print("11. 🔥 仪表盘（热度指数）")
print("12. 🔥 雷达图（多维分析）")
print("13. 🔥 组合页面（Dashboard）")
print("0. 全部生成")
print("=" * 60)

choice = input("请输入选项（如：1,2,3 或 0 全部生成）: ").strip()
if not choice:
    choice = "0"

choices = [c.strip() for c in choice.split(',')]
generate_all = '0' in choices

# -------------------------------------------------------
# 1. 渐变色柱状图（美化版）
# -------------------------------------------------------
if '1' in choices or generate_all:
    print("\n📊 正在生成渐变色柱状图...")
    bar = (
        Bar(init_opts=opts.InitOpts(
            width="1400px", 
            height="700px",
            theme="macarons"
        ))
        .add_xaxis(words_30)
        .add_yaxis(
            "词频",
            counts_30,
            itemstyle_opts=opts.ItemStyleOpts(
                color={
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "#667eea"},
                        {"offset": 1, "color": "#764ba2"}
                    ]
                }
            ),
            label_opts=opts.LabelOpts(is_show=True, position="top")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="关键词词频统计",
                subtitle="Top 30 高频词汇分析",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=24,
                    color="#2c3e50"
                )
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45, font_size=12)
            ),
            yaxis_opts=opts.AxisOpts(
                name="出现次数",
                name_textstyle_opts=opts.TextStyleOpts(font_size=14)
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ],
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                feature=opts.ToolBoxFeatureOpts(
                    save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(title="保存为图片"),
                    data_view=opts.ToolBoxFeatureDataViewOpts(title="数据视图"),
                )
            )
        )
    )
    bar.render(f"{output_dir}/图表_1_渐变柱状图.html")
    print(f"✅ 已生成: {output_dir}/图表_1_渐变柱状图.html")

# -------------------------------------------------------
# 2. 环形饼图
# -------------------------------------------------------
if '2' in choices or generate_all:
    print("\n🍩 正在生成环形饼图...")
    pie_data = [[words_20[i], counts_20[i]] for i in range(len(words_20))]
    pie = (
        Pie(init_opts=opts.InitOpts(
            width="1200px",
            height="800px",
            theme="westeros"
        ))
        .add(
            "",
            pie_data,
            radius=["40%", "70%"],
            label_opts=opts.LabelOpts(
                formatter="{b}: {c} ({d}%)",
                font_size=12
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                border_color="#fff",
                border_width=2
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="关键词分布环形图",
                subtitle="Top 20 词频占比",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24)
            ),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_left="left",
                pos_top="15%"
            )
        )
        .set_series_opts(
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{b}: {c} ({d}%)"
            )
        )
    )
    pie.render(f"{output_dir}/图表_2_环形饼图.html")
    print(f"✅ 已生成: {output_dir}/图表_2_环形饼图.html")

# -------------------------------------------------------
# 3. 南丁格尔玫瑰图
# -------------------------------------------------------
if '3' in choices or generate_all:
    print("\n🌹 正在生成南丁格尔玫瑰图...")
    rose_data = [[words_20[i], counts_20[i]] for i in range(len(words_20))]
    rose = (
        Pie(init_opts=opts.InitOpts(
            width="1200px",
            height="800px",
            theme="romantic"
        ))
        .add(
            "",
            rose_data,
            radius=["30%", "75%"],
            center=["50%", "50%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(
                formatter="{b}\n{c}次",
                font_size=11
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="关键词南丁格尔玫瑰图",
                subtitle="用半径表示数值大小",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24, color="#d14a61")
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    rose.render(f"{output_dir}/图表_3_玫瑰图.html")
    print(f"✅ 已生成: {output_dir}/图表_3_玫瑰图.html")

# -------------------------------------------------------
# 4. 漏斗图（修复版）
# -------------------------------------------------------
if '4' in choices or generate_all:
    print("\n📐 正在生成漏斗图...")
    # 修复：反转数据，让最大值在顶部
    funnel_data = [[words_15[i], counts_15[i]] for i in range(len(words_15))]
    funnel = (
        Funnel(init_opts=opts.InitOpts(
            width="1200px",
            height="900px",
            theme="shine"
        ))
        .add(
            "词频",
            funnel_data,
            sort_="descending",  # 降序排列
            label_opts=opts.LabelOpts(
                position="inside",
                formatter="{b}: {c}",
                font_size=11
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                border_color="#fff",
                border_width=2
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="关键词漏斗图",
                subtitle="Top 15 热度递减展示",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24)
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{b}: {c}"
            )
        )
    )
    funnel.render(f"{output_dir}/图表_4_漏斗图.html")
    print(f"✅ 已生成: {output_dir}/图表_4_漏斗图.html")

# -------------------------------------------------------
# 5. 折线图（趋势）
# -------------------------------------------------------
if '5' in choices or generate_all:
    print("\n📈 正在生成折线趋势图...")
    line = (
        Line(init_opts=opts.InitOpts(
            width="1400px",
            height="700px",
            theme="vintage"
        ))
        .add_xaxis(words_30)
        .add_yaxis(
            "词频",
            counts_30,
            is_smooth=True,
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
            label_opts=opts.LabelOpts(is_show=False),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                ]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均值")]
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="关键词频次趋势图",
                subtitle="Top 30 变化趋势",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24)
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45)
            ),
            yaxis_opts=opts.AxisOpts(name="出现次数"),
            datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100)],
        )
    )
    line.render(f"{output_dir}/图表_5_折线趋势图.html")
    print(f"✅ 已生成: {output_dir}/图表_5_折线趋势图.html")

# -------------------------------------------------------
# 6. Pyecharts 交互式词云
# -------------------------------------------------------
if '6' in choices or generate_all:
    print("\n☁️  正在生成Pyecharts词云图...")
    wordcloud_data = [[words_30[i], str(counts_30[i])] for i in range(len(words_30))]
    pywordcloud = (
        PyWordCloud(init_opts=opts.InitOpts(width="1400px", height="800px"))
        .add(
            "",
            wordcloud_data,
            word_size_range=[20, 100],
            shape="circle",
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="关键词云图",
                subtitle="交互式词云展示",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True)
        )
    )
    pywordcloud.render(f"{output_dir}/图表_6_交互词云.html")
    print(f"✅ 已生成: {output_dir}/图表_6_交互词云.html")

# -------------------------------------------------------
# 7. 横向柱状图
# -------------------------------------------------------
if '7' in choices or generate_all:
    print("\n📊 正在生成横向柱状图...")
    bar_horizontal = (
        Bar(init_opts=opts.InitOpts(
            width="1200px",
            height="900px",
            theme="purple-passion"
        ))
        .add_xaxis(words_20)
        .add_yaxis(
            "词频",
            counts_20,
            label_opts=opts.LabelOpts(is_show=True, position="right"),
            itemstyle_opts=opts.ItemStyleOpts(
                color={
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 1, "y2": 0,
                    "colorStops": [
                        {"offset": 0, "color": "#f093fb"},
                        {"offset": 1, "color": "#f5576c"}
                    ]
                }
            )
        )
        .reversal_axis()
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="关键词频次排行榜",
                subtitle="Top 20 横向展示",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24)
            ),
            xaxis_opts=opts.AxisOpts(name="出现次数"),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12)),
        )
    )
    bar_horizontal.render(f"{output_dir}/图表_7_横向柱状图.html")
    print(f"✅ 已生成: {output_dir}/图表_7_横向柱状图.html")

# -------------------------------------------------------
# 8. 艺术词云图（多配色方案）
# -------------------------------------------------------
if '8' in choices or generate_all:
    print("\n🎨 正在生成艺术词云图...")
    freq_dict = dict(zip(df['Word'], df['Count']))
    
    colormaps = [
        ('viridis', '经典蓝绿'),
        ('plasma', '等离子紫'),
        ('inferno', '火焰橙'),
    ]
    
    for idx, (cmap, name) in enumerate(colormaps, 1):
        if FONT_PATH and os.path.exists(FONT_PATH):
            wc = WordCloud(
                font_path=FONT_PATH,
                width=1920,
                height=1080,
                background_color='white',
                max_words=150,
                colormap=cmap,
                relative_scaling=0.5,
                min_font_size=10
            ).generate_from_frequencies(freq_dict)
        else:
            wc = WordCloud(
                width=1920,
                height=1080,
                background_color='white',
                max_words=150,
                colormap=cmap,
                relative_scaling=0.5,
                min_font_size=10
            ).generate_from_frequencies(freq_dict)
        
        plt.figure(figsize=(19.2, 10.8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(f"{output_dir}/图表_8_词云_{name}.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ 已生成: {output_dir}/图表_8_词云_{name}.png")

# -------------------------------------------------------
# 9. 🔥 3D柱状图（超炫酷）
# -------------------------------------------------------
if '9' in choices or generate_all:
    print("\n🔥 正在生成3D柱状图...")
    bar_3d = (
        Bar(init_opts=opts.InitOpts(
            width="1400px",
            height="800px",
            theme="dark"
        ))
        .add_xaxis(words_20)
        .add_yaxis(
            "词频",
            counts_20,
            itemstyle_opts=opts.ItemStyleOpts(
                color={
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "#00d2ff"},
                        {"offset": 1, "color": "#3a7bd5"}
                    ]
                },
                border_radius=[10, 10, 0, 0]  # 圆角效果
            ),
            label_opts=opts.LabelOpts(
                is_show=True,
                position="top",
                formatter="{c}",
                font_size=12
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="🔥 关键词3D效果柱状图",
                subtitle="炫酷深色主题",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=28,
                    color="#00d2ff"
                )
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45, font_size=12, color="#fff")
            ),
            yaxis_opts=opts.AxisOpts(
                name="热度指数",
                name_textstyle_opts=opts.TextStyleOpts(font_size=14, color="#fff")
            ),
            toolbox_opts=opts.ToolboxOpts(is_show=True)
        )
    )
    bar_3d.render(f"{output_dir}/图表_9_3D柱状图.html")
    print(f"✅ 已生成: {output_dir}/图表_9_3D柱状图.html")

# -------------------------------------------------------
# 10. 🔥 动态水球图（覆盖率展示）
# -------------------------------------------------------
if '10' in choices or generate_all:
    print("\n🔥 正在生成动态水球图...")
    # 计算Top词的覆盖率
    total_count = df['Count'].sum()
    top_10_sum = sum(counts_10)
    coverage_rate = round(top_10_sum / total_count * 100, 2)
    
    liquid = (
        Liquid(init_opts=opts.InitOpts(width="800px", height="800px", theme="shine"))
        .add(
            "覆盖率",
            [coverage_rate / 100],
            is_outline_show=True,
            shape="circle",
            label_opts=opts.LabelOpts(
                font_size=50,
                formatter=f"Top10覆盖率\n{coverage_rate}%",
                position="inside"
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="🔥 Top10关键词覆盖率",
                subtitle=f"前10个词占总词频的 {coverage_rate}%",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24)
            )
        )
    )
    liquid.render(f"{output_dir}/图表_10_水球图.html")
    print(f"✅ 已生成: {output_dir}/图表_10_水球图.html")

# -------------------------------------------------------
# 11. 🔥 仪表盘（热度指数）
# -------------------------------------------------------
if '11' in choices or generate_all:
    print("\n🔥 正在生成仪表盘...")
    # 计算热度指数（最高词频的相对值）
    max_count = counts_30[0]
    heat_index = min(100, int((max_count / df['Count'].mean()) * 10))
    
    gauge = (
        Gauge(init_opts=opts.InitOpts(width="800px", height="600px", theme="romantic"))
        .add(
            "热度指数",
            [("最热关键词", heat_index)],
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color=[[0.3, "#67e0e3"], [0.7, "#37a2da"], [1, "#fd666d"]],
                    width=30
                )
            ),
            detail_label_opts=opts.LabelOpts(
                formatter="{value}",
                font_size=40
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"🔥 关键词热度仪表盘",
                subtitle=f"最热词: {words_30[0]} (出现{max_count}次)",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24)
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    gauge.render(f"{output_dir}/图表_11_仪表盘.html")
    print(f"✅ 已生成: {output_dir}/图表_11_仪表盘.html")

# -------------------------------------------------------
# 12. 🔥 雷达图（多维分析）
# -------------------------------------------------------
if '12' in choices or generate_all:
    print("\n🔥 正在生成雷达图...")
    # 取前8个词做雷达图
    radar_words = words_10[:8]
    radar_counts = counts_10[:8]
    
    # 归一化到100分制
    max_val = max(radar_counts)
    radar_scores = [round(c / max_val * 100, 1) for c in radar_counts]
    
    radar = (
        Radar(init_opts=opts.InitOpts(width="1000px", height="800px", theme="westeros"))
        .add_schema(
            schema=[
                opts.RadarIndicatorItem(name=radar_words[i], max_=100)
                for i in range(len(radar_words))
            ],
            splitarea_opt=opts.SplitAreaOpts(
                is_show=True,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.2)
            ),
        )
        .add(
            "关键词热度",
            [radar_scores],
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=True)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="🔥 关键词多维雷达图",
                subtitle="Top8 热度分析（满分100）",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24)
            )
        )
    )
    radar.render(f"{output_dir}/图表_12_雷达图.html")
    print(f"✅ 已生成: {output_dir}/图表_12_雷达图.html")

# -------------------------------------------------------
# 13. 🔥 组合页面（Dashboard）
# -------------------------------------------------------
if '13' in choices or generate_all:
    print("\n🔥 正在生成Dashboard组合页面...")
    
    # 创建一个Page对象，将多个图表组合在一起
    page = Page(layout=Page.SimplePageLayout)
    
    # 添加多个图表
    # 仪表盘
    gauge_dash = (
        Gauge(init_opts=opts.InitOpts(width="600px", height="400px"))
        .add("", [("热度", min(100, int((counts_30[0] / df['Count'].mean()) * 10)))])
        .set_global_opts(title_opts=opts.TitleOpts(title="热度指数"))
    )
    
    # 饼图
    pie_dash = (
        Pie(init_opts=opts.InitOpts(width="600px", height="400px"))
        .add("", [[words_10[i], counts_10[i]] for i in range(len(words_10))], radius=["30%", "55%"])
        .set_global_opts(title_opts=opts.TitleOpts(title="Top10分布"))
    )
    
    # 柱状图
    bar_dash = (
        Bar(init_opts=opts.InitOpts(width="1200px", height="400px"))
        .add_xaxis(words_20)
        .add_yaxis("词频", counts_20)
        .set_global_opts(title_opts=opts.TitleOpts(title="Top20排行"))
    )
    
    # 折线图
    line_dash = (
        Line(init_opts=opts.InitOpts(width="1200px", height="400px"))
        .add_xaxis(words_20)
        .add_yaxis("趋势", counts_20, is_smooth=True)
        .set_global_opts(title_opts=opts.TitleOpts(title="频次趋势"))
    )
    
    page.add(gauge_dash, pie_dash, bar_dash, line_dash)
    page.render(f"{output_dir}/图表_13_Dashboard.html")
    print(f"✅ 已生成: {output_dir}/图表_13_Dashboard.html")

print("\n" + "=" * 60)
print("🎉 所有图表生成完成！")
print("=" * 60)
print(f"\n📁 所有文件已保存到: {output_dir}/")
print("\n📊 生成的图表类型：")
print("  ✅ 交互式HTML图表 - 可在浏览器中打开，支持缩放、筛选")
print("  ✅ 高清PNG图片 - 可直接用于PPT或报告")
print("  ✅ Dashboard组合页面 - 一页展示多个图表")
print("\n💡 提示：")
print("  - HTML图表可以导出为图片（点击右上角工具栏）")
print("  - 所有图表按时间戳分类存放，不会混乱")
print("  - 推荐用Chrome或Edge浏览器打开HTML文件")
