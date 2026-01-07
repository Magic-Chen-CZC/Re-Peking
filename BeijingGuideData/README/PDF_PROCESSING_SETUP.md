# PDF 处理模块 - 安装完成文档

## ✅ 已完成任务

### 任务 1: `modules/crawlers/pdf_loader.py` ✅
**功能**: 负责从 PDF 文件中提取文本内容

#### 核心功能
- ✅ **PDF 转图片**: 使用 `pdf2image` 将 PDF 页面转换为图像
- ✅ **OCR 识别**: 调用 PaddleOCR 进行文本识别
- ✅ **全文提取**: `load_pdf_content()` 返回完整的 PDF 文本
- ✅ **按页提取**: `load_pdf_pages()` 返回每页的文本列表

#### 主要方法
```python
from modules.crawlers.pdf_loader import PDFLoader

# 方法 1: 提取全文
loader = PDFLoader()
full_text = loader.load_pdf_content(
    file_path="path/to/file.pdf",
    start_page=1,      # 起始页码（可选）
    end_page=10,       # 结束页码（可选）
    save_images=False  # 是否保存中间图片用于调试
)

# 方法 2: 按页提取
pages = loader.load_pdf_pages(
    file_path="path/to/file.pdf",
    start_page=1,
    end_page=10
)
# 返回: ["第1页文本", "第2页文本", ...]
```

---

### 任务 2: `modules/processors/pdf_processor.py` ✅
**功能**: 对 PDF 文本进行智能处理和结构化提取

#### 核心功能
- ✅ **文本切分**: 使用 `llama-index` 的 `SentenceSplitter` 切分长文本
- ✅ **策略选择**: 根据 `doc_type` (legend/arch) 自动选择处理策略
- ✅ **LLM 清洗**: 使用 QwenLLM 进行智能文本清洗和信息提取
- ✅ **结构化输出**: 返回 `List[BaseContent]` (StoryClip 或 ArchitectureDoc)

#### 主要方法
```python
from modules.processors.pdf_processor import PDFProcessor

# 初始化处理器
processor = PDFProcessor()

# 方法 1: 处理单个 PDF (传说故事)
results = processor.process_pdf(
    file_path="path/to/legend.pdf",
    doc_type="legend",           # 文档类型
    start_page=1,                # 可选：起始页
    end_page=10,                 # 可选：结束页
    chunk_size=512,              # 可选：切分大小
    chunk_overlap=50,            # 可选：重叠大小
    save_intermediate=False      # 可选：保存中间结果
)
# 返回: List[StoryClip]

# 方法 2: 处理建筑文档
results = processor.process_pdf(
    file_path="path/to/architecture.pdf",
    doc_type="arch"
)
# 返回: List[ArchitectureDoc]

# 方法 3: 批量处理
results = processor.batch_process_pdfs(
    file_paths=["file1.pdf", "file2.pdf"],
    doc_type="legend"
)
# 返回: List[List[StoryClip]]
```

---

## 📦 已安装的依赖包

所有依赖包已安装到 `BeijingGuideAI/venv` 虚拟环境：

### 核心依赖
- ✅ **pdf2image** (1.17.0) - PDF 转图片
- ✅ **paddleocr** (3.3.2) - OCR 文本识别
- ✅ **paddlepaddle** (3.2.2) - PaddleOCR 运行引擎
- ✅ **llama-index-core** (0.14.10) - 文本切分和处理

### 相关依赖
- ✅ **opencv-contrib-python** (4.10.0.84) - 图像处理
- ✅ **shapely** (2.1.2) - 几何计算
- ✅ **pypdfium2** (5.1.0) - PDF 解析
- ✅ **pillow** (已存在) - 图像处理基础库

---

## 🔧 使用前准备

### 1. 激活虚拟环境
```bash
cd /Users/czc/vscode/Beijing_guide/BeijingGuideAI
source venv/bin/activate
```

