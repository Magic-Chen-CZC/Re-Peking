# PDF Markdown 导出功能说明

## 📋 功能概述

在处理 PDF 文档时，系统现在会自动将 OCR 识别的内容保存为 Markdown 格式文件，方便查看和编辑。

## 📁 目录结构

```
data/
├── raw/                    # 原始 PDF 文件
│   └── legends.pdf
├── processed/              # 处理后的 Markdown 文件 ⭐ 新增
│   └── legends.md
├── review/                 # 待审核 Excel 文件
│   └── pending_*.xlsx
└── chroma_db/              # 向量数据库
```

## 🔄 处理流程

### 完整流程图

```
原始 PDF
    ↓
pdf2image (转图片)
    ↓
PaddleOCR (识别文字)
    ↓
保存 Markdown ⭐ 新增
    ↓
文本切分 (Chunk)
    ↓
LLM 清洗提取
    ↓
导出 Excel
```

### 详细步骤

1. **PDF 转图片**
   - 使用 `pdf2image` 库
   - DPI: 200 (可配置)
   - 格式: JPEG

2. **OCR 识别**
   - 使用 PaddleOCR API
   - 逐页识别文字
   - 拼接所有页面

3. **保存 Markdown** ⭐
   - 自动生成 Markdown 格式
   - 包含元数据（来源、时间、配置）
   - 保存到 `data/processed/`

4. **文本切分**
   - 使用 `SentenceSplitter`
   - chunk_size: 512
   - chunk_overlap: 64

5. **LLM 处理**
   - 使用 Qwen 模型
   - 提取结构化内容
   - 支持多结果返回

6. **导出 Excel**
   - 保存到 `data/review/`
   - 人工审核

## 📝 Markdown 文件格式

生成的 Markdown 文件格式如下：

```markdown
# legends

> 来源: legends.pdf  
> 生成时间: 2025-12-11 22:30:45  
> OCR DPI: 200

---

（这里是 OCR 识别的全文内容）

---

*本文档由 PaddleOCR 自动识别生成，可能存在识别错误*
```

## 🎯 使用示例

### 自动保存 Markdown

运行 PDF 处理时，会自动保存 Markdown：

```bash
python fetch_data.py
# 选择 [2] 传说故事
# 选择 PDF 文件
```

**输出**：
```
✓ Markdown 已保存: data/processed/legends.md
```

### 查看 Markdown 文件

```bash
# 直接查看
cat data/processed/legends.md

# 使用编辑器打开
code data/processed/legends.md
```

### 编辑 Markdown

如果 OCR 识别有误，可以：
1. 打开 `data/processed/legends.md`
2. 手动修正错误
3. 保存文件
4. （可选）重新运行处理流程，使用修正后的内容

## 🔧 配置选项

### DPI 设置

在 `PDFLoader` 初始化时调整 DPI：

```python
from modules.crawlers.pdf_loader import PDFLoader

# 默认 DPI: 200
loader = PDFLoader(dpi=200)

# 高清晰度 (更慢): 300
loader = PDFLoader(dpi=300)

# 快速模式 (更快): 150
loader = PDFLoader(dpi=150)
```

### 输出目录

在 `save_as_markdown` 调用时指定：

```python
md_path = loader.save_as_markdown(
    "test.pdf",
    output_dir="data/processed",  # 默认
    start_page=1,
    end_page=10
)
```

## 📊 文件对照表

| 原始 PDF | Markdown 文件 | Excel 审核文件 |
|---------|--------------|---------------|
| data/raw/legends.pdf | data/processed/legends.md | data/review/pending_20231211_220000.xlsx |
| data/raw/architecture.pdf | data/processed/architecture.md | data/review/pending_20231211_220100.xlsx |

## 🎨 优势

### 1. 可读性强
- Markdown 格式易读
- 可用任何文本编辑器打开
- 支持 Git 版本管理

### 2. 便于校对
- OCR 识别结果一目了然
- 可快速定位识别错误
- 支持人工修正

### 3. 可追溯
- 记录识别时间
- 记录 OCR 配置
- 保留原始文件引用

### 4. 可复用
- 修正后的 Markdown 可重新处理
- 避免重复 OCR（耗时）
- 可作为文档归档

## 🛠️ API 参考

### PDFLoader.save_as_markdown()

```python
def save_as_markdown(
    self,
    pdf_path: str,
    output_dir: str = "data/processed",
    start_page: Optional[int] = None,
    end_page: Optional[int] = None
) -> str:
    """
    将 PDF 转换为 Markdown 格式并保存
    
    Args:
        pdf_path: PDF 文件路径
        output_dir: Markdown 输出目录，默认为 data/processed
        start_page: 起始页码（从 1 开始）
        end_page: 结束页码（包含）
        
    Returns:
        保存的 Markdown 文件路径，失败则返回空字符串
    """
```

## 💡 最佳实践

### 1. 保留 Markdown 文件

建议将 `data/processed/` 目录纳入版本管理：

```bash
git add data/processed/*.md
git commit -m "Add OCR results for legends.pdf"
```

### 2. 人工校对重要文档

对于重要的 PDF：
1. 先查看 `data/processed/` 下的 Markdown
2. 修正 OCR 识别错误
3. 保存修正后的版本
4. 继续后续处理

### 3. 备份原始 Markdown

在修改前备份：

```bash
cp data/processed/legends.md data/processed/legends.md.bak
```

## 🐛 故障排除

### 问题 1: Markdown 文件为空

**症状**：生成的 `.md` 文件内容很少或为空

**原因**：
- OCR 识别失败
- PDF 是扫描件但质量很差
- PaddleOCR API 配置错误

**解决**：
1. 检查日志中的 OCR 错误信息
2. 提高 DPI 设置（200 → 300）
3. 检查 `.env` 中的 `PADDLE_OCR_API_URL`

### 问题 2: 识别结果不准确

**症状**：Markdown 中的文字有很多错误

**原因**：
- PDF 图片质量差
- DPI 设置过低
- OCR 模型不适合该类型文档

**解决**：
1. 提高 DPI：`PDFLoader(dpi=300)`
2. 手动修正 Markdown 文件
3. 考虑使用更专业的 OCR 服务

### 问题 3: 文件保存失败

**症状**：日志显示 "保存 Markdown 文件失败"

**原因**：
- 输出目录不存在或无写权限
- 磁盘空间不足
- 文件名包含非法字符

**解决**：
```bash
# 确保目录存在
mkdir -p data/processed

# 检查权限
chmod 755 data/processed

# 检查磁盘空间
df -h
```

## 📚 相关文档

- [PDF 处理设置](PDF_PROCESSING_SETUP.md)
- [OCR 工具说明](README_OCR_TOOL.md)
- [完整工作流](WORKFLOW_GUIDE.md)

---

**更新时间**: 2025-12-11  
**功能状态**: ✅ 已实现
