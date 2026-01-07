"""api.py。 前端页面的API

Web Workbench 后端：
- 保存用户 JSON 配置到 user_extensions/json_configs
- 使用动态配置运行测试（当前支持 PDF）

启动方式（示例）：uvicorn api:app --reload --port 8000
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from modules.dynamic_loader import load_strategy_from_json_dict
from modules.processors.pdf_processor import PDFProcessor


BASE_DIR = Path(__file__).resolve().parent
USER_CONFIG_DIR = BASE_DIR / "user_extensions" / "json_configs"
USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="BeijingGuideData Theme Workbench API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存任务状态（简单版：单机进程内有效；重启服务会丢失）
_TASKS: Dict[str, Dict[str, Any]] = {}


def _set_task(task_id: str, **kwargs: Any) -> None:
    t = _TASKS.setdefault(task_id, {})
    t.update(kwargs)
    t["updated_at"] = time.time()


def _run_pdf_task(task_id: str, tmp_path: Path, strategy: Dict[str, Any]) -> None:
    try:
        _set_task(task_id, status="running", progress=5, message="初始化处理器")
        processor = PDFProcessor()

        # 粗粒度进度：process_pdf 内部目前是同步执行，这里只能做阶段进度
        _set_task(task_id, progress=15, message="开始解析与抽取")
        results = processor.process_pdf(
            str(tmp_path),
            doc_type="__dynamic__",
            custom_strategy=strategy,
        )

        data = [r.model_dump() for r in results]
        _set_task(task_id, status="done", progress=100, message="完成", result={"ok": True, "count": len(data), "results": data})
    except Exception as e:
        _set_task(task_id, status="error", progress=100, message=str(e))
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


@app.post("/user/config/save")
async def save_user_config(payload: Dict[str, Any]):
    """保存用户配置 JSON（覆盖写入）。"""
    key = payload.get("key")
    if not key or not isinstance(key, str):
        return JSONResponse(status_code=400, content={"error": "Missing or invalid 'key'"})

    path = USER_CONFIG_DIR / f"{key}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "path": str(path)}


@app.get("/user/test/status/{task_id}")
async def get_test_status(task_id: str):
    t = _TASKS.get(task_id)
    if not t:
        return JSONResponse(status_code=404, content={"error": "task not found"})
    return {
        "ok": True,
        "task_id": task_id,
        "status": t.get("status", "pending"),
        "progress": t.get("progress", 0),
        "message": t.get("message", ""),
        "result": t.get("result"),
    }


@app.post("/user/test/run")
async def run_user_test(
    file: UploadFile = File(...),
    config_key: str = Form(...),
):
    """使用指定用户配置处理上传文件（当前：PDF）。

    该接口为异步任务模式：立即返回 task_id，前端轮询 /user/test/status/{task_id} 获取进度与结果。
    """

    config_path = USER_CONFIG_DIR / f"{config_key}.json"
    if not config_path.exists():
        return JSONResponse(status_code=404, content={"error": f"Config not found: {config_key}"})

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    strategy = load_strategy_from_json_dict(raw)

    suffix = Path(file.filename or "upload").suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(await file.read())

    task_id = uuid.uuid4().hex
    _set_task(task_id, status="pending", progress=0, message="已接收任务")

    th = threading.Thread(target=_run_pdf_task, args=(task_id, tmp_path, strategy), daemon=True)
    th.start()

    return {"ok": True, "task_id": task_id}
