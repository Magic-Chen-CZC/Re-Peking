# 仓库指南

## 项目结构与模块组织
- `bakend/`：FastAPI + LangGraph 后端。核心逻辑在 `bakend/app/`（agents、services、graph），本地数据在 `bakend/storage/`。
- `miniprogram/`：微信小程序前端（pages、components、utils、image）。
- `BeijingGuideData/`：数据采集、审核与向量索引流水线（脚本在该目录根部，文档在 `BeijingGuideData/README/`）。
- `*/venv/`：本地虚拟环境目录，不要编辑或提交。

## 构建、测试与开发命令
后端（`bakend/`）：
- `pip install -r requirements.txt` 安装依赖。
- `python main.py` 启动 API 服务，默认监听 `0.0.0.0:8000`。

数据流水线（`BeijingGuideData/`）：
- `pip install -r requirements.txt` 安装依赖。
- `python fetch_data.py` 采集数据并生成审核用 Excel。
- `python build_db.py --file data/review/pending_YYYYMMDD_HHMMSS.xlsx` 导入审核后的数据。
- `python search.py` 交互式检索向量库。

小程序（`miniprogram/`）：
- 用微信开发者工具打开 `miniprogram/`，配置文件为 `miniprogram/project.config.json`。

## 编码风格与命名规范
- Python：延续现有风格（4 空格缩进，snake_case）。
- 小程序：`*.json`、`*.wxml`、`*.wxss` 使用 2 空格缩进；页面目录为 `pages/<feature>/`。
- 脚本文件名保持小写加下划线（如 `debug_api_coords.py`）。

## 测试指南
- 当前未定义统一测试框架，使用现有脚本进行验证：
  - 后端工具：`bakend/debug_api_coords.py`、`bakend/quick_verify_poi.sh`。
  - 小程序脚本：`miniprogram/test_community_detail.sh`、`miniprogram/verify_detail_fix.sh`。
- 修改 UI 后需在微信开发者工具中验证，并保留前后对比截图。

## 提交与 PR 规范
- 当前工作区无 Git 历史可参考，提交规范未定义。
- 建议使用清晰的祈使句提交信息（如“新增路线异常处理”）。
- PR 需包含简要说明、测试记录，小程序改动需附截图，并关联相关 Issue（如有）。

## 安全与配置提示
- API Key 放在 `.env` 中（参考 `bakend/.env` 与 `BeijingGuideData/.env` 用法），严禁提交密钥。
- 后端依赖 DashScope/Qwen 与地图服务密钥，部署前核对 `bakend/app/services/map_service.py` 环境变量。

## 沟通与执行规则
- 以后都用中文沟通，输出尽量简洁、先给结论再给步骤。
- 所有写文件/执行命令前先说明要做什么，并等确认（除非已明确允许自动执行）。
- 我是个小白，每次尽量详细的给我解释代码背后的原理，以及在代码中添加注释方便我阅读。