# 🚀 新架构快速参考

## 一键启动命令

### 激活环境
```bash
cd /Users/czc/vscode/Beijing_guide/BeijingGuideAI
source venv/bin/activate
```

### 处理小红书数据
```bash
# 本地 JSON 文件
python main.py --source xhs --file data/raw/xhs_manual_collection.json
```

### 处理 PDF 文档
```bash
# 传说故事
python main.py --source pdf --file data/raw/legends.pdf --doc_type legend

# 建筑文档
python main.py --source pdf --file data/raw/architecture.pdf --doc_type arch
```

---

## 核心文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `main.py` | 主程序，命令行入口 | ✅ 已更新 |
| `modules/vector_store.py` | 向量存储，支持 BaseContent | ✅ 已更新 |
| `modules/schemas.py` | 数据模型定义 | ✅ 完成 |
| `modules/crawlers/xhs_crawler.py` | XHS 爬虫 | ✅ 完成 |
| `modules/crawlers/pdf_loader.py` | PDF 加载器 | ✅ 完成 |
| `modules/processors/xhs_processor.py` | XHS 处理器 | ✅ 完成 |
| `modules/processors/pdf_processor.py` | PDF 处理器 | ✅ 完成 |

---

## 数据模型

```python
BaseContent (基类)
├── XHSNote          # 小红书笔记
├── StoryClip        # 传说故事
└── ArchitectureDoc  # 建筑文档
```

---

## 命令行参数

```bash
--source {xhs,pdf}           # 必选：数据源
--file FILE                  # 可选：文件路径
--doc_type {legend,arch}     # 可选：PDF 类型
--keyword KEYWORD            # 可选：爬取关键词
--limit LIMIT                # 可选：爬取数量
```

---

## 测试命令

```bash
# 查看帮助
python main.py --help

# 导入测试
python -c "from modules.schemas import BaseContent; print('✅ OK')"

# 完整测试
python test_new_architecture.py
```

---

## 文档索引

- 📘 [新架构使用指南](NEW_ARCHITECTURE_USAGE.md)
- 📘 [架构更新总结](ARCHITECTURE_UPDATE_SUMMARY.md)
- 📘 [PDF 处理文档](PDF_PROCESSING_SETUP.md)
- 📘 [快速开始](QUICKSTART_PDF.md)

---

**更新日期**: 2025-12-09 | **状态**: ✅ 就绪
