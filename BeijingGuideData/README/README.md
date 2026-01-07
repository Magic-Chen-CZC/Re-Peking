# BeijingGuideAI - 北京导览 AI 系统

> 智能数据采集、人工审核、向量检索一体化解决方案

## 🎯 核心功能

- 📥 **数据采集**: 支持小红书笔记、PDF 文档等多种数据源
- 👁️ **人工审核**: Excel 可视化审核，确保数据质量
- 💾 **向量存储**: ChromaDB + LlamaIndex，高效语义检索
- 🤖 **LLM 增强**: Qwen 大模型清洗和提取结构化内容

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
QWEN_API_KEY=sk-your-key-here
DASHSCOPE_API_KEY=sk-your-key-here
```

### 3. 完整工作流

#### 📥 步骤 1: 采集数据

```bash
python fetch_data.py
```

选择数据源，选择文件，自动处理并生成 Excel

#### ✅ 步骤 2: 审核数据

在 Excel 中审核 `data/review/pending_*.xlsx`

#### 💾 步骤 3: 入库

```bash
python build_db.py --file data/review/pending_20231211_153045.xlsx
```

#### 🔍 步骤 4: 检索

```bash
python search.py
```

## 📁 项目结构

```
BeijingGuideAI/
├── fetch_data.py          # 📥 数据采集脚本
├── build_db.py            # 💾 数据入库脚本
├── search.py              # 🔍 数据检索脚本
│
├── data/
│   ├── raw/               # 原始数据
│   ├── review/            # 待审核 Excel
│   └── chroma_db/         # 向量数据库
│
├── modules/
│   ├── crawlers/          # 数据爬虫
│   ├── processors/        # 数据处理器
│   ├── reviewer.py        # Excel 审核模块
│   ├── vector_store.py    # 向量存储
│   ├── schemas.py         # 数据模型
│   ├── strategies.py      # 处理策略
│   └── prompts.py         # 提示词库
│
└── README/                # 详细文档
```

## 📖 详细文档

- [完整工作流指南](README/WORKFLOW_GUIDE.md) ⭐ 推荐
- [架构说明](README/README_ARCHITECTURE.md)
- [PDF 处理设置](README/PDF_PROCESSING_SETUP.md)
- [搜索系统说明](README/SEARCH_README.md)

## 🎨 支持的数据源

| 数据源 | 格式 | 文档类型 | 说明 |
|--------|------|----------|------|
| 小红书笔记 | JSON | - | 旅游攻略、打卡点推荐 |
| PDF 文档 | PDF | legend | 传说故事、历史典故 |
| PDF 文档 | PDF | arch | 建筑技术文档 |

## 🛠️ 技术栈

- **LLM**: Qwen (通义千问)
- **Embedding**: DashScope Embedding
- **向量数据库**: ChromaDB
- **索引框架**: LlamaIndex
- **数据审核**: Pandas + openpyxl
- **结构化输出**: Instructor + Pydantic

## 💡 使用示例

### 交互式采集

```bash
$ python fetch_data.py

========================================
🤖 BeijingGuideAI 数据采集向导
========================================
请选择数据处理模式：
[1] 小红书笔记 (XHS -> Excel)
[2] 传说故事 (PDF/Legend -> Excel)
[3] 建筑文档 (PDF/Arch -> Excel)

请输入序号 (1-3): 2
```

### 命令行采集

```bash
python fetch_data.py --source pdf --file test_data/legends.pdf --doc_type legend
```

### 数据入库

```bash
python build_db.py --file data/review/pending_20231211_153045.xlsx
```

### 交互式检索

```bash
$ python search.py

🔍 北京导览 AI - 交互式检索系统
✅ 检索系统已就绪！

🔎 请输入查询: 北京有哪些适合夏天去的景点

📝 检索结果:
北京夏天适合去的景点有...
```

## 🔧 开发指南

### 添加新的数据源

1. 在 `modules/schemas.py` 定义数据模型
2. 在 `modules/prompts.py` 添加清洗提示词
3. 在 `modules/strategies.py` 注册处理策略
4. 在 `modules/crawlers/` 实现爬虫
5. 在 `modules/processors/` 实现处理器

### 自定义提示词

编辑 `modules/prompts.py` 中的提示词模板

### 调整切分参数

在 `PDFProcessor` 初始化时调整 `chunk_size` 和 `chunk_overlap`

## 📊 数据质量控制

- ✅ LLM 自动清洗和结构化
- ✅ Excel 人工审核环节
- ✅ Valid 字段标记有效性
- ✅ 批量处理，灵活入库

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

---

**快速开始**: 查看 [完整工作流指南](README/WORKFLOW_GUIDE.md)
