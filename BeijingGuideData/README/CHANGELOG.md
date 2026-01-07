# 变更日志 (Changelog)

## [2.0.0] - 2025-12-11

### 🎉 重大重构 - 三脚本分离架构

#### 新增 (Added)

**核心脚本**：
- `fetch_data.py` - 数据采集脚本，支持交互式菜单和命令行模式
- `build_db.py` - 数据入库脚本，从 Excel 批量导入向量数据库
- `modules/reviewer.py` - Excel 审核模块，支持导出和导入

**文档**：
- `README.md` - 项目主页，快速了解项目
- `README/QUICKSTART.md` - 5分钟快速开始指南
- `README/WORKFLOW_GUIDE.md` - 完整工作流程说明
- `README/REFACTOR_SUMMARY.md` - 重构总结文档

**目录**：
- `data/review/` - Excel 审核文件存放目录

**依赖**：
- `openpyxl==3.1.5` - Excel 文件读写支持

#### 变更 (Changed)

- `search.py` - 更新文档字符串，添加使用说明
- `requirements.txt` - 添加 openpyxl 依赖

#### 废弃 (Deprecated)

- `main.py` - 重命名为 `main_legacy.py.bak`，不再使用

#### 功能亮点

✨ **交互式菜单模式**
- 无需记忆命令行参数
- 自动扫描 `data/raw/` 目录
- 友好的用户界面
- 文件大小显示
- 支持 Ctrl+C 中断

✨ **人工审核环节**
- Excel 可视化编辑
- 灵活的数据筛选（valid 字段）
- 质量控制
- 批量修改

✨ **职责清晰**
- `fetch_data.py`: 负责采集和清洗
- `build_db.py`: 负责入库
- `search.py`: 负责检索

### 工作流变化

**旧工作流**：
```
原始数据 → main.py → 直接入库 → 检索
```

**新工作流**：
```
原始数据 → fetch_data.py → Excel → 人工审核 → build_db.py → 向量库 → search.py
```

### 使用示例

**交互式采集**：
```bash
python fetch_data.py
```

**命令行采集**：
```bash
python fetch_data.py --source pdf --file data/raw/legends.pdf --doc_type legend
```

**数据入库**：
```bash
python build_db.py --file data/review/pending_20231211_153045.xlsx
```

**数据检索**：
```bash
python search.py
```

---

## [1.0.0] - 2025-12-09

### 初始版本

- 实现 `main.py` 单一入口
- 支持 XHS 和 PDF 数据源
- ChromaDB 向量存储
- LlamaIndex 检索
- Qwen LLM 集成

---

## 版本说明

- **主版本号 (Major)**: 重大架构变更
- **次版本号 (Minor)**: 功能新增
- **修订号 (Patch)**: Bug 修复

当前版本：**2.0.0**
