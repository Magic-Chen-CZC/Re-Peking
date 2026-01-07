import pandas as pd
from collections import Counter
import os
import re

# =================交互式输入配置=================
print("=" * 50)
print("关键词词频统计工具")
print("=" * 50)

# 获取用户输入的文件名
default_input = "data1.csv"
input_file_input = input(f"请输入原始数据文件名 (直接回车使用默认: {default_input}): ").strip()
INPUT_FILE = input_file_input if input_file_input else default_input

# 检查文件是否存在
if not os.path.exists(INPUT_FILE):
    print(f"\n❌ 错误：找不到文件 '{INPUT_FILE}'")
    print("请确保文件在当前目录下，或提供完整路径")
    raise SystemExit(1)

# 获取输出文件名
default_output = "word_frequency.csv"
output_file_input = input(f"请输入输出文件名 (直接回车使用默认: {default_output}): ").strip()
OUTPUT_FILE = output_file_input if output_file_input else default_output

print(f"\n正在读取原始数据: {INPUT_FILE} ...")

# 1. 读取数据（按扩展名选择正确读取方式；避免读错文件）
ext = os.path.splitext(INPUT_FILE)[1].lower()

def _read_table(path: str) -> pd.DataFrame:
    if ext in {".xls", ".xlsx"}:
        return pd.read_excel(path)

    # CSV：data1.csv 这种文件常见来自 Excel/中文环境，优先尝试 gb18030
    sep = input("CSV 分隔符 (直接回车默认逗号 ,): ").strip() or ","

    for trial in ("utf-8-sig", "utf-8", "gb18030", "gbk"):
        try:
            return pd.read_csv(path, encoding=trial, sep=sep)
        except UnicodeDecodeError:
            continue

    # 兜底
    return pd.read_csv(path, sep=sep)


df = _read_table(INPUT_FILE)

# 针对“关键词列表单元格”做拆分：把中文标点统一后按分隔符切开
# 只按“关键词分隔符”拆：逗号/分号/顿号（不按换行、制表符、竖线、斜杠拆）
SPLIT_RE = re.compile(r"[，,；;、]+")


def split_keywords(cell: str) -> list[str]:
    cell = str(cell).strip()
    if not cell or cell.lower() in {"nan", "none"}:
        return []
    parts = [p.strip() for p in SPLIT_RE.split(cell) if p and p.strip()]
    # 这里不做二次分词：保留原始“短语关键词”作为统计单位
    return parts


# 统计：默认只统计 title_keywords / abstract_keywords（因为你的输入就是这两列）
cols = [c for c in ["title_keywords", "abstract_keywords"] if c in df.columns]
if not cols:
    print(f"❌ 找不到关键词列 title_keywords/abstract_keywords，实际列名：{list(df.columns)}")
    raise SystemExit(1)

all_terms: list[str] = []
for col in cols:
    for cell in df[col].dropna():
        all_terms.extend(split_keywords(cell))

# 词频
word_counts = Counter(all_terms)
df_count = pd.DataFrame(word_counts.most_common(), columns=["Word", "Count"])

# 保存（utf-8-sig 方便 Excel 打开）
df_count.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("-" * 30)
print("✅ 处理完成（按关键词短语统计）")
print(f"统计列: {cols}")
print(f"共提取关键词: {len(all_terms)} 条")
print(f"去重后不同关键词: {len(word_counts)} 个")
print(f"结果已保存: {OUTPUT_FILE}")
print("-" * 30)