### 2. 验证安装
```bash
python -c "from modules.crawlers.pdf_loader import PDFLoader; print('✅ 导入成功')"
python -c "from modules.processors.pdf_processor import PDFProcessor; print('✅ 导入成功')"
```

### 3. 配置 OCR 服务
确保 `config.py` 中配置了 PaddleOCR 服务地址：
```python
# OCR 配置
PADDLEOCR_URL = "http://127.0.0.1:8866/predict/ocr_system"
```

启动 PaddleOCR 服务（如果还未启动）：
```bash
# 参考 README_OCR_TOOL.md 中的说明
```

### 4. 配置 Qwen LLM
确保 `.env` 文件中配置了 Qwen API：
```bash
QWEN_API_KEY=your_api_key_here
QWEN_MODEL_NAME=qwen-plus  # 或其他模型
```

---

## 📝 完整使用示例

### 示例 1: 处理传说故事 PDF
```python
from modules.processors.pdf_processor import PDFProcessor

# 初始化处理器
processor = PDFProcessor()

# 处理 PDF
story_clips = processor.process_pdf(
    file_path="data/raw/beijing_legends.pdf",
    doc_type="legend",
    start_page=1,
    end_page=20
)

# 查看结果
for clip in story_clips:
    print(f"标题: {clip.title}")
    print(f"内容: {clip.content[:100]}...")
    print(f"地点: {clip.location}")
    print("-" * 50)
```

### 示例 2: 处理建筑文档 PDF
```python
from modules.processors.pdf_processor import PDFProcessor

processor = PDFProcessor()

# 处理建筑文档
arch_docs = processor.process_pdf(
    file_path="data/raw/architecture_details.pdf",
    doc_type="arch",
    chunk_size=1024,
    chunk_overlap=100
)

# 查看结果
for doc in arch_docs:
    print(f"建筑名称: {doc.name}")
    print(f"建筑类型: {doc.type}")
    print(f"历史背景: {doc.history[:100]}...")
    print("-" * 50)
```

### 示例 3: 批量处理多个 PDF
```python
from modules.processors.pdf_processor import PDFProcessor
from pathlib import Path

processor = PDFProcessor()

# 获取所有 PDF 文件
pdf_files = list(Path("data/raw/pdfs").glob("*.pdf"))

# 批量处理
all_results = processor.batch_process_pdfs(
    file_paths=[str(f) for f in pdf_files],
    doc_type="legend"
)

# 统计结果
total_clips = sum(len(results) for results in all_results)
print(f"共处理 {len(pdf_files)} 个文件，提取 {total_clips} 条故事")
```

---

## 🧪 测试脚本

已创建完整的测试脚本：`test/test_pdf_processing.py`

运行测试：
```bash
cd /Users/czc/vscode/Beijing_guide/BeijingGuideAI
source venv/bin/activate
python test/test_pdf_processing.py
```

---

## 📚 相关文档

- **OCR 工具文档**: `README/README_OCR_TOOL.md`
- **策略和提示词文档**: `README/README_PROMPTS_STRATEGIES.md`
- **架构文档**: `README/README_ARCHITECTURE.md`

---

## ✅ 总结

所有 PDF 处理相关的模块已经完成：

1. ✅ **PDFLoader** - PDF 文本提取
2. ✅ **PDFProcessor** - 智能文本处理
3. ✅ **OCR 工具** - PaddleOCR 集成
4. ✅ **策略系统** - 提示词和 Schema 管理
5. ✅ **依赖安装** - 所有包已安装到 venv
6. ✅ **测试脚本** - 完整的测试用例

**下一步建议**：
1. 启动 PaddleOCR 服务
2. 运行 `test/test_pdf_processing.py` 测试
3. 将 PDF 处理集成到 `main.py` 主流程中

---

**更新日期**: 2025年12月8日
**安装位置**: `/Users/czc/vscode/Beijing_guide/BeijingGuideAI/venv`
