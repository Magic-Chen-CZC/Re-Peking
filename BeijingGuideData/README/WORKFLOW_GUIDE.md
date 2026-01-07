# 新架构使用指南

## 📋 概述

项目已重构为三个独立的入口脚本，职责清晰：

1. **fetch_data.py** - 数据采集和清洗
2. **build_db.py** - 数据入库
3. **search.py** - 数据检索

## 🚀 完整工作流

### 步骤 1: 数据采集 (fetch_data.py)

#### 方式 A: 交互式模式 (推荐)

```bash
python fetch_data.py
```

交互界面示例：
```
========================================
🤖 BeijingGuideAI 数据采集向导
========================================
请选择数据处理模式：
[1] 小红书笔记 (XHS -> Excel)
[2] 传说故事 (PDF/Legend -> Excel)
[3] 建筑文档 (PDF/Arch -> Excel)

请输入序号 (1-3): 2

----------------------------------------
📂 正在扫描 data/raw/ 下的 PDF 文件...
发现以下文件：
[1] old_beijing_stories.pdf (2.3 MB)
[2] gugong_history.pdf (1.8 MB)

请选择要处理的文件序号: 1
----------------------------------------

🚀 开始处理：old_beijing_stories.pdf (模式: 传说故事)...
```

#### 方式 B: 命令行模式

```bash
# 处理小红书 JSON 数据
python fetch_data.py --source xhs --file data/raw/xhs_notes.json

# 处理传说故事 PDF
python fetch_data.py --source pdf --file test_data/legends.pdf --doc_type legend

# 处理建筑文档 PDF
python fetch_data.py --source pdf --file data/raw/architecture.pdf --doc_type arch
```

**输出**: Excel 文件保存在 `data/review/pending_{timestamp}.xlsx`

---

### 步骤 2: 人工审核

打开生成的 Excel 文件（例如 `data/review/pending_20231211_153045.xlsx`）：

1. 检查 `valid` 字段，设置为 `True` (保留) 或 `False` (删除)
2. 修改不准确的内容（摘要、地点、分类等）
3. 删除不需要的行
4. 保存文件

---

### 步骤 3: 数据入库 (build_db.py)

```bash
# 导入审核后的数据（默认只导入 valid=True 的数据）
python build_db.py --file data/review/pending_20231211_153045.xlsx

# 导入所有数据（不验证 valid 字段）
python build_db.py --file data/review/pending_20231211_153045.xlsx --no-validate
```

**输出**: 数据存入向量数据库 `data/chroma_db/`

---

### 步骤 4: 数据检索 (search.py)

#### 方式 A: 交互式模式

```bash
python search.py
```

然后输入查询问题，例如：
- "北京有哪些适合夏天去的景点？"
- "介绍一下故宫的历史"
- "推荐一些胡同文化相关的地方"

#### 方式 B: 命令行模式

```bash
python search.py 北京有哪些适合夏天去的景点
```

---

## 📁 目录结构

```
BeijingGuideAI/
├── fetch_data.py          # 数据采集脚本
├── build_db.py            # 数据入库脚本
├── search.py              # 数据检索脚本
├── main_legacy.py.bak     # 旧版主程序（已废弃）
│
├── data/
│   ├── raw/               # 原始数据存放目录
│   │   ├── *.json        # 小红书 JSON 文件
│   │   └── *.pdf         # PDF 文档
│   ├── review/            # 待审核 Excel 文件
│   │   └── pending_*.xlsx
│   └── chroma_db/         # 向量数据库
│
├── modules/
│   ├── crawlers/          # 数据爬虫
│   ├── processors/        # 数据处理器
│   ├── reviewer.py        # Excel 审核模块 (新)
│   ├── vector_store.py    # 向量存储
│   └── ...
│
└── test_data/             # 测试数据
```

---

## 🎯 快速开始

### 示例 1: 处理小红书数据

```bash
# 1. 将 JSON 文件放入 data/raw/
cp xhs_notes.json data/raw/

# 2. 采集和处理
python fetch_data.py
# 选择 [1] 小红书笔记
# 选择对应的 JSON 文件

# 3. 在 Excel 中审核数据

# 4. 入库
python build_db.py --file data/review/pending_20231211_153045.xlsx

# 5. 检索测试
python search.py 北京有什么好玩的地方
```

### 示例 2: 处理 PDF 传说故事

```bash
# 1. 将 PDF 文件放入 data/raw/
cp legends.pdf data/raw/

# 2. 采集和处理
python fetch_data.py
# 选择 [2] 传说故事
# 选择对应的 PDF 文件

# 3. 在 Excel 中审核数据

# 4. 入库
python build_db.py --file data/review/pending_20231211_153045.xlsx

# 5. 检索测试
python search.py 有哪些关于北京的传说故事
```

---

## 🔧 依赖安装

确保安装了所有依赖：

```bash
pip install -r requirements.txt
```

主要依赖：
- pandas
- openpyxl (用于 Excel 读写)
- chromadb
- llama-index
- instructor
- 等等

---

## ⚙️ 配置

确保 `.env` 文件配置正确：

```bash
# Qwen API
QWEN_API_KEY=sk-xxx
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# DashScope API
DASHSCOPE_API_KEY=sk-xxx
```

---

## 📝 注意事项

1. **数据目录**: 原始数据放在 `data/raw/`，审核文件在 `data/review/`
2. **Excel 格式**: 不要修改 `_content_type` 列，这是用于反序列化的类型标识
3. **文件命名**: Excel 文件名会自动生成时间戳，避免覆盖
4. **审核建议**: 重点检查 `summary`、`location`、`valid` 字段
5. **批量处理**: 可以多次运行 `fetch_data.py` 生成多个 Excel，审核后分批入库

---

## 🆚 新旧架构对比

### 旧架构 (main.py)
- ❌ 数据直接入库，无人工审核环节
- ❌ 数据质量无法控制
- ❌ 错误数据难以修正

### 新架构 (三脚本分离)
- ✅ 人工审核环节，确保数据质量
- ✅ Excel 可视化编辑，方便修改
- ✅ 职责清晰，易于维护和扩展
- ✅ 交互式模式，使用更友好

---

## 🐛 故障排除

### 问题 1: 找不到文件
```
❌ 未找到任何 PDF 文件
💡 请先将文件放入 data/raw/ 目录
```
**解决**: 确保文件放在正确的目录，文件名后缀正确

### 问题 2: Excel 读取失败
```
无法解析导入"pandas"
```
**解决**: 安装 pandas 和 openpyxl
```bash
pip install pandas openpyxl
```

### 问题 3: 向量数据库错误
```
无法解析导入"chromadb"
```
**解决**: 安装完整依赖
```bash
pip install -r requirements.txt
```

---

## 📚 扩展阅读

- [架构更新说明](README/ARCHITECTURE_UPDATE_SUMMARY.md)
- [PDF 处理设置](README/PDF_PROCESSING_SETUP.md)
- [搜索系统说明](README/SEARCH_README.md)
- [提示词和策略](README/README_PROMPTS_STRATEGIES.md)
