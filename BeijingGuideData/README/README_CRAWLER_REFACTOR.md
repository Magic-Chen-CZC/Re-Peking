# 爬虫模块重构说明文档

## 📋 重构概述

本次重构实现了**多模式数据采集**功能，支持从不同数据源获取原始数据，并统一格式化为标准的 `RawNote` 对象。

### 🎯 核心改进

1. **工厂模式设计** - 统一的数据采集接口 `get_raw_data()`
2. **多数据源支持** - Local（本地文件）和 Web（网络爬取）两种模式
3. **格式标准化** - 自动清洗杂乱数据，转换为统一格式
4. **灵活扩展** - 易于添加新的数据源（如数据库、API等）

---

## 📁 文件结构

```
BeijingGuideAI/
├── modules/
│   ├── crawler.py          # ✅ 重构后的爬虫模块
│   ├── schemas.py          # 数据模型定义
│   ├── cleaner.py          # AI 清洗模块
│   └── vector_store.py     # 向量存储模块
├── main.py                 # ✅ 更新后的主程序
├── data/
│   └── raw/
│       └── xhs_manual_collection.json  # 本地数据文件
└── README_CRAWLER_REFACTOR.md  # 本文档
```

---

## 🔧 核心功能说明

### 1. `modules/crawler.py` - 爬虫模块

#### 1.1 `_load_local_data(file_path)` - 本地模式

**功能**: 从本地 JSON 文件加载数据并转换为标准格式

**核心逻辑**:
```python
# 格式清洗与装箱流程
1. URL处理：优先取 url 字段，无则生成 "unknown_local_id_N"
2. 文本处理：优先取 raw_text，无则拼接 title + desc
3. 图片处理：确保 images 字段为列表
4. 来源标记：统一标记为 "local_manual"
5. 创建标准 RawNote 对象
```

**输入示例** (JSON):
```json
{
  "url": "https://example.com/note1",
  "title": "标题",
  "desc": "正文内容",
  "images": ["img1.jpg", "img2.jpg"]
}
```

**输出**: `RawNote` 对象
```python
RawNote(
    url="https://example.com/note1",
    raw_text="标题\n正文内容",
    images=["img1.jpg", "img2.jpg"],
    source="local_manual"
)
```

#### 1.2 `_fetch_from_web(keyword, limit)` - 网络模式

**功能**: 从网络爬取数据（当前为接口占位，返回 Mock 数据）

**说明**: 
- 当前版本返回 Mock 数据用于测试
- 后续可集成真实的 MediaCrawler 爬虫逻辑
- 保留接口，便于未来扩展

#### 1.3 `get_raw_data(mode, keyword, limit)` - 统一入口

**功能**: 工厂模式的统一数据采集接口

**参数**:
- `mode`: 采集模式 (`"local"` 或 `"web"`)
- `keyword`: 搜索关键词（web 模式需要）
- `limit`: 数量限制（web 模式需要）

**使用示例**:
```python
# 本地模式
notes = await get_raw_data(mode="local")

# 网络模式
notes = await get_raw_data(mode="web", keyword="北京故宫", limit=20)
```

---

### 2. `main.py` - 主程序

#### 2.1 新增命令行参数

```bash
--mode       # 采集模式: local 或 web（默认: local）
--keyword    # 搜索关键词（web 模式使用）
--limit      # 抓取数量（web 模式使用）
```

#### 2.2 更新后的流程

```python
async def run_pipeline(mode, keyword, limit):
    # 阶段1: 数据采集（根据 mode 调度不同数据源）
    raw_notes = await get_raw_data(mode=mode, keyword=keyword, limit=limit)
    
    # 阶段2: AI 清洗
    for raw_note in raw_notes:
        processed_note = await clean_note_content(raw_note)
        
        # 阶段3: 存储有效数据
        if processed_note.valid:
            await save_to_db(processed_note)
```

---

## 🚀 使用方法

### 方式 1: 本地模式（从文件加载）

```bash
# 默认使用 data/raw/xhs_manual_collection.json
python main.py --mode local
```

**适用场景**:
- 测试数据清洗和存储逻辑
- 处理手动采集的数据
- 避免频繁调用网络爬虫

### 方式 2: 网络模式（爬取数据）

```bash
# 从网络爬取关键词相关的笔记
python main.py --mode web --keyword "北京故宫" --limit 20
```

**适用场景**:
- 批量采集最新数据
- 扩充数据库内容
- 定期更新数据

---

## 📝 本地数据文件格式

位置: `data/raw/xhs_manual_collection.json`

### 支持的字段

#### 完整格式（所有字段都有）:
```json
{
  "url": "https://www.xiaohongshu.com/explore/xxx",
  "raw_text": "完整的笔记内容，包含标题和正文",
  "images": ["img1.jpg", "img2.jpg"],
  "source": "xhs"
}
```

#### 简化格式（分离标题和正文）:
```json
{
  "url": "https://www.xiaohongshu.com/explore/xxx",
  "title": "笔记标题",
  "desc": "笔记正文内容",
  "images": ["img1.jpg"]
}
```

