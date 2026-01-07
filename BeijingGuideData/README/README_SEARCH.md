# 北京导览 AI - RAG 检索系统使用指南

## 系统架构

本系统现已全面使用**通义千问（Qwen）**模型：

- 🤖 **LLM 模型**: `qwen-plus` - 用于 RAG 问答生成
- 🔤 **Embedding 模型**: `text-embedding-v4` - 用于向量嵌入
- 💾 **向量数据库**: ChromaDB
- 🔍 **检索框架**: LlamaIndex

## 配置说明

### 环境变量（.env）

```properties
# 必填配置
DEEPSEEK_API_KEY=sk-xxx          # DeepSeek API（用于数据清洗）
DASHSCOPE_API_KEY=sk-xxx         # 通义千问 API（用于嵌入和 RAG）

# 可选配置
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus              # LLM 模型
EMBEDDING_MODEL=text-embedding-v4 # 嵌入模型
```

## 使用方法

### 1. 数据采集与存储

运行主程序采集和清洗数据：

```bash
# 采集 10 条数据（默认）
python main.py

# 自定义关键词和数量
python main.py --keyword "北京美食" --limit 5
```

**流程：**
1. 🕷️ 采集数据（模拟爬虫）
2. 🤖 AI 清洗（DeepSeek）
3. 🔤 向量化（Qwen Embedding）
4. 💾 存储（ChromaDB）

### 2. RAG 检索查询

#### 命令行模式（单次查询）

```bash
python search.py "北京有哪些影视拍摄地推荐？"
```

#### 交互式模式（持续对话）

```bash
python search.py
```

进入交互式界面后：
- 输入查询内容，按回车查询
- 输入 `quit`、`exit` 或 `q` 退出

### 3. 检索结果示例

```
============================================================
📝 检索结果:
============================================================

推荐北京东四六条附近的《邪不压正》电影同款屋顶拍摄地，
此处是影视打卡热门地点，可拍摄李天然同款机位，夕阳景色尤为绝美。

============================================================
📚 来源文档:
============================================================

【来源 1】
相似度: 0.4871
地点: 东四六条附近
分类: 影视打卡
推荐指数: 4/5
有效: 是
URL: https://www.xiaohongshu.com/explore/xxx

摘要:
打卡电影《邪不压正》的屋顶拍摄地，位于东四六条附近...
```

## 技术特点

### RAG 工作流程

1. **用户查询** → Qwen Embedding 向量化
2. **向量检索** → ChromaDB 语义相似度匹配
3. **上下文增强** → 检索相关文档
4. **答案生成** → Qwen LLM 综合回答

### 模型选择优势

- ✅ **全中文优化**：通义千问针对中文场景优化
- ✅ **成本优化**：相比 OpenAI 更经济
- ✅ **速度快**：国内访问无需翻墙
- ✅ **统一生态**：Embedding + LLM 同一厂商，兼容性好

## 常见问题

### Q: 如何获取通义千问 API Key？

访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/) 注册并获取 API Key。

### Q: 检索结果为空怎么办？

1. 确认数据库中有数据：`ls data/chroma_db`
2. 运行 `python main.py --limit 5` 添加测试数据
3. 调整查询关键词，使用更具体的描述

### Q: 如何调整检索数量？

修改 `search.py` 中的 `similarity_top_k` 参数：

```python
query_engine = index.as_query_engine(
    similarity_top_k=5,  # 修改这里
    response_mode="compact"
)
```

### Q: 想使用其他 Qwen 模型？

在 `.env` 中修改：

```properties
QWEN_MODEL=qwen-turbo        # 更快更便宜
QWEN_MODEL=qwen-max          # 更强大
QWEN_MODEL=qwen-plus         # 平衡（默认）
```

## 项目结构

```
BeijingGuideAI/
├── main.py              # 数据采集主程序
├── search.py            # RAG 检索脚本
├── config.py            # 配置管理
├── modules/
│   ├── crawler.py       # 爬虫模块
│   ├── cleaner.py       # AI 清洗（DeepSeek）
│   ├── vector_store.py  # 向量存储（Qwen Embedding）
│   ├── qwen_embedding.py # Qwen 嵌入模型
│   ├── qwen_llm.py      # Qwen LLM 模型
│   └── schemas.py       # 数据模型
├── utils/
│   └── logger.py        # 日志工具
└── data/
    └── chroma_db/       # 向量数据库
```

## 下一步

- [ ] 接入真实爬虫（MediaCrawler）
- [ ] 优化检索策略（混合检索、重排序）
- [ ] 添加对话历史记忆
- [ ] Web UI 界面
- [ ] 地理位置过滤
