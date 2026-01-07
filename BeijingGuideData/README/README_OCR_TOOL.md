# OCR 工具使用说明

## 📋 文件位置

- **OCR 工具**: `modules/tools/ocr_tool.py`
- **配置文件**: `config.py`
- **环境变量**: `.env`

---

## ✅ 已完成的任务

### 1. 更新 `config.py`

添加了 PaddleOCR 配置项：

```python
# ==================== OCR 配置 ====================
PADDLE_OCR_API_URL: str = ""  # PaddleOCR API 地址
PADDLE_OCR_TOKEN: str = ""     # PaddleOCR API 访问令牌
```

### 2. `modules/tools/ocr_tool.py` 功能

**已实现的类：**
- `PaddleOCRClient` - PaddleOCR API 客户端

**已实现的方法：**

#### `__init__(api_url=None, token=None)`
初始化客户端，从 settings 读取配置或使用传入参数

#### `ocr_image(image_data, file_type=1, **kwargs) -> str`
核心方法，对图片进行 OCR 识别：
- 参数：
  - `image_data: bytes` - 图片二进制数据
  - `file_type: int` - 文件类型（0=PDF, 1=图片）
  - `use_doc_orientation_classify: bool` - 是否使用文档方向分类
  - `use_doc_unwarping: bool` - 是否使用文档去畸变
  - `use_textline_orientation: bool` - 是否使用文本行方向检测
- 返回：提取的文本内容（多行用换行符连接），失败返回空字符串
- 错误处理：
  - 配置未设置 → 记录 ERROR 日志，返回空字符串
  - 请求超时 → 记录 ERROR 日志，返回空字符串
  - 请求异常 → 记录 ERROR 日志，返回空字符串
  - 状态码非 200 → 记录 ERROR 日志，返回空字符串

#### `ocr_image_with_details(image_data, file_type=1, **kwargs) -> Dict`
返回详细的 OCR 结果（包含位置、置信度等）

#### `_extract_text_from_result(result) -> str`
内部方法，从 API 响应中提取文本

---

## 🔧 配置方法

### 方式 1: 使用 `.env` 文件（推荐）

在项目根目录创建或编辑 `.env` 文件：

```bash
# PaddleOCR 配置
PADDLE_OCR_API_URL=https://aistudio.baidu.com/serving/xxx/xxx
PADDLE_OCR_TOKEN=your-access-token-here
```

### 方式 2: 环境变量

```bash
export PADDLE_OCR_API_URL="https://aistudio.baidu.com/serving/xxx/xxx"
export PADDLE_OCR_TOKEN="your-access-token-here"
```

### 方式 3: 代码中直接传入

```python
from modules.tools.ocr_tool import PaddleOCRClient

client = PaddleOCRClient(
    api_url="https://aistudio.baidu.com/serving/xxx/xxx",
    token="your-access-token-here"
)
```

---

## 📖 使用示例

### 示例 1: 基本使用

```python
from modules.tools.ocr_tool import PaddleOCRClient

# 初始化客户端（从 settings 读取配置）
ocr_client = PaddleOCRClient()

# 读取图片
with open("image.jpg", "rb") as f:
    image_data = f.read()

# 进行 OCR 识别
text = ocr_client.ocr_image(image_data)

if text:
    print("识别结果:")
    print(text)
else:
    print("识别失败或未识别出文本")
```

### 示例 2: 识别 PDF

```python
from modules.tools.ocr_tool import PaddleOCRClient

ocr_client = PaddleOCRClient()

# 读取 PDF
with open("document.pdf", "rb") as f:
    pdf_data = f.read()

# 进行 OCR 识别（file_type=0 表示 PDF）
text = ocr_client.ocr_image(pdf_data, file_type=0)
print(text)
```

### 示例 3: 使用高级选项

```python
from modules.tools.ocr_tool import PaddleOCRClient

ocr_client = PaddleOCRClient()

with open("image.jpg", "rb") as f:
    image_data = f.read()

# 启用文档方向分类和去畸变
text = ocr_client.ocr_image(
    image_data,
    use_doc_orientation_classify=True,
    use_doc_unwarping=True
)
print(text)
```

### 示例 4: 获取详细结果

```python
from modules.tools.ocr_tool import PaddleOCRClient

ocr_client = PaddleOCRClient()

with open("image.jpg", "rb") as f:
    image_data = f.read()

# 获取详细结果（包含位置、置信度等）
result = ocr_client.ocr_image_with_details(image_data)

if result:
    ocr_results = result.get("result", {}).get("ocrResults", [])
    for i, res in enumerate(ocr_results):
        print(f"结果 {i+1}:")
        print(f"  文本: {res.get('prunedResult', '')}")
        print(f"  图片: {res.get('ocrImage', '')}")
```

