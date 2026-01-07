"""web_app.py

Streamlit Workbench 前端：左侧编辑配置，右侧上传文件测试。

启动方式（示例）：streamlit run web_app.py
"""

from __future__ import annotations

import json
import os
import time
from io import BytesIO
from typing import Any, Dict, List

import pandas as pd
import requests
import streamlit as st

# 兼容：未配置 secrets.toml 时，st.secrets 会抛 StreamlitSecretNotFoundError
# 优先 secrets -> 环境变量 -> 默认值
try:
    API_BASE = st.secrets.get("API_BASE", None)
except Exception:
    API_BASE = None

API_BASE = API_BASE or os.getenv("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="Theme Workbench", layout="wide")

st.title("🛠️ 自定义主题构建工作台 (Theme Workbench)")

left, right = st.columns(2, gap="large")


# BaseContent 通用字段：工作台内置（展示为只读），用户仅需添加业务字段。
# 注意：后端 dynamic_loader 会把 BaseContent 的字段合并进最终 schema。
BASE_FIELDS: List[Dict[str, Any]] = [
    {"name": "id", "type": "string", "description": "唯一标识，建议：{source_type}_{unique_id}", "required": False},
    {"name": "text_content", "type": "string", "description": "用于向量化的核心文本内容", "required": False},
    {"name": "source_type", "type": "string", "description": "数据源类型，如 xhs / pdf_legend / pdf_architecture", "required": False},
    {"name": "summary", "type": "string", "description": "内容摘要（一句话总结）", "required": False},
    {"name": "metadata", "type": "string", "description": "额外元数据（JSON 字符串/对象，通常由处理器填充）", "required": False},
]


def _is_base_field(name: Any) -> bool:
    return isinstance(name, str) and name in {f["name"] for f in BASE_FIELDS}


def _user_fields_only(fields: Any) -> List[Dict[str, Any]]:
    """将 cfg["fields"] 过滤成仅用户自定义字段（排除 BaseContent 通用字段）。"""
    if not isinstance(fields, list):
        return []
    out: List[Dict[str, Any]] = []
    for f in fields:
        if not isinstance(f, dict):
            continue
        name = f.get("name")
        if _is_base_field(name):
            continue
        out.append(f)
    return out


def _default_config() -> Dict[str, Any]:
    return {
        "key": "my_theme",
        "description": "",
        "prompt": "",
        "chunking": {"mode": "sentence", "chunk_size": 800, "overlap": 100, "min_length": 50},
        # 仅保存用户字段；BaseContent 通用字段由工作台内置展示。
        "fields": [
            {"name": "location", "type": "string", "description": "地点", "required": True},
            {"name": "valid", "type": "boolean", "description": "是否有效", "required": True},
        ],
    }


with left:
    st.subheader("配置定义区")

    if "cfg" not in st.session_state:
        st.session_state.cfg = _default_config()

    cfg: Dict[str, Any] = st.session_state.cfg

    cfg["key"] = st.text_input("Key (文件名)", value=cfg.get("key", ""))
    cfg["description"] = st.text_input("Description", value=cfg.get("description", ""))

    cfg["prompt"] = st.text_area("Prompt", value=cfg.get("prompt", ""), height=360)

    st.markdown("#### Chunking")
    c = cfg.get("chunking", {})
    c["mode"] = st.selectbox("mode", options=["none", "sentence"], index=["none", "sentence"].index(c.get("mode", "sentence")))
    c["chunk_size"] = st.number_input("chunk_size", min_value=0, value=int(c.get("chunk_size", 800)))
    c["overlap"] = st.number_input("overlap", min_value=0, value=int(c.get("overlap", 100)))
    c["min_length"] = st.number_input("min_length", min_value=0, value=int(c.get("min_length", 50)))
    cfg["chunking"] = c

    st.markdown("#### Schema 构建器")

    # 1) 通用字段展示（只读）
    st.caption("通用字段（自动包含，无法编辑）")
    st.dataframe(pd.DataFrame(BASE_FIELDS), use_container_width=True, hide_index=True)

    # 2) 用户字段编辑（可增删改）
    st.caption("业务字段（你需要填写/维护）")
    user_df = pd.DataFrame(_user_fields_only(cfg.get("fields", [])))
    if user_df.empty:
        user_df = pd.DataFrame([{"name": "location", "type": "string", "description": "地点", "required": True}])

    edited = st.data_editor(
        user_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "name": st.column_config.TextColumn("Field Name"),
            "type": st.column_config.SelectboxColumn("Type", options=["string", "integer", "boolean", "float"]),
            "description": st.column_config.TextColumn("Description"),
            "required": st.column_config.CheckboxColumn("Required"),
        },
    )
    cfg["fields"] = edited.to_dict(orient="records")

    if st.button("💾 保存配置"):
        payload = dict(cfg)
        # 只保存用户字段，避免把通用字段写入 JSON 配置里（保持更干净）
        payload["fields"] = _user_fields_only(payload.get("fields"))
        r = requests.post(f"{API_BASE}/user/config/save", json=payload, timeout=60)
        if r.ok:
            st.success("已保存")
        else:
            st.error(r.text)


with right:
    st.subheader("测试预览区")

    up = st.file_uploader("上传文件 (PDF)", type=["pdf"])

    if st.button("🚀 保存并运行测试"):
        payload = dict(cfg)
        payload["fields"] = _user_fields_only(payload.get("fields"))

        # 先保存配置
        r1 = requests.post(f"{API_BASE}/user/config/save", json=payload, timeout=60)
        if not r1.ok:
            st.error(f"保存失败: {r1.text}")
        elif up is None:
            st.error("请先上传 PDF")
        else:
            # 提交任务
            files = {"file": (up.name, up.getvalue(), "application/pdf")}
            data = {"config_key": payload["key"]}
            r2 = requests.post(f"{API_BASE}/user/test/run", files=files, data=data, timeout=60)
            if not r2.ok:
                st.error(r2.text)
            else:
                task_id = r2.json().get("task_id")
                if not task_id:
                    st.error(f"后端未返回 task_id: {r2.text}")
                else:
                    progress = st.progress(0)
                    status_box = st.empty()

                    # 轮询进度
                    result = None
                    for _ in range(300):  # 最长约 300s
                        s = requests.get(f"{API_BASE}/user/test/status/{task_id}", timeout=30)
                        if not s.ok:
                            status_box.error(s.text)
                            break
                        js = s.json()
                        pct = int(js.get("progress", 0))
                        msg = js.get("message", "")
                        stt = js.get("status", "pending")
                        progress.progress(min(max(pct, 0), 100))
                        status_box.info(f"状态: {stt} | {pct}% | {msg}")

                        if stt == "done":
                            result = js.get("result")
                            break
                        if stt == "error":
                            status_box.error(f"处理失败: {msg}")
                            break
                        time.sleep(1)

                    if result and isinstance(result, dict) and result.get("ok"):
                        st.success(f"完成，共 {result.get('count', 0)} 条")
                        st.json(result)

                        # 导出 Excel
                        rows = result.get("results", []) or []
                        try:
                            df_out = pd.json_normalize(rows)
                        except Exception:
                            df_out = pd.DataFrame(rows)

                        bio = BytesIO()
                        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
                            df_out.to_excel(writer, index=False, sheet_name="results")
                        st.download_button(
                            label="⬇️ 下载结果 Excel",
                            data=bio.getvalue(),
                            file_name=f"{payload['key']}_results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )

    st.markdown("---")
    with st.expander("当前配置 JSON"):
        st.code(json.dumps(cfg, ensure_ascii=False, indent=2), language="json")
