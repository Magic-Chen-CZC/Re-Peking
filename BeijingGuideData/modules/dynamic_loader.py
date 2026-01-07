"""modules.dynamic_loader

动态加载器：
- 从用户 JSON 配置动态生成 Pydantic Schema（继承 BaseContent）
- 组装为与 DOMAIN_CONFIG 同结构的 strategy dict

注意：此模块设计为"零侵入"，不修改既有 schemas.py / domain_config.py。
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Tuple, Type

from pydantic import BaseModel, Field, create_model

from modules.schemas import BaseContent


_PYDANTIC_TYPE_MAP: Dict[str, Any] = {
    "string": str,
    "integer": int,
    "int": int,
    "boolean": bool,
    "bool": bool,
    "float": float,
}


class DynamicFieldDef(BaseModel):
    name: str
    type: Literal["string", "integer", "int", "boolean", "bool", "float"]
    description: str = ""
    required: bool = True


class DynamicChunkingDef(BaseModel):
    mode: str = "sentence"
    chunk_size: int = 512
    overlap: int = 64
    min_length: int = 0


class DynamicConfig(BaseModel):
    key: str
    description: str = ""
    prompt: str
    fields: List[DynamicFieldDef]
    chunking: DynamicChunkingDef = Field(default_factory=DynamicChunkingDef)


def _build_dynamic_schema(config: DynamicConfig) -> Type[BaseContent]:
    """根据 fields 动态构建 Pydantic Model。

    - 继承 BaseContent
    - 自动提供 source_type 默认值为 "user:{key}"
    - 默认追加 valid: bool 字段（如果用户未定义）
    """

    field_defs: Dict[str, Tuple[Any, Any]] = {
        # BaseContent 必需字段：给一个合理默认，避免 LLM 不返回导致全量 ValidationError
        # 但仍建议在 prompt 中要求 LLM 填写。
        "id": (str, Field(default="", description="唯一标识（如为空将由处理器补齐）")),
        "text_content": (str, Field(default="", description="用于向量化的核心原文")),
        "summary": (str, Field(default="", description="摘要")),
        "metadata": (dict, Field(default_factory=dict, description="元数据")),
        "source_type": (str, Field(default=f"user:{config.key}", description="数据源类型")),
    }

    for f in config.fields:
        py_t = _PYDANTIC_TYPE_MAP.get(f.type)
        if py_t is None:
            raise ValueError(f"Unsupported field type: {f.type}")

        default = ... if f.required else None
        field_defs[f.name] = (py_t, Field(default=default, description=f.description))

    if "valid" not in field_defs:
        field_defs["valid"] = (bool, Field(default=True, description="是否有效（LLM 判断）"))

    # create_model 会把 BaseContent 的字段也带上；这里我们显式声明以便默认值更友好
    DynamicModel = create_model(
        f"User_{config.key}_Model",
        __base__=BaseContent,
        **{k: v for k, v in field_defs.items() if k not in BaseContent.model_fields},
    )

    # 覆盖 BaseContent 字段默认值（Pydantic v2 通过 model_fields 配置较麻烦；这里保持最小可用）
    return DynamicModel  # type: ignore[return-value]


def load_strategy_from_json_dict(raw: Dict[str, Any]) -> Dict[str, Any]:
    """从 JSON dict 构建运行时 strategy（DOMAIN_CONFIG 兼容结构）。"""
    config = DynamicConfig.model_validate(raw)
    schema_cls = _build_dynamic_schema(config)

    return {
        "description": config.description or f"User config: {config.key}",
        "schema": schema_cls,
        "prompt": config.prompt,
        "chunking": config.chunking.model_dump(),
        # 可扩展：未来可加 processors/crawlers 选择等
    }