---

## 🧪 测试

### 测试 1: 检查配置

```bash
cd /Users/czc/vscode/Beijing_guide/BeijingGuideAI
source venv/bin/activate
python3 -m modules.tools.ocr_tool
```

**预期输出（未配置时）：**
```
============================================================
PaddleOCR 客户端测试
============================================================
❌ PADDLE_OCR_API_URL 未配置
请在 .env 文件中设置 PADDLE_OCR_API_URL
```

### 测试 2: 识别图片

```bash
source venv/bin/activate
python3 -m modules.tools.ocr_tool path/to/image.jpg
```

**预期输出（配置正确时）：**
```
============================================================
PaddleOCR 客户端测试
============================================================
✓ API URL: https://aistudio.baidu.com/serving/xxx/xxx

测试图片: path/to/image.jpg
图片大小: 123456 字节

开始 OCR 识别...

============================================================
识别结果:
============================================================
这里是识别出的文本内容
可能有多行
============================================================

✓ 识别成功，提取 XXX 字符
```

---

## 🔍 API 接口说明

根据 PaddleOCR API 文档：

### 请求格式

```json
{
  "file": "<base64_encoded_file_data>",
  "fileType": 1,  // 0=PDF, 1=图片
  "useDocOrientationClassify": false,
  "useDocUnwarping": false,
  "useTextlineOrientation": false
}
```

### 响应格式

```json
{
  "result": {
    "ocrResults": [
      {
        "prunedResult": "识别出的文本",
        "ocrImage": "https://处理后的图片URL"
      }
    ]
  }
}
```

---

## 🚨 错误处理

OCR 工具实现了完善的错误处理机制：

1. **配置检查**
   - 未配置 API_URL → 警告日志 + 返回空字符串
   - 未配置 TOKEN → 警告日志（但仍尝试请求）

2. **网络错误**
   - 请求超时（30秒） → ERROR 日志 + 返回空字符串
   - 连接失败 → ERROR 日志 + 返回空字符串

3. **API 错误**
   - 状态码非 200 → ERROR 日志（包含状态码和响应） + 返回空字符串
   - 响应格式错误 → ERROR 日志 + 返回空字符串

4. **解析错误**
   - JSON 解析失败 → ERROR 日志 + 返回空字符串
   - 结果为空 → WARNING 日志 + 返回空字符串

---

## 📦 依赖

已安装在 `venv` 虚拟环境中：

```
requests>=2.31.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

---

## 🎯 与其他模块的集成

### 在 PDF 处理器中使用

```python
from modules.tools.ocr_tool import PaddleOCRClient

class PDFProcessor:
    def __init__(self):
        self.ocr_client = PaddleOCRClient()
    
    def extract_text_from_image_pdf(self, pdf_path: str) -> str:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        
        return self.ocr_client.ocr_image(pdf_data, file_type=0)
```

### 在爬虫中使用

```python
from modules.tools.ocr_tool import PaddleOCRClient

class ImageCrawler:
    def __init__(self):
        self.ocr_client = PaddleOCRClient()
    
    def process_image_note(self, image_url: str) -> str:
        # 下载图片
        response = requests.get(image_url)
        image_data = response.content
        
        # OCR 识别
        text = self.ocr_client.ocr_image(image_data)
        return text
```

---

## 📝 获取 API 访问凭证

1. 访问 https://aistudio.baidu.com/paddleocr/task
2. 在 "API 调用示例" 中获取：
   - `API_URL` - PaddleOCR API 地址
   - `TOKEN` - 访问令牌
3. 将这两个值配置到 `.env` 文件中

---

## ✅ 总结

**已完成：**
- ✅ 创建 `PaddleOCRClient` 类
- ✅ 实现 `ocr_image()` 方法（核心功能）
- ✅ 实现 `ocr_image_with_details()` 方法（详细结果）
- ✅ 从 `config.py` 读取配置（`PADDLE_OCR_API_URL` 和 `PADDLE_OCR_TOKEN`）
- ✅ 完善的错误处理和日志记录
- ✅ 支持图片和 PDF 两种文件类型
- ✅ 支持高级选项（方向分类、去畸变、文本行方向）
- ✅ 提供命令行测试工具
- ✅ 在虚拟环境中安装 `requests` 依赖

**特点：**
- 🔒 配置安全：支持 `.env` 文件和环境变量
- 📝 日志完善：记录所有关键步骤和错误
- 🛡️ 错误处理：优雅降级，返回空字符串而不是抛出异常
- 🚀 易于使用：简单的 API，清晰的文档
- 🔧 灵活配置：支持多种配置方式和高级选项

OCR 工具已经可以投入使用！🎉
