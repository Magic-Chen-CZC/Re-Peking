# 配置重构总结：源头治理

## 🎯 重构目标

将"筛选逻辑"从 Python 代码移入 Prompt，将"必填逻辑"移入 Schema，实现**源头治理**，消除冗余的 Python 判断代码。

---

## 📋 重构前后对比

### 重构前的问题

1. **冗余参数**：`domain_config` 中有大量 Python 逻辑判断参数：
   - `require_location`、`architecture_types`、`min_content_length`
   - 需要在 `pdf_processor.py` 中用 `if` 语句逐一检查

2. **职责混乱**：
   - Schema 定义：`location: Optional[str]` （允许为空）
   - Python 代码：`if require_location and not location` （手动检查）
   - Prompt：没有明确说明是否必填

3. **低效过滤**：
   - 短文本块也会调用 LLM
   - 在 LLM 处理后才检查长度，浪费 API 调用

---

### 重构后的方案

| 逻辑类型 | 原位置 | 新位置 | 实现方式 |
|---------|--------|--------|---------|
| **必填验证** | Python `if` 检查 | Schema 定义 | `location: str`（移除 `Optional`） |
| **内容筛选** | Python `if` 检查 | Prompt 指令 | 明确告诉 LLM："必须提及地点，否则跳过" |
| **文本切分** | 硬编码参数 | `chunking` 配置 | `{mode, chunk_size, overlap, min_length}` |
| **长度过滤** | LLM 后检查 | 切分时预过滤 | `if len(chunk) < min_length: skip` |

---

## 📝 具体修改

### 1. `modules/domain_config.py`

#### 删除冗余字段

```python
# ❌ 旧版（冗余）
"config": {
    "min_content_length": 200,
    "require_location": False,
    "architecture_types": [...],
}
```

#### 新增 `chunking` 配置块

```python
# ✅ 新版（聚合切分逻辑）
"chunking": {
    "mode": "sentence",      # 切分模式：none/markdown/sentence
    "chunk_size": 600,       # 每块最大字符数
    "overlap": 80,           # 块之间重叠字符数
    "min_length": 200,       # 【源头过滤】低于此值直接丢弃，不调 LLM
}
```

#### 强化 Prompt 指令

```python
# ✅ Legend Prompt（明确必填和筛选规则）
"""
⚠️ 严格筛选规则：
- **必须明确提及北京的具体地点**：如无地点请跳过
- **location 字段必填**：如果无法从文中提取，请不要提取该条数据
...
"""

# ✅ Architecture Prompt（明确允许/排除类型）
"""
⚠️ 严格筛选规则（仅提取以下类型）：
- ✅ 允许：古建筑、遗址、故居、寺庙、园林
- ❌ 排除：现代建筑（1949年后）、行政公文、施工报告
...
"""
```

---

### 2. `modules/schemas.py`

#### 移除 `Optional`，强制必填

```python
# ❌ 旧版（允许为空）
class StoryClip(BaseContent):
    story_name: str
    # location 字段不存在或在 metadata 中

# ✅ 新版（必填，Pydantic 自动校验）
class StoryClip(BaseContent):
    story_name: str
    location: str = Field(description="故事发生的具体地点（必填）")
    is_legend: bool
```

```python
# ❌ 旧版
class ArchitectureDoc(BaseContent):
    page_number: int
    technical_specs: Optional[str]
    # location 不存在

# ✅ 新版
class ArchitectureDoc(BaseContent):
    location: str = Field(description="建筑名称（必填）")
    page_number: int
    technical_specs: Optional[str]
```

---

### 3. `modules/processors/pdf_processor.py`

#### 重构 `_split_text`：源头过滤

```python
# ✅ 新版（使用 chunking 配置 + 源头过滤）
def _split_text(self, text: str, domain_config: Dict[str, Any]) -> List[str]:
    chunking = domain_config.get('chunking', {})
    mode = chunking.get('mode', 'sentence')
    chunk_size = chunking.get('chunk_size', 512)
    overlap = chunking.get('overlap', 64)
    min_length = chunking.get('min_length', 0)
    
    # 根据 mode 切分
    if mode == 'none':
        chunks = [text]
    else:
        splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        chunks = [node.text for node in splitter.get_nodes_from_documents([doc])]
    
    # 【源头过滤】在调用 LLM 前过滤短文本
    if min_length > 0:
        chunks = [c for c in chunks if len(c) >= min_length]
        logger.info(f"已过滤过短的 chunk (< {min_length} 字符)")
    
    return chunks
```

