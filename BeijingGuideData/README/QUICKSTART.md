# 🚀 快速开始指南

## 一、环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `pandas` + `openpyxl` (Excel 处理)
- `chromadb` (向量数据库)
- `llama-index` (索引框架)
- `instructor` (结构化输出)

### 2. 配置 API Key

编辑 `.env` 文件：

```bash
# Qwen API
QWEN_API_KEY=sk-your-qwen-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# DashScope API (用于 Embedding)
DASHSCOPE_API_KEY=sk-your-dashscope-key
```

## 二、数据准备

将原始数据放入 `data/raw/` 目录：

```bash
# 小红书 JSON 数据
data/raw/xhs_notes.json

# PDF 文档
data/raw/legends.pdf
data/raw/architecture.pdf
```

## 三、完整流程演示

### 示例：处理传说故事 PDF

#### 第 1 步：采集数据

```bash
python fetch_data.py
```

**交互流程**：
```
========================================
🤖 BeijingGuideAI 数据采集向导
========================================
请选择数据处理模式：
[1] 小红书笔记 (XHS -> Excel)
[2] 传说故事 (PDF/Legend -> Excel)
[3] 建筑文档 (PDF/Arch -> Excel)

请输入序号 (1-3): 2

------------------------------------------------------------
📂 正在扫描 data/raw/ 下的 PDF 文件...
发现以下文件：
[1] legends.pdf (2.3 MB)

请选择要处理的文件序号 (1-1): 1
------------------------------------------------------------

🚀 开始处理：legends.pdf (模式: 传说故事)...
```

**输出**：
```
✅ 数据采集和处理完成
📊 共处理 15 条数据
📁 Excel 文件: data/review/pending_20231211_153045.xlsx

⚠️  请在 Excel 中人工审核数据
```

#### 第 2 步：人工审核

打开 `data/review/pending_20231211_153045.xlsx`：

| _content_type | id | summary | location | valid | text_content |
|---------------|----|---------|-----------|----|--------------|
| StoryClip | xxx | 景山公园的传说... | 景山公园 | TRUE | ... |
| StoryClip | yyy | 白塔寺的故事... | 白塔寺 | TRUE | ... |

**审核要点**：
- 检查 `valid` 列：保留 TRUE，删除或改为 FALSE
- 修正错误的 `location`、`summary` 等
- 删除无效的行

保存后关闭。

#### 第 3 步：入库

```bash
python build_db.py --file data/review/pending_20231211_153045.xlsx
```

**输出**：
```
✅ 数据入库完成
📊 成功入库 13 条数据
```

#### 第 4 步：检索测试

**交互式模式**：

```bash
python search.py
```

```
🔍 北京导览 AI - 交互式检索系统
✅ 检索系统已就绪！

🔎 请输入查询: 景山公园有什么传说故事

📝 检索结果:
景山公园有一个著名的传说...

📚 来源文档:
【1】 景山公园 | 评分: 4.5/5 | 分类: 历史传说
    景山公园的传说故事包括...
```

**命令行模式**：

```bash
python search.py 景山公园有什么传说故事
```

## 四、命令行快捷模式

如果你已经知道文件路径，可以直接使用命令行：

```bash
# 采集
python fetch_data.py --source pdf --file data/raw/legends.pdf --doc_type legend

# 入库
python build_db.py --file data/review/pending_20231211_153045.xlsx

# 检索
python search.py 景山公园有什么传说故事
```

## 五、常见问题

### Q1: 找不到文件

```
❌ 未找到任何 PDF 文件
💡 请先将文件放入 data/raw/ 目录
```

**解决**：确保文件在 `data/raw/` 目录下，且文件扩展名正确（.json 或 .pdf）

### Q2: 缺少依赖

```
ModuleNotFoundError: No module named 'openpyxl'
```

**解决**：
```bash
pip install openpyxl pandas
```

### Q3: API Key 错误

```
Error: Invalid API key
```

**解决**：检查 `.env` 文件中的 API Key 是否正确

### Q4: PDF 处理失败

```
Error: poppler not found
```

**解决**（macOS）：
```bash
brew install poppler
```

## 六、目录结构说明

```
BeijingGuideAI/
├── fetch_data.py          # ✅ 运行这个采集数据
├── build_db.py            # ✅ 运行这个入库
├── search.py              # ✅ 运行这个检索
│
├── data/
│   ├── raw/               # 👈 把原始文件放这里
│   ├── review/            # 👈 审核 Excel 在这里
│   └── chroma_db/         # 👈 向量数据库在这里
│
├── modules/               # 内部模块，不需要手动运行
├── test_data/             # 测试数据
└── README/                # 详细文档
```

## 七、下一步

- 查看 [完整工作流指南](WORKFLOW_GUIDE.md)
- 了解 [架构设计](README_ARCHITECTURE.md)
- 学习 [提示词和策略](README_PROMPTS_STRATEGIES.md)

---

**祝你使用愉快！** 🎉

如有问题，请查看文档或提交 Issue。
