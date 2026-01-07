import pandas as pd
from pyecharts.charts import Bar, Pie, WordCloud as PyWordCloud, Funnel, Line, Radar
from pyecharts import options as opts
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import platform

# =================交互式输入配置=================
print("=" * 60)
print("🎨 关键词高级图表生成工具")
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
    print(f"\n⚠️  警告：字体文件不存在: {FONT_PATH}")
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
top_10 = df.head(10)
words_30 = top_30['Word'].tolist()
counts_30 = top_30['Count'].tolist()
words_20 = top_20['Word'].tolist()
counts_20 = top_20['Count'].tolist()
words_10 = top_10['Word'].tolist()
counts_10 = top_10['Count'].tolist()

# 选择要生成的图表
print("请选择要生成的图表类型（可多选，用逗号分隔）：")
print("1. 渐变色柱状图（美化版）")
print("2. 环形饼图（Top 20）")
print("3. 南丁格尔玫瑰图（Top 20）")
print("4. 漏斗图（Top 15）")
print("5. 折线图（趋势展示）")
print("6. Pyecharts词云图（交互式）")
print("7. 横向柱状图（Top 20）")
print("8. 艺术词云图（多种配色）")
print("9. 全部生成")
print("=" * 60)

choice = input("请输入选项（如：1,2,3 或 9）: ").strip()
if not choice:
    choice = "9"

choices = [c.strip() for c in choice.split(',')]
generate_all = '9' in choices

# -------------------------------------------------------
# 1. 渐变色柱状图（美化版）
# -------------------------------------------------------
if '1' in choices or generate_all:
    print("\n📊 正在生成渐变色柱状图...")
    bar = (
        Bar(init_opts=opts.InitOpts(
            width="1400px", 
            height="700px",
            theme="macarons"  # 使用马卡龙主题
        ))
        .add_xaxis(words_30)
        .add_yaxis(
            "词频",
            counts_30,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#5470c6",
                color0="#91cc75"
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
    bar.render("图表_1_渐变柱状图.html")
    print("✅ 已生成: 图表_1_渐变柱状图.html")

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
            radius=["40%", "70%"],  # 环形
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
    pie.render("图表_2_环形饼图.html")
    print("✅ 已生成: 图表_2_环形饼图.html")

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
            rosetype="radius",  # 南丁格尔图
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
    rose.render("图表_3_玫瑰图.html")
    print("✅ 已生成: 图表_3_玫瑰图.html")

# -------------------------------------------------------
# 4. 漏斗图
# -------------------------------------------------------
if '4' in choices or generate_all:
    print("\n📐 正在生成漏斗图...")
    top_15 = df.head(15)
    funnel_data = [[top_15['Word'].iloc[i], top_15['Count'].iloc[i]] 
                   for i in range(len(top_15))]
    funnel = (
        Funnel(init_opts=opts.InitOpts(width="1200px", height="800px", theme="shine"))
        .add(
            "词频",
            funnel_data,
            label_opts=opts.LabelOpts(position="inside", formatter="{b}: {c}"),
            itemstyle_opts=opts.ItemStyleOpts(border_color="#fff", border_width=2)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="关键词漏斗图",
                subtitle="Top 15 递减展示",
                title_textstyle_opts=opts.TextStyleOpts(font_size=24)
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    funnel.render("图表_4_漏斗图.html")
    print("✅ 已生成: 图表_4_漏斗图.html")

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
            is_smooth=True,  # 平滑曲线
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3),  # 区域填充
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
    line.render("图表_5_折线趋势图.html")
    print("✅ 已生成: 图表_5_折线趋势图.html")

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
    pywordcloud.render("图表_6_交互词云.html")
    print("✅ 已生成: 图表_6_交互词云.html")

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
                        {"offset": 0, "color": "#667eea"},
                        {"offset": 1, "color": "#764ba2"}
                    ]
                }
            )
        )
        .reversal_axis()  # 横向
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
    bar_horizontal.render("图表_7_横向柱状图.html")
    print("✅ 已生成: 图表_7_横向柱状图.html")

# -------------------------------------------------------
# 8. 艺术词云图（多配色方案）
# -------------------------------------------------------
if '8' in choices or generate_all:
    print("\n🎨 正在生成艺术词云图...")
    freq_dict = dict(zip(df['Word'], df['Count']))
    
    # 配色方案
    colormaps = [
        ('viridis', '经典蓝绿'),
        ('plasma', '等离子紫'),
        ('inferno', '火焰橙'),
        ('Blues', '渐变蓝'),
        ('Reds', '渐变红')
    ]
    
    for idx, (cmap, name) in enumerate(colormaps[:3], 1):  # 生成3个配色
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
        plt.title(f'关键词云图 - {name}', fontsize=20, pad=20)
        plt.tight_layout(pad=0)
        plt.savefig(f"图表_8_词云_{name}.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ 已生成: 图表_8_词云_{name}.png")

print("\n" + "=" * 60)
print("🎉 所有图表生成完成！")
print("=" * 60)
print("\n📁 生成的文件列表：")
print("  HTML交互式图表：可在浏览器中打开，支持缩放、筛选等交互")
print("  PNG图片：高清图片，可直接用于PPT或报告")
print("\n💡 提示：HTML图表可以导出为图片，点击右上角的工具栏即可")
