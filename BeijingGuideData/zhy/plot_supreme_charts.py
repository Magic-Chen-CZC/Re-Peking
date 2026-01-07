import pandas as pd
from pyecharts.charts import Bar, Pie, WordCloud as PyWordCloud, Funnel, Line, Radar, Gauge, Liquid, Page, Sunburst, TreeMap
from pyecharts import options as opts
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import os
import platform
from datetime import datetime
import numpy as np

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("🎨 关键词至尊图表生成工具 Supreme Edition")
print("🚀 包含24种图表类型 | 自动文件夹管理 | 超炫酷可视化")
print("=" * 70)

# 获取用户输入
default_data = "word_frequency.csv"
data_file_input = input(f"\n请输入词频统计文件名 (直接回车使用默认: {default_data}): ").strip()
DATA_FILE = data_file_input if data_file_input else default_data

if not os.path.exists(DATA_FILE):
    print(f"\n❌ 错误：找不到文件 '{DATA_FILE}'")
    print("请先运行 word_frequency.py 生成词频统计文件！")
    exit(1)

# 创建输出文件夹
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"图表输出_{timestamp}"
os.makedirs(output_dir, exist_ok=True)
print(f"\n📁 输出目录: {output_dir}/")

# 检测字体
system = platform.system()
FONT_PATH = None
if system == "Darwin":
    fonts = ["/System/Library/Fonts/STHeiti Light.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]
    for font in fonts:
        if os.path.exists(font):
            FONT_PATH = font
            break
elif system == "Windows":
    FONT_PATH = "C:/Windows/Fonts/simhei.ttf"

print(f"\n正在读取统计数据: {DATA_FILE} ...")
try:
    df = pd.read_csv(DATA_FILE)
    print(f"✅ 成功读取 {len(df)} 条词频数据\n")
except Exception as e:
    print(f"❌ 错误：{e}")
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

# 选择菜单
print("请选择要生成的图表类型（可多选，用逗号分隔）：")
print("\n📊 基础图表系列 (1-6)：")
print("1. 渐变柱状图  2. 环形饼图  3. 南丁格尔玫瑰图")
print("4. 漏斗图  5. 折线图  6. 横向柱状图")
print("\n🔥 炫酷特效系列 (7-10)：")
print("7. 3D柱状图  8. 动态水球图  9. 仪表盘  10. 雷达图")
print("\n☁️  词云系列 (11-12)：")
print("11. 交互词云  12. 艺术词云PNG")
print("\n🎯 高级分析系列 (13-18)：")
print("13. 树状图  14. 旭日图  15. 热力图")
print("16. 箱线图  17. 小提琴图  18. 帕累托图")
print("\n🌈 Plotly交互系列 (19-22)：")
print("19. 3D气泡图  20. 极坐标图  21. 瀑布图  22. 桑基图")
print("\n📈 组合展示 (23-24)：")
print("23. Dashboard  24. 统计报告")
print("\n💫 快捷选项：")
print("99. ⭐ 精选套餐（10个最美图表）")
print("0.  🎨 全部生成（24种）")
print("=" * 70)

choice = input("\n请输入选项（如：1,2,3 或 0 或 99）: ").strip()
if not choice:
    choice = "99"

choices = [c.strip() for c in choice.split(',')]
generate_all = '0' in choices
generate_selected = '99' in choices

if generate_selected:
    choices.extend(['1', '3', '7', '8', '9', '11', '13', '19', '20', '23'])

# 计算通用数据
total_count = df['Count'].sum()
top_10_sum = sum(counts_10)
coverage_rate = round(top_10_sum / total_count * 100, 2)
max_count = counts_30[0]
heat_index = min(100, int((max_count / df['Count'].mean()) * 10))

print("\n🚀 开始生成图表...\n")

# [1] 渐变柱状图
if '1' in choices or generate_all:
    print("📊 [1] 渐变柱状图...")
    bar = (
        Bar(init_opts=opts.InitOpts(width="1400px", height="700px", theme="macarons"))
        .add_xaxis(words_30)
        .add_yaxis("词频", counts_30,
            itemstyle_opts=opts.ItemStyleOpts(
                color={"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                       "colorStops": [{"offset": 0, "color": "#667eea"}, {"offset": 1, "color": "#764ba2"}]}),
            label_opts=opts.LabelOpts(is_show=True, position="top"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="关键词词频统计", subtitle="Top 30"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            datazoom_opts=[opts.DataZoomOpts()],
            toolbox_opts=opts.ToolboxOpts(is_show=True))
    )
    bar.render(f"{output_dir}/01_渐变柱状图.html")
    print("   ✅ 01_渐变柱状图.html")

# [2] 环形饼图
if '2' in choices or generate_all:
    print("🍩 [2] 环形饼图...")
    pie = (
        Pie(init_opts=opts.InitOpts(width="1200px", height="800px", theme="westeros"))
        .add("", [[words_20[i], counts_20[i]] for i in range(len(words_20))], radius=["40%", "70%"])
        .set_global_opts(title_opts=opts.TitleOpts(title="关键词分布环形图"))
    )
    pie.render(f"{output_dir}/02_环形饼图.html")
    print("   ✅ 02_环形饼图.html")

# [3] 南丁格尔玫瑰图
if '3' in choices or generate_all:
    print("🌹 [3] 南丁格尔玫瑰图...")
    rose = (
        Pie(init_opts=opts.InitOpts(width="1200px", height="800px", theme="romantic"))
        .add("", [[words_20[i], counts_20[i]] for i in range(len(words_20))],
             radius=["30%", "75%"], rosetype="radius")
        .set_global_opts(title_opts=opts.TitleOpts(title="南丁格尔玫瑰图"))
    )
    rose.render(f"{output_dir}/03_玫瑰图.html")
    print("   ✅ 03_玫瑰图.html")

# [4] 漏斗图
if '4' in choices or generate_all:
    print("📐 [4] 漏斗图...")
    funnel = (
        Funnel(init_opts=opts.InitOpts(width="1200px", height="900px", theme="shine"))
        .add("词频", [[words_15[i], counts_15[i]] for i in range(len(words_15))], sort_="descending")
        .set_global_opts(title_opts=opts.TitleOpts(title="关键词漏斗图"))
    )
    funnel.render(f"{output_dir}/04_漏斗图.html")
    print("   ✅ 04_漏斗图.html")

# [5] 折线图
if '5' in choices or generate_all:
    print("📈 [5] 折线图...")
    line = (
        Line(init_opts=opts.InitOpts(width="1400px", height="700px", theme="vintage"))
        .add_xaxis(words_30)
        .add_yaxis("词频", counts_30, is_smooth=True, areastyle_opts=opts.AreaStyleOpts(opacity=0.3))
        .set_global_opts(title_opts=opts.TitleOpts(title="关键词趋势图"))
    )
    line.render(f"{output_dir}/05_折线图.html")
    print("   ✅ 05_折线图.html")

# [6] 横向柱状图
if '6' in choices or generate_all:
    print("📊 [6] 横向柱状图...")
    bar_h = (
        Bar(init_opts=opts.InitOpts(width="1200px", height="900px", theme="purple-passion"))
        .add_xaxis(words_20)
        .add_yaxis("词频", counts_20)
        .reversal_axis()
        .set_global_opts(title_opts=opts.TitleOpts(title="关键词排行榜"))
    )
    bar_h.render(f"{output_dir}/06_横向柱状图.html")
    print("   ✅ 06_横向柱状图.html")

# [7] 3D柱状图
if '7' in choices or generate_all:
    print("🔥 [7] 3D柱状图...")
    bar_3d = (
        Bar(init_opts=opts.InitOpts(width="1400px", height="800px", theme="dark"))
        .add_xaxis(words_20)
        .add_yaxis("词频", counts_20,
            itemstyle_opts=opts.ItemStyleOpts(
                color={"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                       "colorStops": [{"offset": 0, "color": "#00d2ff"}, {"offset": 1, "color": "#3a7bd5"}]},
                border_radius=[10, 10, 0, 0]))
        .set_global_opts(title_opts=opts.TitleOpts(title="🔥 3D柱状图"))
    )
    bar_3d.render(f"{output_dir}/07_3D柱状图.html")
    print("   ✅ 07_3D柱状图.html")

# [8] 水球图
if '8' in choices or generate_all:
    print("🔥 [8] 水球图...")
    liquid = (
        Liquid(init_opts=opts.InitOpts(width="800px", height="800px", theme="shine"))
        .add("覆盖率", [coverage_rate / 100])
        .set_global_opts(title_opts=opts.TitleOpts(title=f"Top10覆盖率 {coverage_rate}%"))
    )
    liquid.render(f"{output_dir}/08_水球图.html")
    print("   ✅ 08_水球图.html")

# [9] 仪表盘
if '9' in choices or generate_all:
    print("🔥 [9] 仪表盘...")
    gauge = (
        Gauge(init_opts=opts.InitOpts(width="800px", height="600px", theme="romantic"))
        .add("热度", [("", heat_index)])
        .set_global_opts(title_opts=opts.TitleOpts(title=f"热度指数: {words_30[0]}"))
    )
    gauge.render(f"{output_dir}/09_仪表盘.html")
    print("   ✅ 09_仪表盘.html")

# [10] 雷达图
if '10' in choices or generate_all:
    print("🔥 [10] 雷达图...")
    radar_words = words_10[:8]
    radar_counts = counts_10[:8]
    max_val = max(radar_counts)
    radar_scores = [round(c / max_val * 100, 1) for c in radar_counts]
    radar = (
        Radar(init_opts=opts.InitOpts(width="1000px", height="800px", theme="westeros"))
        .add_schema(schema=[opts.RadarIndicatorItem(name=radar_words[i], max_=100) for i in range(len(radar_words))])
        .add("热度", [radar_scores])
        .set_global_opts(title_opts=opts.TitleOpts(title="关键词雷达图"))
    )
    radar.render(f"{output_dir}/10_雷达图.html")
    print("   ✅ 10_雷达图.html")

# [11] 交互词云
if '11' in choices or generate_all:
    print("☁️  [11] 交互词云...")
    pywordcloud = (
        PyWordCloud(init_opts=opts.InitOpts(width="1400px", height="800px"))
        .add("", [[words_30[i], str(counts_30[i])] for i in range(len(words_30))], word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="交互式词云"))
    )
    pywordcloud.render(f"{output_dir}/11_交互词云.html")
    print("   ✅ 11_交互词云.html")

# [12] 艺术词云
if '12' in choices or generate_all:
    print("🎨 [12] 艺术词云...")
    freq_dict = dict(zip(df['Word'], df['Count']))
    colormaps = [('viridis', '蓝绿'), ('plasma', '紫色'), ('inferno', '橙红')]
    for cmap, name in colormaps:
        if FONT_PATH:
            wc = WordCloud(font_path=FONT_PATH, width=1920, height=1080, background_color='white',
                          max_words=150, colormap=cmap).generate_from_frequencies(freq_dict)
        else:
            wc = WordCloud(width=1920, height=1080, background_color='white',
                          max_words=150, colormap=cmap).generate_from_frequencies(freq_dict)
        plt.figure(figsize=(19.2, 10.8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(f"{output_dir}/12_词云_{name}.png", dpi=150, bbox_inches='tight')
        plt.close()
    print("   ✅ 12_词云_*.png (3张)")

# [13] 树状图
if '13' in choices or generate_all:
    print("🎯 [13] 树状图...")
    treemap = (
        TreeMap(init_opts=opts.InitOpts(width="1200px", height="800px", theme="wonderland"))
        .add("关键词", [{"value": counts_15[i], "name": words_15[i]} for i in range(len(words_15))], leaf_depth=1)
        .set_global_opts(title_opts=opts.TitleOpts(title="关键词树状图"))
    )
    treemap.render(f"{output_dir}/13_树状图.html")
    print("   ✅ 13_树状图.html")

# [14] 旭日图
if '14' in choices or generate_all:
    print("🎯 [14] 旭日图...")
    sunburst_data = [
        {"name": "高频词", "children": [{"name": words_10[i], "value": counts_10[i]} for i in range(5)]},
        {"name": "中频词", "children": [{"name": words_10[i], "value": counts_10[i]} for i in range(5, 10)]}
    ]
    sunburst = (
        Sunburst(init_opts=opts.InitOpts(width="1000px", height="800px", theme="romantic"))
        .add("", data_pair=sunburst_data, radius=[0, "90%"])
        .set_global_opts(title_opts=opts.TitleOpts(title="关键词旭日图"))
    )
    sunburst.render(f"{output_dir}/14_旭日图.html")
    print("   ✅ 14_旭日图.html")

# [15] 热力图
if '15' in choices or generate_all:
    print("🎯 [15] 热力图...")
    matrix_data = np.array(counts_10[:10]).reshape(-1, 1)
    plt.figure(figsize=(12, 8))
    sns.heatmap(matrix_data.T, annot=True, fmt='d', cmap='YlOrRd',
                xticklabels=words_10[:10], yticklabels=['词频'])
    plt.title('关键词热力图', fontsize=16)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/15_热力图.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✅ 15_热力图.png")

# [16] 箱线图
if '16' in choices or generate_all:
    print("🎯 [16] 箱线图...")
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df['Count'], color='skyblue')
    plt.title('词频分布箱线图', fontsize=16)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/16_箱线图.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✅ 16_箱线图.png")

# [17] 小提琴图
if '17' in choices or generate_all:
    print("🎯 [17] 小提琴图...")
    plt.figure(figsize=(12, 6))
    sns.violinplot(data=df['Count'], color='lightcoral')
    plt.title('词频密度分布图', fontsize=16)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/17_小提琴图.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✅ 17_小提琴图.png")

# [18] 帕累托图
if '18' in choices or generate_all:
    print("🎯 [18] 帕累托图...")
    cumsum = np.cumsum(counts_20)
    cumsum_pct = cumsum / cumsum[-1] * 100
    fig, ax1 = plt.subplots(figsize=(14, 7))
    ax1.bar(range(len(words_20)), counts_20, color='steelblue', alpha=0.7)
    ax1.set_xlabel('关键词', fontsize=12)
    ax1.set_ylabel('词频', fontsize=12)
    plt.xticks(range(len(words_20)), words_20, rotation=45, ha='right')
    ax2 = ax1.twinx()
    ax2.plot(range(len(words_20)), cumsum_pct, color='red', marker='o', linewidth=2)
    ax2.set_ylabel('累计占比 (%)', fontsize=12, color='red')
    ax2.axhline(y=80, color='gray', linestyle='--', alpha=0.5)
    plt.title('帕累托图 - 二八定律', fontsize=16)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/18_帕累托图.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✅ 18_帕累托图.png")

# [19] 3D气泡图
if '19' in choices or generate_all:
    print("🌈 [19] 3D气泡图...")
    fig = go.Figure(data=[go.Scatter3d(
        x=list(range(len(words_20))), y=counts_20, z=[i * 2 for i in counts_20],
        mode='markers',
        marker=dict(size=counts_20, color=counts_20, colorscale='Viridis', showscale=True),
        text=words_20
    )])
    fig.update_layout(title='关键词3D气泡图', width=1200, height=800)
    fig.write_html(f"{output_dir}/19_3D气泡图.html")
    print("   ✅ 19_3D气泡图.html")

# [20] 极坐标图
if '20' in choices or generate_all:
    print("🌈 [20] 极坐标图...")
    fig = go.Figure(data=go.Scatterpolar(r=counts_20, theta=words_20, fill='toself'))
    fig.update_layout(title='关键词极坐标图', width=1000, height=800)
    fig.write_html(f"{output_dir}/20_极坐标图.html")
    print("   ✅ 20_极坐标图.html")

# [21] 瀑布图
if '21' in choices or generate_all:
    print("🌈 [21] 瀑布图...")
    fig = go.Figure(go.Waterfall(x=words_15, y=counts_15, text=counts_15))
    fig.update_layout(title='关键词瀑布图', width=1200, height=700)
    fig.write_html(f"{output_dir}/21_瀑布图.html")
    print("   ✅ 21_瀑布图.html")

# [22] 桑基图
if '22' in choices or generate_all:
    print("🌈 [22] 桑基图...")
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=["所有关键词"] + words_10[:5]),
        link=dict(source=[0]*5, target=list(range(1, 6)), value=counts_10[:5])
    )])
    fig.update_layout(title='关键词流向图', width=1200, height=600)
    fig.write_html(f"{output_dir}/22_桑基图.html")
    print("   ✅ 22_桑基图.html")

# [23] Dashboard
if '23' in choices or generate_all:
    print("📈 [23] Dashboard...")
    page = Page(layout=Page.SimplePageLayout)
    g1 = Gauge(init_opts=opts.InitOpts(width="600px", height="400px")).add("", [("热度", heat_index)])
    p1 = Pie(init_opts=opts.InitOpts(width="600px", height="400px")).add("", [[words_10[i], counts_10[i]] for i in range(len(words_10))], radius=["30%", "55%"])
    b1 = Bar(init_opts=opts.InitOpts(width="1200px", height="400px")).add_xaxis(words_20).add_yaxis("词频", counts_20)
    l1 = Line(init_opts=opts.InitOpts(width="1200px", height="400px")).add_xaxis(words_20).add_yaxis("趋势", counts_20)
    page.add(g1, p1, b1, l1)
    page.render(f"{output_dir}/23_Dashboard.html")
    print("   ✅ 23_Dashboard.html")

# [24] 统计报告
if '24' in choices or generate_all:
    print("📈 [24] 统计报告...")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('关键词统计分析报告', fontsize=20, fontweight='bold')
    axes[0, 0].bar(words_10, counts_10, color='steelblue')
    axes[0, 0].set_title('Top10 柱状图')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 1].pie(counts_10, labels=words_10, autopct='%1.1f%%')
    axes[0, 1].set_title('Top10 饼图')
    axes[1, 0].plot(words_20, counts_20, marker='o', color='green')
    axes[1, 0].set_title('Top20 趋势')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 1].axis('off')
    stats_text = f"""统计摘要

总词数: {len(df)}
总词频: {df['Count'].sum()}
平均词频: {df['Count'].mean():.2f}
最高词频: {df['Count'].max()}
最热词: {words_30[0]}
Top10覆盖: {coverage_rate}%"""
    axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    plt.tight_layout()
    plt.savefig(f"{output_dir}/24_统计报告.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✅ 24_统计报告.png")

print("\n" + "=" * 70)
print("🎉 所有图表生成完成！")
print("=" * 70)
print(f"\n📁 保存位置: {output_dir}/")
selected_count = len([c for c in choices if c.isdigit() and c not in ['0', '99']])
if generate_all:
    print("✅ 已生成 24 种图表（全部）")
elif generate_selected:
    print("⭐ 已生成 10 种图表（精选套餐）")
else:
    print(f"✅ 已生成 {selected_count} 种图表")
print("\n💡 推荐:")
print("  📊 PPT: 03玫瑰图、07_3D柱状图、19_3D气泡图")
print("  📈 报告: 18帕累托图、23Dashboard、24统计报告")
print("  🎨 展示: 12词云、13树状图、20极坐标图")
print("\n🌟 用Chrome或Edge打开HTML文件效果最佳！")
