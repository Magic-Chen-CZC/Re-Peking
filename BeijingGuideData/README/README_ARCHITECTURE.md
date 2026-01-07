# 新架构说明文档

## 📊 架构概览

```
BeijingGuideAI/
├── main.py                 # [指挥官] 接收命令行参数 (--source, --file)
├── config.py               # [配置中心] 新增 PADDLE_OCR_API_URL
├── .env                    # 环境变量配置
│
├── modules/
│   ├── schemas.py          # ✅ [协议] 定义数据模型继承体系
│   ├── prompts.py          # [指令] 定义各类 Prompt
│   ├── strategies.py       # [大脑] 定义类型到 Prompt 的映射
│   ├── vector_store.py     # [仓库] 统一入库接口
│   │
│   ├── tools/              # [工具箱]
│   │   ├── ocr.py          # PaddleOCR 封装
│   │   └── pdf_utils.py    # PDF 处理工具
│   │
│   ├── crawlers/           # [进货渠道]
│   │   ├── __init__.py     # 暴露 get_crawler(source_type)
│   │   ├── xhs_crawler.py  # 小红书爬虫
│   │   └── pdf_loader.py   # PDF 加载器
│   │
│   └── processors/         # [加工流水线]
│       ├── __init__.py     # 暴露 get_processor(source_type)
│       ├── xhs_processor.py    # 小红书处理器
│       └── pdf_processor.py     # PDF 处理器
│
└── data/
```

---

## ✅ 已完成的重构

### 1. **config.py 更新**

#### 新增配置项：
```python
# ==================== OCR 配置 ====================
PADDLE_OCR_API_URL: str = ""  # PaddleOCR API 地址（如果为空则使用本地模式）
```

#### 配置分组：
- **必填字段**：DEEPSEEK_API_KEY, DASHSCOPE_API_KEY
- **LLM 配置**：模型地址、模型名称
- **数据库配置**：ChromaDB 路径
- **OCR 配置**：PaddleOCR API
- **日志和爬取**：日志级别、爬取限制

---

### 2. **schemas.py 重构**

#### 继承体系：

```
BaseContent (基类)
    ├── XHSNote (小红书笔记)
    ├── StoryClip (传说故事)
    └── ArchitectureDoc (建筑文档)
```

#### BaseContent 基类

所有内容的统一接口：

```python
class BaseContent(BaseModel):
    id: str                    # 唯一标识
    text_content: str          # 用于向量化的核心文本
    source_type: str           # 数据源类型
    summary: str               # 内容摘要
    metadata: Dict[str, Any]   # 额外元数据
```

**设计优势**：
- ✅ 统一接口，方便多态处理
- ✅ `text_content` 字段专门用于向量化
- ✅ `metadata` 灵活存储额外信息

---

#### XHSNote - 小红书笔记

```python
class XHSNote(BaseContent):
    source_type: str = "xhs"           # 固定为 xhs
    location: Optional[str] = None     # 地点名称
    valid: bool                        # 是否有效打卡点
```

**特点**：
- 继承所有 `BaseContent` 字段
- 添加小红书特有的 `location` 和 `valid` 字段
- 适用于旅游打卡点分析

---

#### StoryClip - 传说故事

```python
class StoryClip(BaseContent):
    source_type: str = "pdf_legend"    # 固定为 pdf_legend
    story_name: str                    # 故事名称
    is_legend: bool                    # 是否为传说
```

**特点**：
- 用于存储从 PDF 提取的传说故事
- `is_legend` 区分神话传说和历史事件
- 可关联地点信息（通过 metadata）

---

#### ArchitectureDoc - 建筑文档

```python
class ArchitectureDoc(BaseContent):
    source_type: str = "pdf_architecture"  # 固定为 pdf_architecture
    page_number: int                       # 页码（>= 1）
    technical_specs: Optional[str] = None  # 技术规格
```

**特点**：
- 用于存储建筑文档和技术资料
- `page_number` 方便定位原始文档
- `technical_specs` 存储结构化的技术参数

---

## 🎯 核心设计理念

### 1. **统一入口，多态处理**

所有内容类型都继承自 `BaseContent`，可以统一处理：

```python
def save_to_database(contents: List[BaseContent]):
    """统一保存接口，接受任意类型的内容"""
    for content in contents:
        # 都有 text_content 可以向量化
        embedding = embed(content.text_content)
        # 都有 metadata 可以存储
        db.save(content.id, embedding, content.metadata)
```

### 2. **灵活扩展**

添加新数据源只需：
1. 创建新的子类继承 `BaseContent`
2. 添加特有字段
3. 无需修改其他代码