#### 简化 `_is_valid_result`：删除冗余检查

```python
# ❌ 旧版（手动检查 location）
def _is_valid_result(self, result, strategy):
    # ... 检查 valid 字段
    
    # 检查最小内容长度
    min_length = strategy.config.get("min_content_length", 0)
    if len(result.text_content) < min_length:
        return False
    
    # 检查是否必须有地点
    require_location = strategy.config.get("require_location", False)
    if require_location and not result.location:
        return False
    
    return True
```

```python
# ✅ 新版（依赖 Schema 和 Prompt）
def _is_valid_result(self, result, domain_config):
    """
    职责分离：
    - 必填验证 → Schema (Pydantic 自动校验)
    - 内容筛选 → Prompt (LLM 判断)
    - 长度过滤 → _split_text (源头过滤)
    """
    # 1. StoryClip 特殊检查
    if isinstance(result, StoryClip) and not result.is_legend:
        return False
    
    # 2. 检查 valid 字段（由 LLM 在 Prompt 中判断）
    if hasattr(result, 'valid'):
        return result.valid
    
    return True
    # 注意：location 必填验证已由 Pydantic 完成
    # 如果 LLM 未提取 location，会抛出 ValidationError
```

#### 捕获 `ValidationError`

```python
# ✅ 在 _process_chunks 中区分异常类型
try:
    # LLM 提取
    response_list = self.llm.generate(...)
    
    for item in response_list:
        if self._is_valid_result(item, domain_config):
            results.append(item)

except ValidationError as e:
    # Pydantic 验证失败：LLM 未提取必填字段（如 location）
    logger.warning(f"数据验证失败（缺少必填字段）: {str(e)}")
    
except Exception as e:
    logger.error(f"处理失败: {str(e)}")
```

---

## 🔄 数据流程（新）

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PDF 文本提取                                              │
│    full_text = pdf_loader.load_pdf_content(...)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 文本切分 + 源头过滤                                        │
│    chunking = domain_config['chunking']                     │
│    chunks = split_text(text, chunking)                      │
│    ✅ 过滤掉 len(chunk) < min_length 的块                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LLM 提取 (遵循 Prompt 指令)                               │
│    prompt = domain_config['prompt']                         │
│    - "必须提取 location，如无则跳过"                          │
│    - "仅提取古建筑，排除现代建筑"                             │
│    response = llm.generate(prompt, schema)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Pydantic 验证                                             │
│    try:                                                     │
│        obj = StoryClip(**data)  # location 必填             │
│    except ValidationError:                                  │
│        logger.warning("缺少 location，丢弃")                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 简化验证                                                  │
│    if obj.valid:  # LLM 在 Prompt 中已判断                   │
│        results.append(obj)                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ 重构效果

### 代码简化

| 指标 | 旧版 | 新版 | 改进 |
|------|------|------|------|
| `_is_valid_result` 行数 | ~40 行 | ~20 行 | **-50%** |
| 配置参数数量 | 5+ 个 | 1 个 (`chunking`) | **-80%** |
| 手动 `if` 检查 | 4 处 | 1 处 | **-75%** |

### 性能优化

- ✅ **减少 LLM 调用**：过短的 chunk 在源头被过滤，不调用 LLM
- ✅ **减少 API 费用**：避免处理明显无效的短文本

### 可维护性提升

- ✅ **职责清晰**：
  - Schema：定义数据结构和必填字段
  - Prompt：告诉 LLM 筛选规则
  - Processor：执行流程，无业务判断

- ✅ **易于扩展**：
  - 新增字段？修改 Schema，Excel 自动同步
  - 调整筛选规则？修改 Prompt，无需改代码
  - 调整切分策略？修改 `chunking`，统一管理

---

## 📚 相关文档

- `modules/domain_config.py` - 业务配置中心
- `modules/schemas.py` - 数据模型定义
- `modules/processors/pdf_processor.py` - 处理流程
- `modules/reviewer.py` - Excel 动态导入导出

---

## 🎓 设计原则总结

1. **源头治理**：在数据流最早的阶段过滤/验证，避免后续无效处理
2. **职责分离**：Prompt 管内容，Schema 管结构，Processor 管流程
3. **声明式配置**：用配置表达意图，减少命令式代码
4. **自动化验证**：利用框架能力（Pydantic），减少手写校验代码

---

*重构完成时间：2025年12月14日*
