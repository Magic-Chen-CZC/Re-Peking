# Prompts & Strategies 架构说明

本文档说明 `prompts.py` 和 `strategies.py` 两个模块的设计、使用方法和扩展指南。

## 📋 目录

1. [整体架构](#整体架构)
2. [prompts.py 详解](#promptspy-详解)
3. [strategies.py 详解](#strategiespy-详解)
4. [使用示例](#使用示例)
5. [扩展指南](#扩展指南)
6. [最佳实践](#最佳实践)

---

## 整体架构

### 设计目标

- **集中管理**: 所有 AI 提示词统一管理，避免散落在各处
- **类型映射**: 将数据源类型 (source_type) 映射到对应的 Schema 和 Prompt
- **易于扩展**: 添加新数据源只需注册新的策略
- **配置灵活**: 每个策略可以有自己的处理配置

### 模块分工

```
modules/
├── schemas.py      # 数据模型定义 (BaseContent, XHSNote, etc.)
├── prompts.py      # Prompt 提示词管理 (PromptRegistry)
└── strategies.py   # 策略映射 (PROCESSING_STRATEGIES)
```

### 数据流

```
原始数据 → 识别 source_type → 查找 Strategy → 获取 Schema + Prompt → AI 处理 → 结构化数据
```

---

## prompts.py 详解

### PromptRegistry 类

核心类，用于注册和管理所有 Prompt。

#### 主要方法

1. **register(key, prompt)** - 注册新 Prompt
2. **get(key)** - 获取指定 Prompt
3. **list_keys()** - 列出所有已注册的 Prompt key

#### 命名规范

```
{source_type}_{action}
```

- `source_type`: xhs, legend, arch, generic 等
- `action`: clean, filter, extract, summarize 等

#### 已注册的 Prompt

| Key | 描述 | 用途 |
|-----|------|------|
| `xhs_clean` | 小红书笔记清洗 | 提取地点、分类、摘要等 |
| `legend_filter` | 故事传说筛选 | 判断是否包含北京相关故事 |
| `arch_filter` | 建筑文档筛选 | 判断是否包含建筑专业信息 |
| `generic_extract` | 通用信息提取 | 默认/回退选项 |

### Prompt 设计原则

1. **明确任务**: 清楚说明需要提取的字段
2. **提供示例**: 给出分类选项、评分标准
3. **避免幻觉**: 强调基于实际内容，不要编造
4. **输出结构**: 明确返回格式（配合 Pydantic Schema）

---

## strategies.py 详解

### ProcessingStrategy 类

封装一个完整的处理策略，包含：

```python
class ProcessingStrategy:
    source_type: str            # 数据源类型
    schema: Type[BaseModel]     # Pydantic 模型
    prompt_key: str             # Prompt Registry 中的 key
    description: str            # 策略说明
    config: Dict[str, Any]      # 额外配置
```

### PROCESSING_STRATEGIES 字典

核心注册表，映射 `source_type` 到策略。

#### 当前支持的策略

| source_type | Schema | Prompt Key | 描述 |
|-------------|--------|------------|------|
| `xhs` | XHSNote | xhs_clean | 小红书笔记 |
| `legend` | StoryClip | legend_filter | 历史故事传说 |
| `arch` | ArchitectureDoc | arch_filter | 建筑文档 |
| `generic` | BaseContent | generic_extract | 通用回退 |

#### 策略配置示例

```python
"xhs": ProcessingStrategy(
    source_type="xhs",
    schema=XHSNote,
    prompt_key="xhs_clean",
    description="小红书笔记数据清洗和结构化",
    config={
        "min_content_length": 50,
        "max_title_length": 100,
        "default_category": "其他",
        "require_location": True,
    }
)
```

### 核心函数

1. **get_strategy(source_type)** - 获取策略（不存在则返回 generic）
2. **list_strategies()** - 列出所有策略
3. **validate_strategy(source_type)** - 验证策略完整性
4. **apply_strategy(source_type, raw_data)** - 应用策略处理数据

---

## 使用示例

### 1. 获取 Prompt

```python
from modules.prompts import PromptRegistry

# 获取小红书清洗 Prompt
prompt = PromptRegistry.get("xhs_clean")
print(prompt)
```

### 2. 注册新 Prompt

```python
from modules.prompts import PromptRegistry

# 注册新的 PDF 提取 Prompt
PDF_EXTRACT_PROMPT = """你是文档分析专家。请从 PDF 中提取..."""
PromptRegistry.register("pdf_extract", PDF_EXTRACT_PROMPT)
```

### 3. 查找并使用策略

```python
from modules.strategies import get_strategy

# 获取 XHS 策略
strategy = get_strategy("xhs")

# 访问策略组件
schema_class = strategy.schema        # XHSNote
prompt_text = strategy.prompt         # "你是北京资深导游..."
config = strategy.config              # {"min_content_length": 50, ...}

# 使用 Schema 验证数据
data = {
    "source_type": "xhs",
    "content_id": "123456",
    "title": "故宫一日游",
    # ...
}
validated_data = schema_class(**data)
```

### 4. AI 处理完整流程

```python
import instructor
from openai import OpenAI
from modules.strategies import get_strategy

# 1. 获取策略
strategy = get_strategy("xhs")

# 2. 初始化 AI 客户端
client = instructor.from_openai(OpenAI(...))

# 3. 调用 AI，自动解析为 Schema
result = client.chat.completions.create(
    model="deepseek-chat",
    response_model=strategy.schema,  # XHSNote
    messages=[
        {"role": "system", "content": strategy.prompt},
        {"role": "user", "content": raw_text}
    ]
)

# 4. 得到结构化数据
print(result.title)
print(result.location)
```

### 5. 在 cleaner.py 中使用

```python
from modules.prompts import PromptRegistry
from modules.strategies import get_strategy

async def clean_note_content(note: RawNote) -> ProcessedNote:
    # 方式 1: 直接从 PromptRegistry 获取
    prompt = PromptRegistry.get("xhs_clean")
    
    # 方式 2: 通过 Strategy 获取（推荐，更完整）
    strategy = get_strategy("xhs")
    prompt = strategy.prompt
    
    # 调用 AI...
```

---

## 扩展指南

### 添加新数据源

假设要添加"微博 (Weibo)"数据源，步骤如下：

#### Step 1: 定义 Schema (在 schemas.py)

```python
class WeiboPost(BaseContent):
    """微博帖子数据模型"""
    source_type: Literal["weibo"] = "weibo"
    content_id: str = Field(..., description="微博 ID")
    repost_count: int = Field(0, description="转发数")
    comment_count: int = Field(0, description="评论数")
    # ...其他字段
```

#### Step 2: 定义 Prompt (在 prompts.py)

```python
WEIBO_CLEAN_PROMPT = """你是社交媒体分析专家。请分析这条微博，提取以下信息：
1. 主题 (location)
2. 分类 (category)
3. 摘要 (summary)
...
"""
PromptRegistry.register("weibo_clean", WEIBO_CLEAN_PROMPT)
```

#### Step 3: 注册策略 (在 strategies.py)

```python
PROCESSING_STRATEGIES["weibo"] = ProcessingStrategy(
    source_type="weibo",
    schema=WeiboPost,
    prompt_key="weibo_clean",
    description="微博帖子数据清洗",
    config={
        "min_content_length": 30,
        "require_location": False,
    }
)
```

#### Step 4: 使用

```python
strategy = get_strategy("weibo")
# 开始处理微博数据...
```

---

## 最佳实践

### 1. Prompt 设计

- ✅ **明确输出格式**: 配合 Pydantic Schema，明确字段含义
- ✅ **提供判断标准**: 如何判断 valid? 如何评分?
- ✅ **避免幻觉**: 强调"基于实际内容"、"不要编造"
- ❌ **避免过长**: 过长的 Prompt 会增加 Token 消耗

### 2. 策略管理

- ✅ **一致性命名**: 使用 `{source}_action` 格式
- ✅ **完整配置**: 为每个策略提供合理的 config 默认值
- ✅ **验证机制**: 使用 `validate_strategy()` 确保策略完整
- ❌ **避免硬编码**: 不要在处理代码中硬编码 Prompt

### 3. 错误处理

```python
# 优雅的降级处理
strategy = get_strategy(source_type)
if not strategy:
    logger.warning(f"未找到策略 {source_type}，使用 generic 策略")
    strategy = get_strategy("generic")

if not strategy.prompt:
    logger.error(f"策略 {source_type} 缺少 Prompt")
    raise ValueError("Invalid strategy configuration")
```

### 4. 版本管理

当 Prompt 需要迭代时：

```python
# 方式 1: 版本化
PromptRegistry.register("xhs_clean_v1", OLD_PROMPT)
PromptRegistry.register("xhs_clean_v2", NEW_PROMPT)

# 方式 2: 在 config 中记录版本
config={
    "prompt_version": "2.0",
    "last_updated": "2025-01-15",
}
```

---

## 测试

### 测试 Prompt 注册

```python
python -m modules.prompts
```

输出：
```
已注册的 Prompt:
  - xhs_clean
  - legend_filter
  - arch_filter
  - generic_extract

=== XHS Clean Prompt ===
你是北京资深导游...
```

### 测试策略映射

```python
python -m modules.strategies
```

输出：
```
============================================================
已注册的处理策略:
============================================================

【XHS】
  描述: 小红书笔记数据清洗和结构化
  模型: XHSNote
  Prompt Key: xhs_clean
  配置: {'min_content_length': 50, ...}
  验证: ✓ 有效
...
```

---

## 总结

### 优势

1. **集中管理**: Prompt 统一维护，修改方便
2. **类型安全**: 配合 Pydantic，确保数据结构正确
3. **易于扩展**: 添加新数据源只需 3 步
4. **配置灵活**: 每个策略独立配置，互不干扰

### 架构关系

```
┌──────────────┐
│ prompts.py   │ ← Prompt 文本管理
└──────┬───────┘
       │
       ↓
┌──────────────┐     ┌──────────────┐
│ strategies.py│ ←→  │ schemas.py   │
└──────┬───────┘     └──────────────┘
       │                 ↑
       ↓                 │
┌──────────────┐         │
│ cleaner.py   │─────────┘
│ processors/  │
│ ...          │
└──────────────┘
```

### 下一步

- [ ] 在 `processors/` 目录实现各数据源的具体处理器
- [ ] 在 `crawlers/` 目录实现各数据源的采集器
- [ ] 集成 OCR、PDF 等工具到 `tools/` 目录
- [ ] 完善主流程 `main.py`，支持多源数据处理
- [ ] 添加 RAG 检索和 Web UI

---

## 参考

- [schemas.py 架构说明](./README_ARCHITECTURE.md)
- [爬虫重构说明](./README_CRAWLER_REFACTOR.md)
- [搜索功能说明](./README_SEARCH.md)