### 3. **类型安全**

使用 Pydantic 提供：
- ✅ 自动类型检查
- ✅ 数据验证（如 `page_number >= 1`）
- ✅ JSON 序列化/反序列化
- ✅ 生成 JSON Schema

---

## 🧪 测试验证

运行测试脚本：

```bash
cd /Users/czc/vscode/Beijing_guide/BeijingGuideAI
source venv/bin/activate
python test_schemas.py
```

**测试覆盖**：
1. ✅ XHSNote 创建和验证
2. ✅ StoryClip 创建和验证
3. ✅ ArchitectureDoc 创建和验证
4. ✅ 多态处理（统一操作不同类型）
5. ✅ 数据验证（错误输入捕获）

---

## 📝 使用示例

### 示例 1：创建小红书笔记

```python
from modules.schemas import XHSNote

note = XHSNote(
    id="xhs_66fad51c000000001b0224b8",
    text_content="故宫是北京最著名的景点，拥有600多年历史...",
    summary="故宫游玩攻略",
    location="故宫",
    valid=True,
    metadata={
        "url": "https://www.xiaohongshu.com/explore/...",
        "category": "影视打卡",
        "rating": 5
    }
)
```

### 示例 2：创建传说故事

```python
from modules.schemas import StoryClip

story = StoryClip(
    id="pdf_legend_baishechuan_001",
    text_content="相传白蛇修炼千年化为人形...",
    summary="白蛇传：白娘子与许仙的爱情传说",
    story_name="白蛇传",
    is_legend=True,
    metadata={
        "pdf_file": "chinese_legends.pdf",
        "page_number": 5,
        "location_mentioned": "西湖断桥"
    }
)
```

### 示例 3：创建建筑文档

```python
from modules.schemas import ArchitectureDoc

doc = ArchitectureDoc(
    id="pdf_arch_forbidden_city_taihe",
    text_content="太和殿，俗称金銮殿，是故宫三大殿之首...",
    summary="太和殿建筑规格与历史介绍",
    page_number=12,
    technical_specs="高度: 35.05米, 面积: 2377平方米",
    metadata={
        "pdf_file": "forbidden_city_architecture.pdf",
        "building_name": "太和殿"
    }
)
```

### 示例 4：统一处理（多态）

```python
from modules.schemas import BaseContent
from typing import List

def process_contents(contents: List[BaseContent]):
    """统一处理不同类型的内容"""
    for content in contents:
        print(f"处理 {content.source_type}: {content.summary}")
        # 向量化
        embedding = embed(content.text_content)
        # 保存
        db.save(content.id, embedding)

# 可以混合处理不同类型
contents = [xhs_note, story_clip, arch_doc]
process_contents(contents)
```

---

## 🔄 兼容性说明

### 旧模型保留

为了兼容旧代码，保留了 `RawNote` 和 `ProcessedNote`：

```python
# 旧模型（兼容性）
class RawNote(BaseModel):
    url: str
    raw_text: str
    images: List[str]
    source: str

class ProcessedNote(BaseModel):
    url: str
    location: Optional[str]
    category: str
    summary: str
    rating: int
    valid: bool
    metadata: Dict
```

**迁移建议**：
- 新代码使用 `XHSNote`, `StoryClip`, `ArchitectureDoc`
- 旧代码可以继续使用 `RawNote`, `ProcessedNote`
- 逐步迁移到新架构

---

## 🚀 下一步

### 待实现模块：

1. **modules/prompts.py** - 定义各类 Prompt
2. **modules/strategies.py** - 类型到 Prompt 的映射
3. **modules/tools/ocr.py** - PaddleOCR 封装
4. **modules/tools/pdf_utils.py** - PDF 处理工具
5. **modules/crawlers/** - 爬虫模块
6. **modules/processors/** - 处理器模块

### 开发顺序建议：

```
1. 工具层 (tools/)
   └── ocr.py, pdf_utils.py

2. 提示词层 (prompts.py, strategies.py)
   └── 定义各种场景的 Prompt

3. 爬虫层 (crawlers/)
   └── 实现数据采集

4. 处理层 (processors/)
   └── 实现数据清洗和转换

5. 主程序 (main.py)
   └── 整合所有模块
```

---

## 📚 参考文档

- Pydantic 文档: https://docs.pydantic.dev/
- 继承与多态: https://docs.pydantic.dev/latest/concepts/models/#inheritance
- 字段验证: https://docs.pydantic.dev/latest/concepts/validators/

---

**✅ 重构完成！**

新架构已就绪，可以开始实现其他模块了！