#### 最简格式（只有文本）:
```json
{
  "raw_text": "所有内容放在这里"
}
```

**说明**: 爬虫模块会自动处理各种格式，统一转换为标准的 `RawNote`

---

## 🔍 数据流转示意图

```
┌─────────────────────────────────────────────────────────┐
│                    数据采集阶段                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Local Mode]              [Web Mode]                   │
│       ↓                         ↓                        │
│  JSON 文件                 MediaCrawler                  │
│       ↓                         ↓                        │
│  格式清洗                   API 调用                     │
│       ↓                         ↓                        │
│  ──────────────────────────────────                     │
│              ↓                                           │
│         List[RawNote]  ← 统一格式                       │
│              ↓                                           │
└──────────────┼──────────────────────────────────────────┘
               ↓
┌──────────────┼──────────────────────────────────────────┐
│              ↓          AI 清洗阶段                      │
├──────────────┼──────────────────────────────────────────┤
│         for each RawNote:                                │
│              ↓                                           │
│         LLM 分析                                         │
│              ↓                                           │
│      ProcessedNote (location, category, rating...)      │
│              ↓                                           │
└──────────────┼──────────────────────────────────────────┘
               ↓
┌──────────────┼──────────────────────────────────────────┐
│              ↓          向量存储阶段                      │
├──────────────┼──────────────────────────────────────────┤
│         if valid:                                        │
│              ↓                                           │
│         ChromaDB                                         │
│              ↓                                           │
│         可检索                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 🎨 设计模式说明

### 工厂模式 (Factory Pattern)

```python
# 统一接口
def get_raw_data(mode, ...):
    if mode == "local":
        return _load_local_data()
    elif mode == "web":
        return _fetch_from_web()
    else:
        raise ValueError(...)
```

**优势**:
1. ✅ 屏蔽底层实现细节
2. ✅ 易于添加新的数据源
3. ✅ 统一的返回格式
4. ✅ 便于测试和维护

---

## 🧪 测试建议

### 1. 测试本地模式

```bash
# 确保 data/raw/xhs_manual_collection.json 存在
python main.py --mode local
```

**检查点**:
- [ ] 能否正确读取 JSON 文件
- [ ] 格式转换是否正确
- [ ] 缺失字段是否有默认处理
- [ ] 日志输出是否清晰

### 2. 测试 Web 模式

```bash
python main.py --mode web --keyword "测试" --limit 3
```

**检查点**:
- [ ] Mock 数据是否返回
- [ ] 流程能否正常运行
- [ ] 后续集成真实爬虫后验证

---

## 📦 后续扩展计划

### 1. 集成真实爬虫

```python
async def _fetch_from_web(keyword, limit):
    # TODO: 调用 MediaCrawler
    from MediaCrawler import XHSCrawler
    
    crawler = XHSCrawler()
    results = await crawler.search(keyword, limit)
    
    # 转换为 RawNote 格式
    notes = [RawNote(...) for r in results]
    return notes
```

### 2. 添加更多数据源

```python
async def _fetch_from_database():
    """从数据库加载历史数据"""
    pass

async def _fetch_from_api():
    """从第三方 API 获取数据"""
    pass

# 在 get_raw_data 中添加新模式
if mode == "database":
    return await _fetch_from_database()
```

### 3. 增量更新模式

```python
async def _incremental_fetch(since_date):
    """增量抓取最新数据"""
    pass
```

---

## ❓ 常见问题

### Q1: 本地 JSON 文件格式错误怎么办？

**A**: 爬虫模块会自动处理常见格式问题：
- 缺少 URL → 生成 `unknown_local_id_N`
- 缺少文本 → 尝试拼接 title/desc
- images 不是列表 → 自动转换
- 单条数据出错 → 跳过并记录日志

### Q2: 如何添加自定义数据源？

**A**: 3 步即可：
1. 在 `crawler.py` 中添加 `_fetch_from_xxx()` 函数
2. 返回 `List[RawNote]` 格式
3. 在 `get_raw_data()` 的 if-else 中添加新模式

### Q3: Web 模式什么时候可用？

**A**: 当前返回 Mock 数据。实际使用需要：
1. 配置 MediaCrawler 环境
2. 完成登录流程
3. 在 `_fetch_from_web()` 中集成真实调用

---

## 📚 相关文档

- `modules/schemas.py` - 数据模型定义
- `modules/cleaner.py` - AI 清洗逻辑
- `modules/vector_store.py` - 向量存储实现
- `README_SEARCH.md` - RAG 检索使用说明

---

## ✅ 重构完成清单

- [x] 实现 `_load_local_data()` 函数
- [x] 实现格式清洗逻辑（URL/文本/图片处理）
- [x] 实现 `_fetch_from_web()` 接口占位
- [x] 实现 `get_raw_data()` 统一入口
- [x] 更新 `main.py` 添加 `--mode` 参数
- [x] 更新 `run_pipeline()` 调用逻辑
- [x] 添加详细注释和日志
- [x] 编写使用文档

---

**🎉 重构完成！现在可以使用新的多模式数据采集系统了。**
