# 统一 Chunking 接口重构总结

**日期**: 2025-12-14  
**任务**: 将所有 processors 统一使用 `domain_config.py` 中的 chunking 配置

---

## 📋 重构目标

1. **统一配置管理**: 所有业务类型的切分参数集中在 `domain_config.py`
2. **消除硬编码**: 删除各 processor 中的硬编码切分参数
3. **源头过滤**: 在切分时就过滤掉过短的 chunk，避免无效 LLM 调用
4. **保持扩展性**: 保留 `mode` 字段以便后续支持 markdown/其他切分模式

---

## ✅ 已完成的修改

### 1. `modules/domain_config.py`

**统一 chunking 配置结构**：

```python
"chunking": {
    "mode": "sentence",    # 切分模式（保留以便扩展）
    "chunk_size": 800,     # 每块最大字符数
    "overlap": 100,        # 块之间重叠字符数
    "min_length": 150,     # 最小块长度（源头过滤）
}
```

**各业务类型配置**：

| 业务类型 | mode | chunk_size | overlap | min_length | 说明 |
|---------|------|------------|---------|------------|------|
| **xhs** | none | 0 | 0 | 50 | 不分块（短文本） |
| **legend** | sentence | 800 | 100 | 150 | 故事文档 |
| **arch** | sentence | 600 | 80 | 200 | 建筑文档（信息密度高） |

**新增辅助函数**：
- `get_chunking_config(domain_type)`: 获取完整 chunking 配置

---

### 2. `modules/processors/pdf_processor.py`

**✅ 重构 `_split_text()` 方法**：

```python
def _split_text(self, text: str, domain_config: Dict[str, Any]) -> List[str]:
    """
    使用配置中的 chunking 参数切分文本，并预过滤短文本
    
    源头过滤逻辑：
    - 在切分后立即检查每个 chunk 的长度
    - 过滤掉 len(chunk) < min_length 的块
    - 避免对过短文本调用 LLM（节省 API 费用）
    """
    # 获取 chunking 配置
    chunking = domain_config.get('chunking', {})
    mode = chunking.get('mode', 'sentence')
    chunk_size = chunking.get('chunk_size', 512)
    overlap = chunking.get('overlap', 64)
    min_length = chunking.get('min_length', 0)
    
    # 根据 mode 选择切分策略
    if mode == 'none':
        chunks = [text]  # 不切分
    else:
        # 使用 SentenceSplitter 按字数切分
        splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
        )
        nodes = splitter.get_nodes_from_documents([Document(text=text)])
        chunks = [node.text for node in nodes if node.text.strip()]
    
    # 【源头过滤】过滤过短的 chunk
    if min_length > 0:
        original_count = len(chunks)
        chunks = [chunk for chunk in chunks if len(chunk) >= min_length]
        filtered_count = original_count - len(chunks)
        if filtered_count > 0:
            logger.info(f"已过滤 {filtered_count} 个过短的 chunk")
    
    return chunks
```

**关键改进**：
- ✅ 动态读取 chunking 配置（不再硬编码）
- ✅ 支持 `mode='none'` 不分块模式
- ✅ 源头过滤：切分后立即检查长度
- ✅ 日志记录过滤统计

---

### 3. `modules/processors/xhs_processor.py`

**✅ 替换旧的 `strategies` 为 `domain_config`**：

```python
# 修改前
from modules.strategies import get_strategy
self.strategy = get_strategy("xhs")
system_prompt = self.strategy.prompt

# 修改后
from modules.domain_config import get_domain_config
self.domain_config = get_domain_config("xhs")
system_prompt = self.domain_config['prompt']
```

**✅ 简化 instructor 模式**：

```python
# 修改前：定义临时 Extraction 模型
class XHSNoteExtraction(BaseModel):
    location: Optional[str] = ...
    # ...

extraction = client.create(..., response_model=XHSNoteExtraction)

# 修改后：直接使用 domain_config 的 schema
schema_class = self.domain_config['schema']
extraction = client.create(..., response_model=schema_class)
```

**关键改进**：
- ✅ 统一使用 `domain_config`
- ✅ 删除重复的临时模型定义
- ✅ 直接使用配置中的 Schema

---

### 4. `fetch_data.py` - Web 数据处理

**✅ 重构 `fetch_web_data()` 函数**：

```python
# 修改前：硬编码切分参数
text_splitter = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=64,
    separator="\n"
)
doc = Document(text=full_text)
nodes = text_splitter.get_nodes_from_documents([doc])
chunks = [node.text for node in nodes if node.text.strip()]

# 修改后：使用统一的处理逻辑
processor = PDFProcessor()
chunks = processor._split_text(full_text, domain_config)
```

