# 配置构建与测试工作台（PDF Theme Workbench）

本工作台为现有 **BeijingGuideData** 数据处理项目提供一个「**配置构建 + 在线测试**」的 Web 界面。

- ✅ **零侵入**：不修改 `modules/schemas.py`、`modules/domain_config.py` 等核心业务与配置文件
- ✅ **独立存储**：用户自定义配置以 JSON 形式保存到 `user_extensions/json_configs/`
- ✅ **动态加载**：运行时将 JSON 配置动态转换为 Pydantic Schema + strategy（DOMAIN_CONFIG 兼容结构）
- ✅ **核心逻辑复用**：测试运行直接复用 `modules/processors/pdf_processor.py` 的处理流程

> 当前阶段：**仅支持 PDF 工作台**（上传 PDF → 使用自定义配置抽取 → 返回 JSON 结果）。

---

## 目录结构

- `modules/dynamic_loader.py`
  - 动态加载器：读取用户 JSON 配置，生成 Pydantic 模型（继承 `BaseContent`），并组装成 strategy dict。

- `api.py`（FastAPI）
  - 后端 API：保存配置、上传文件并运行测试。

- `web_app.py`（Streamlit）
  - 前端工作台：左侧编辑配置，右侧上传 PDF 运行测试。

- `user_extensions/json_configs/`
  - 用户配置存储目录：`{key}.json`

---

## 安装依赖

本工作台依赖已追加到 `BeijingGuideData/requirements.txt`：

- `fastapi`
- `uvicorn`
- `python-multipart`
- `streamlit`
- `requests`

请在 `BeijingGuideData` 目录下安装依赖：

```bash
pip install -r requirements.txt
```

---

## 启动方式

### 1) 启动后端 API

在 `BeijingGuideData` 目录下运行：

```bash
uvicorn api:app --reload --port 8000
```

启动成功后，你将看到类似输出：

- `Uvicorn running on http://127.0.0.1:8000`

### 2) 启动前端 Streamlit

在 **另一个终端**，仍在 `BeijingGuideData` 目录下运行：

```bash
streamlit run web_app.py
```

默认会打开浏览器：

- `http://localhost:8501`

---

## 工作台使用说明（左侧定义 / 右侧测试）

### 左侧：配置定义区

- **Key（文件名）**：保存为 `user_extensions/json_configs/{key}.json`
- **Description**：策略描述
- **Prompt**：给 LLM 的抽取说明
- **Chunking**：切分参数
- **Schema 构建器**：用表格编辑字段列表

点击 **「💾 保存配置」** 会调用：

- `POST /user/config/save`

### 右侧：测试预览区

- 上传 PDF
- 点击 **「🚀 保存并运行测试」**
  - 先保存配置（确保后端最新）
  - 再调用测试接口运行抽取

调用接口：

- `POST /user/test/run`

返回：

```json
{
  "ok": true,
  "count": 3,
  "results": [ ... ]
}
```

---

## 用户配置 JSON 格式

保存到：`user_extensions/json_configs/{key}.json`

示例：

```json
{
  "key": "my_theme",
  "description": "示例主题",
  "prompt": "...",
  "chunking": {
    "mode": "sentence",
    "chunk_size": 800,
    "overlap": 100,
    "min_length": 50
  },
  "fields": [
    {"name": "location", "type": "string", "description": "地点", "required": true},
    {"name": "category", "type": "string", "description": "类别", "required": true},
    {"name": "valid", "type": "boolean", "description": "是否有效", "required": true}
  ]
}
```

字段类型支持：

- `string`
- `integer` / `int`
- `boolean` / `bool`
- `float`

---

## API 接口说明

### POST `/user/config/save`

- Body：JSON（见上方格式）
- 行为：覆盖写入 `user_extensions/json_configs/{key}.json`

返回：

```json
{"ok": true, "path": ".../user_extensions/json_configs/my_theme.json"}
```

### POST `/user/test/run`

- Form-data：
  - `config_key`: string
  - `file`: UploadFile（PDF）

返回：

```json
{"ok": true, "count": 2, "results": [ ... ]}
```

---

## 常见问题

### 1) Streamlit 报 "无法解析导入 streamlit"

这是因为当前 Python 环境还没安装依赖。请确认已执行：

```bash
pip install -r requirements.txt
```

### 2) CORS 跨域问题

`api.py` 已启用宽松 CORS（`allow_origins=["*"]`），默认可从 Streamlit 访问。

---

## 设计说明（最小侵入）

- 未修改核心 `modules/domain_config.py` / `modules/schemas.py`
- 仅对 `PDFProcessor.process_pdf()` 增加 `custom_strategy` 注入参数：
  - 不影响既有 `fetch_data.py` 与原有调用
  - 新工作台通过 `custom_strategy` 直接复用核心 PDF 流程

---

## 未来扩展

- 支持 Web URL / XHS 等来源
- 支持更多 chunking 模式（markdown/semantic 等）
- 将策略运行日志/中间 chunk 输出在工作台右侧可视化

source venv/bin/activate
./venv/bin/python3 -m pip install -r requirements.txt
./venv/bin/python3 -m uvicorn api:app --reload --port 8000
./venv/bin/python3 -m streamlit run web_app.py