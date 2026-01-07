import pandas as pd
from pyecharts.charts import Bar
from pyecharts import options as opts
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import platform

# =================交互式输入配置=================
print("=" * 50)
print("关键词图表生成工具")
print("=" * 50)

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
    # macOS 常见的中文字体路径（按优先级）
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

# 允许用户自定义字体路径
custom_font = input(f"字体路径 (直接回车使用默认: {FONT_PATH}): ").strip()
if custom_font:
    FONT_PATH = custom_font

# 检查字体文件是否存在
if not os.path.exists(FONT_PATH):
    print(f"\n⚠️  警告：字体文件不存在: {FONT_PATH}")
    print("词云图将使用默认字体，可能无法正确显示中文")
    FONT_PATH = None

print(f"\n正在读取统计数据: {DATA_FILE} ...")
try:
    df = pd.read_csv(DATA_FILE)
    print(f"✅ 成功读取 {len(df)} 条词频数据")
except FileNotFoundError:
    print(f"❌ 错误：没找到 {DATA_FILE}，请先运行 word_frequency.py！")
    exit(1)

# 准备数据：取前 30 个高频词
top_30 = df.head(30)
words = top_30['Word'].tolist()
counts = top_30['Count'].tolist()

# -------------------------------------------------------
# 方案一：生成柱状图 (Pyecharts)
# -------------------------------------------------------
print("正在绘制柱状图...")
bar = (
    Bar(init_opts=opts.InitOpts(width="1200px", height="600px"))
    .add_xaxis(words)
    .add_yaxis("频次", counts, color="#3b82f6")
    .set_global_opts(
        title_opts=opts.TitleOpts(title="关键词词频 Top 30"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
        datazoom_opts=[opts.DataZoomOpts()]
    )
)
bar.render("图表_柱状图.html")
print("✅ 柱状图已生成: 图表_柱状图.html")

# -------------------------------------------------------
# 方案二：生成词云图 (WordCloud)
# -------------------------------------------------------
print("正在绘制词云图...")

# 将数据转为字典格式 {词: 频率} 给词云使用
# 这里我们用全部数据，不仅仅是 Top 30，这样词云更丰富
freq_dict = dict(zip(df['Word'], df['Count']))

if FONT_PATH and os.path.exists(FONT_PATH):
    wc = WordCloud(
        font_path=FONT_PATH,
        width=1600, height=900,
        background_color='white',
        max_words=200,
        colormap='viridis'
    ).generate_from_frequencies(freq_dict)
else:
    # 如果没有字体路径，尝试不指定字体
    print("⚠️  使用默认字体生成词云，中文可能显示为方框")
    wc = WordCloud(
        width=1600, height=900,
        background_color='white',
        max_words=200,
        colormap='viridis'
    ).generate_from_frequencies(freq_dict)

# 保存高清图片
plt.figure(figsize=(16, 9))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.tight_layout()
plt.savefig("图表_词云.png", dpi=300)
print("✅ 词云图已生成: 图表_词云.png")