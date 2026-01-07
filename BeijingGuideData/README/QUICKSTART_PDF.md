# 快速开始 - PDF 处理模块

## 一键测试

```bash
# 1. 进入项目目录并激活虚拟环境
cd /Users/czc/vscode/Beijing_guide/BeijingGuideAI
source venv/bin/activate

# 2. 验证模块可用
python -c "from modules.crawlers.pdf_loader import PDFLoader; from modules.processors.pdf_processor import PDFProcessor; print('✅ 所有模块就绪')"

# 3. 运行测试
python test/test_pdf_processing.py
```

## 最简使用示例

### 提取 PDF 文本
```python
from modules.crawlers.pdf_loader import PDFLoader

loader = PDFLoader()
text = loader.load_pdf_content("your_file.pdf")
print(text)
```

### 处理 PDF 为结构化数据
```python
from modules.processors.pdf_processor import PDFProcessor

processor = PDFProcessor()

# 处理传说故事
stories = processor.process_pdf("legends.pdf", doc_type="legend")

# 处理建筑文档
buildings = processor.process_pdf("architecture.pdf", doc_type="arch")
```

## 依赖项清单

✅ **已安装**（位于 `BeijingGuideAI/venv`）：
- pdf2image
- paddleocr
- paddlepaddle
- llama-index-core

✅ **已更新**：
- requirements.txt（包含所有依赖）

## 需要的外部服务

⚠️ **PaddleOCR 服务**（需单独启动）：
```bash
# 参考 README/README_OCR_TOOL.md
```

⚠️ **Qwen API**（需配置 .env）：
```bash
QWEN_API_KEY=your_key
QWEN_MODEL_NAME=qwen-plus
```

---

**准备就绪！现在可以开始使用 PDF 处理模块了。** 🚀
