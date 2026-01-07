# BeijingGuideData Workbench（配置构建 + 在线测试）

本 README 用于说明 **BeijingGuideData** 的“配置构建与测试工作台”代码结构，并提供一份 **Graph（业务流程）结构图** 方便理解前后端协作与数据流。

> 入口：`api.py`（FastAPI 后端） + `web_app.py`（Streamlit 前端）

---

## 1. 代码结构概览

> 以工作台相关代码为主（不展开 venv / data 大文件夹）。

```text
BeijingGuideData/
├── api.py                      # FastAPI：保存配置、运行测试（任务/进度）
├── web_app.py                  # Streamlit：配置编辑 + 上传 PDF + 查看进度 + 下载 Excel
├── requirements_workbench.txt  # 工作台最小依赖（建议用于快速安装）
├── user_extensions/
│   └── json_configs/           # 工作台保存的用户配置：{key}.json
├── modules/
│   ├── dynamic_loader.py        # 将 user JSON 配置动态转换为 strategy（schema/prompt/chunking）
│   ├── processors/
│   │   └── pdf_processor.py     # 复用现有 PDF 抽取主流程（LLM 清洗/抽取）
│   ├── crawlers/
│   │   └── pdf_loader.py        # PDF 加载/OCR/导出 Markdown（被 pdf_processor 调用）
│   └── schemas.py              # BaseContent 等数据模型（工作台动态 schema 继承它）
└── README_WORKBENCH.md          # 旧版说明（偏操作手册）
```

---

## 2. Graph（工作台业务流程）结构图

### 2.1 前后端交互 Graph（推荐）

```mermaid
flowchart TD
  U[用户] -->|编辑配置| ST[Streamlit: web_app.py]
  ST -->|POST /user/config/save| API[FastAPI: api.py]
  ST -->|上传PDF + POST /user/test/run| API
  API -->|返回 task_id| ST
  ST -->|轮询 GET /user/test/status/{task_id}| API

  API -->|读取 user_extensions/json_configs/{key}.json| CFG[用户配置 JSON]
  API --> DL[modules/dynamic_loader.py\nload_strategy_from_json_dict]
  DL --> STR[strategy: schema + prompt + chunking]

  API --> PP[modules/processors/pdf_processor.py\nPDFProcessor.process_pdf]
  PP --> PL[modules/crawlers/pdf_loader.py\nload_pdf_content/save_as_markdown]
  PP --> LLM[modules/qwen_llm.py / LLM 调用]
  PP --> RES[results: List[BaseContent]]

  API -->|status=done + result| ST
  ST -->|渲染 JSON| UI[结果展示]
  ST -->|导出 xlsx| EXCEL[Excel 下载]
```

### 2.2 后端内部处理 Graph（粗粒度）

```mermaid
flowchart LR
  A[接收上传 PDF] --> B[保存到临时文件]
  B --> C[加载用户 config_key -> JSON]
  C --> D[dynamic_loader: 构建 schema/strategy]
  D --> E[pdf_processor: 解析PDF -> 切分chunk -> LLM抽取]
  E --> F[聚合 results -> model_dump]
  F --> G[返回给前端/生成 Excel]
```

---

## 3. 关键模块职责（简述）

- `web_app.py`
  - 左侧：配置（key/description/prompt/chunking/fields）
  - 右侧：上传 PDF、显示后端进度、展示结构化结果
  - 结果导出：将 `results` 扁平化写入 xlsx，并提供下载

- `api.py`
  - `/user/config/save`：保存配置 JSON
  - `/user/test/run`：提交任务，返回 `task_id`
  - `/user/test/status/{task_id}`：查询任务状态/进度/结果

- `modules/dynamic_loader.py`
  - 将用户 JSON 配置转换成运行时 `strategy`（兼容 DOMAIN_CONFIG 结构）

- `modules/processors/pdf_processor.py`
  - 复用 PDF 主处理流程：加载 → 切分 → LLM 抽取 → 结构化输出

---

## 4. 备注

- Mermaid 图在 GitHub 上可以直接渲染；如果你的渲染器不支持，可安装 Mermaid 相关 VS Code 插件或使用在线 Mermaid 编辑器预览。
- 目前进度条为“阶段型进度”（受 `process_pdf()` 同步执行限制）。若需要按 chunk 精细进度，需要在 `PDFProcessor` 增加回调。
