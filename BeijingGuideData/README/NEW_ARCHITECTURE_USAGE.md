# 新架构使用指南

## ✅ 架构更新完成

已成功更新 `main.py` 和 `modules/vector_store.py` 以适配新的模块化架构。

---

## 📋 更新内容

### 1. `modules/vector_store.py`
✅ **修改完成**
- `save_to_db()` 现在接受 `BaseContent` 类型参数（支持多态）
- 使用 `item.model_dump()` 将 Pydantic 对象转为字典
- 提取 `text_content` 作为向量化内容
- 将其余字段作为 `metadata` 存入 ChromaDB

### 2. `main.py`
✅ **重构完成**
- 引入新模块路径：
  - `modules.crawlers.xhs_crawler`
  - `modules.crawlers.pdf_loader`
  - `modules.processors.xhs_processor`
  - `modules.processors.pdf_processor`
- 新增命令行参数：
  - `--source` (必选): `xhs` 或 `pdf`
  - `--file` (可选): 本地文件路径
  - `--doc_type` (可选): PDF 文档类型 (`legend` 或 `arch`)
  - `--keyword` (可选): XHS 爬取关键词
  - `--limit` (可选): XHS 爬取数量限制
- 实现智能调度逻辑

---

## 🚀 使用方法

### 方式 1: 处理本地小红书 JSON 文件

```bash
cd /Users/czc/vscode/Beijing_guide/BeijingGuideAI
source venv/bin/activate

python main.py --source xhs --file data/raw/xhs_manual_collection.json
```

**流程**:
1. `XHSCrawler` 加载本地 JSON
2. `XHSProcessor` 处理并清洗数据
3. 将有效的 `XHSNote` 存入向量数据库

---

### 方式 2: 处理 PDF 文档（传说故事）

```bash
python main.py --source pdf --file data/raw/legends.pdf --doc_type legend
```

**流程**:
1. `PDFLoader` 将 PDF 转图片并 OCR 提取文本
2. `PDFProcessor` 切分文本并用 LLM 清洗
3. 将 `StoryClip` 列表存入向量数据库

---

### 方式 3: 处理 PDF 文档（建筑文档）

```bash
python main.py --source pdf --file data/raw/architecture.pdf --doc_type arch
```

**流程**:
1. `PDFLoader` 提取 PDF 文本
2. `PDFProcessor` 处理并提取建筑信息
3. 将 `ArchitectureDoc` 列表存入向量数据库

---

### 方式 4: 网络爬取小红书（Web 模式）

```bash
python main.py --source xhs --keyword "北京故宫" --limit 20
```

**注意**: 当前 Web 模式为占位实现，需要在 `XHSCrawler` 中补充真实的网络爬取逻辑。

---

## 📂 数据流架构

```
┌─────────────────────────────────────────────────────────┐
│                    数据源 (Source)                       │
├─────────────────────────────────────────────────────────┤
│  • XHS (小红书 JSON)                                     │
│  • PDF (传说/建筑文档)                                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              爬虫/加载器 (Crawler/Loader)                │
├─────────────────────────────────────────────────────────┤
│  • XHSCrawler.load_local_json_data()                    │
│  • PDFLoader.load_pdf_content()                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                 处理器 (Processor)                       │
├─────────────────────────────────────────────────────────┤
│  • XHSProcessor.process_batch() → List[XHSNote]         │
│  • PDFProcessor.process_pdf() → List[StoryClip/Arch]    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│            向量存储 (Vector Store)                       │
├─────────────────────────────────────────────────────────┤
│  • save_to_db(BaseContent)                              │
│  • text_content → 向量化                                 │
│  • 其余字段 → metadata                                   │
└─────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                ChromaDB 向量数据库                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 数据模型层级

```python
BaseContent (基类)
├── XHSNote (小红书笔记)
│   ├── id: str
│   ├── text_content: str
│   ├── source_type: "xhs"
│   ├── summary: str
│   ├── location: str | None
│   ├── valid: bool
│   └── metadata: dict
│
├── StoryClip (传说故事)
│   ├── id: str
│   ├── text_content: str
│   ├── source_type: "pdf_legend"
│   ├── summary: str
│   ├── story_name: str
│   ├── is_legend: bool
│   └── metadata: dict
│
└── ArchitectureDoc (建筑文档)
    ├── id: str
    ├── text_content: str
    ├── source_type: "pdf_architecture"
    ├── summary: str
    ├── page_number: int
    ├── technical_specs: str | None
    └── metadata: dict
```

---

## ✅ 自检通过

已验证所有模块可正常导入：
- ✅ `schemas` 模块
- ✅ `XHSCrawler`
- ✅ `PDFLoader`
- ✅ `XHSProcessor`
- ✅ `PDFProcessor`
- ✅ `vector_store`
- ✅ `main` 模块

---

## 🧪 测试命令

### 查看帮助
```bash
python main.py --help
```

### 测试本地 XHS 处理
```bash
# 假设已有 data/raw/xhs_manual_collection.json
python main.py --source xhs --file data/raw/xhs_manual_collection.json
```

### 测试 PDF 处理
```bash
# 假设已有 test_data/sample.pdf
python main.py --source pdf --file test_data/sample.pdf --doc_type legend
```

---

## 📝 待办事项

### 1. 实现 XHS Web 爬取
当前 `_process_xhs_web()` 使用本地加载占位，需要：
- 在 `XHSCrawler` 中实现真实的网络爬取逻辑
- 可能需要使用 playwright 或 requests 库
- 参考 MediaCrawler 项目的实现

### 2. 完善错误处理
- 添加更详细的错误日志
- 实现重试机制
- 处理 API 限流

### 3. 性能优化
- 实现批量向量化（减少 Embedding API 调用）
- 添加缓存机制
- 并行处理多个文件

### 4. 测试覆盖
- 编写单元测试
- 添加集成测试
- 性能基准测试

---

## 📚 相关文档

- **PDF 处理文档**: `README/PDF_PROCESSING_SETUP.md`
- **快速开始**: `README/QUICKSTART_PDF.md`
- **策略和提示词**: `README/README_PROMPTS_STRATEGIES.md`
- **架构说明**: `README/README_ARCHITECTURE.md`

---

**更新日期**: 2025年12月9日  
**状态**: ✅ 架构更新完成，已通过自检