**关键改进**：
- ✅ 删除硬编码切分参数
- ✅ 复用 PDFProcessor 的统一切分逻辑
- ✅ 自动应用 chunking 配置和源头过滤

---

## 🎯 统一后的数据处理流程

```
┌─────────────────────────────────────────────────────────┐
│  domain_config.py (配置中心)                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │ "xhs": { chunking: {mode: none, min_length: 50}}│   │
│  │ "legend": {chunking: {size: 800, min: 150}}    │   │
│  │ "arch": {chunking: {size: 600, min: 200}}      │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
┌──────────────────┐  ┌──────────────────┐
│ pdf_processor.py │  │ xhs_processor.py │
│ ┌──────────────┐ │  │ ┌──────────────┐ │
│ │_split_text() │ │  │ │使用 config   │ │
│ │  ↓           │ │  │ │['schema']    │ │
│ │读取 chunking │ │  │ │['prompt']    │ │
│ │配置          │ │  │ └──────────────┘ │
│ │  ↓           │ │  └──────────────────┘
│ │按 mode 切分  │ │           │
│ │  ↓           │ │           │
│ │源头过滤      │ │           │
│ │min_length    │ │           │
│ └──────────────┘ │           │
└──────────────────┘           │
          │                    │
          └────────┬───────────┘
                   ▼
         ┌──────────────────┐
         │  统一的 LLM 处理  │
         │  + Pydantic 验证 │
         └──────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │  Excel 动态导出  │
         └──────────────────┘
```

---

## 📊 重构效果对比

| 指标 | 重构前 | 重构后 | 改进 |
|------|--------|--------|------|
| **配置位置** | 分散在 3 个文件 | 集中在 `domain_config.py` | ✅ 统一管理 |
| **硬编码参数** | 多处硬编码 | 全部动态读取 | ✅ 易于修改 |
| **重复代码** | Web/PDF 分别切分 | 复用同一逻辑 | ✅ DRY 原则 |
| **过滤时机** | LLM 调用后 | 切分时（源头） | ✅ 节省 API |
| **可扩展性** | 难以添加新模式 | 保留 `mode` 字段 | ✅ 易扩展 |

---

## 🔧 如何调整切分参数

**现在只需修改一个文件**：`modules/domain_config.py`

### 示例 1: 调整建筑文档的切分大小

```python
"arch": {
    "chunking": {
        "chunk_size": 1000,  # 改为 1000 字符
        "min_length": 300,   # 提高最小长度要求
    },
}
```

### 示例 2: 为传说故事启用 Markdown 模式（未来扩展）

```python
"legend": {
    "chunking": {
        "mode": "markdown",  # 将来支持按 Markdown 标题切分
        "chunk_size": 1500,
    },
}
```

**无需修改任何 processor 代码**，配置立即生效！

---

## ✨ 后续扩展方向

### 1. 支持更多 chunking 模式

在 `pdf_processor._split_text()` 中添加：

```python
if mode == 'markdown':
    # 按 Markdown 标题切分
    from llama_index.core.node_parser import MarkdownNodeParser
    splitter = MarkdownNodeParser()
elif mode == 'semantic':
    # 语义切分（基于相似度）
    from llama_index.core.node_parser import SemanticSplitterNodeParser
    splitter = SemanticSplitterNodeParser(...)
```

### 2. 智能 chunk 大小调整

根据文档类型自动调整：

```python
def auto_adjust_chunk_size(text: str, doc_type: str) -> int:
    """根据文本长度和类型动态调整 chunk_size"""
    base_size = get_chunking_config(doc_type)['chunk_size']
    if len(text) < 2000:
        return base_size // 2  # 短文档用小块
    return base_size
```

### 3. Chunk 质量评估

在源头过滤时增加质量检查：

```python
def is_valid_chunk(chunk: str, min_length: int) -> bool:
    """评估 chunk 质量"""
    # 长度检查
    if len(chunk) < min_length:
        return False
    
    # 内容质量检查
    if chunk.count('\n') / len(chunk) > 0.5:  # 太多换行
        return False
    
    if len(set(chunk)) < 20:  # 字符种类太少
        return False
    
    return True
```

---

## 🎉 总结

通过这次重构，我们实现了：

1. ✅ **配置集中化**: 所有 chunking 参数集中在 `domain_config.py`
2. ✅ **代码复用**: 所有 processors 使用同一套切分逻辑
3. ✅ **性能优化**: 源头过滤减少无效 LLM 调用
4. ✅ **易于维护**: 修改配置无需改代码
5. ✅ **保持扩展性**: 保留 `mode` 字段支持未来扩展

**下一步**: 可以开始进行端到端测试，验证整个数据处理流程！
