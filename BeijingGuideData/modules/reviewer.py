"""
数据审核模块 - 动态 Excel 导入导出

本模块提供 Excel 导入导出功能，用于人工审核数据质量：
1. export_to_excel: 将处理后的数据导出到 Excel 供人工审核
2. load_from_excel: 从审核后的 Excel 中读取数据并转换为 BaseContent 对象

核心特性：
- 动态字段映射：自动根据 Schema 定义导出/导入字段
- metadata 扁平化：将嵌套的 metadata 字典展开为一级列
- 自动适配：Schema 新增字段时，Excel 自动同步，无需修改代码

工作流程：
1. 采集+处理后，调用 export_to_excel 生成 Excel 文件
2. 人工在 Excel 中审核、修改、删除不合格数据
3. 调用 load_from_excel 读取审核后的数据（自动识别字段）
4. 将审核通过的数据批量存入向量数据库
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Type

import pandas as pd
from pydantic import ValidationError, BaseModel

from modules.schemas import BaseContent, XHSNote, StoryClip, ArchitectureDoc
from utils.logger import logger


# 类型映射：从字符串到 Pydantic 类
CONTENT_TYPE_MAP = {
    "XHSNote": XHSNote,
    "StoryClip": StoryClip,
    "ArchitectureDoc": ArchitectureDoc,
}


# ============================================================================
# 辅助函数：metadata 扁平化处理
# ============================================================================

def _flatten_metadata(item_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    将 metadata 字段扁平化为一级字段
    
    Args:
        item_dict: 包含 metadata 的字典
    
    Returns:
        扁平化后的字典
    
    Example:
        输入: {"id": "xxx", "metadata": {"author": "张三", "year": 2024}}
        输出: {"id": "xxx", "author": "张三", "year": 2024", "_has_metadata": true}
    """
    if "metadata" not in item_dict or not isinstance(item_dict["metadata"], dict):
        return item_dict
    
    flattened = item_dict.copy()
    metadata = flattened.pop("metadata")
    
    # 将 metadata 中的所有键值对提升为一级字段
    for key, value in metadata.items():
        # 避免覆盖已有字段，使用 metadata_ 前缀
        safe_key = f"metadata_{key}" if key in flattened else key
        flattened[safe_key] = value
    
    # 标记是否有 metadata（用于导入时重建）
    flattened["_has_metadata"] = True
    
    return flattened


def _unflatten_metadata(row_dict: Dict[str, Any], schema_fields: set) -> Dict[str, Any]:
    """
    将扁平化的字段重新打包回 metadata
    
    Args:
        row_dict: Excel 行数据（扁平化的）
        schema_fields: Schema 定义的标准字段集合
    
    Returns:
        包含 metadata 的字典
    
    Example:
        输入: {"id": "xxx", "author": "张三", "year": 2024, "_has_metadata": true}
        输出: {"id": "xxx", "metadata": {"author": "张三", "year": 2024}}
    """
    unflattened = {}
    metadata = {}
    
    for key, value in row_dict.items():
        # 跳过辅助字段
        if key in ["_has_metadata", "_content_type"]:
            continue
        
        # 标准字段直接保留
        if key in schema_fields:
            unflattened[key] = value
        # 带 metadata_ 前缀的字段
        elif key.startswith("metadata_"):
            original_key = key.replace("metadata_", "", 1)
            metadata[original_key] = value
        # 其他非标准字段都打包进 metadata
        else:
            metadata[key] = value
    
    # 如果有 metadata 内容，添加到结果中
    if metadata:
        unflattened["metadata"] = metadata
    
    return unflattened


def export_to_excel(
    content_list: List[BaseContent],
    output_dir: str = "data/review",
    filename: Optional[str] = None
) -> str:
    """
    将处理后的内容导出到 Excel 供人工审核（动态字段映射）
    
    特性：
    - 自动根据 Schema 定义导出所有字段
    - metadata 自动扁平化为一级列
    - Schema 新增字段时，Excel 自动同步
    
    Args:
        content_list: 内容列表（XHSNote、StoryClip、ArchitectureDoc 等）
        output_dir: 输出目录，默认为 data/review
        filename: 文件名，如果不指定则自动生成（pending_{timestamp}.xlsx）
    
    Returns:
        导出的 Excel 文件路径
    """
    if not content_list:
        logger.warning("没有数据可导出")
        return ""
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pending_{timestamp}.xlsx"
    
    output_path = os.path.join(output_dir, filename)
    
    try:
        # 将 Pydantic 对象转换为字典列表（扁平化 metadata）
        data_list = []
        for item in content_list:
            item_dict = item.model_dump()
            # 添加类型标识，用于后续反序列化
            item_dict["_content_type"] = type(item).__name__
            # 扁平化 metadata
            item_dict = _flatten_metadata(item_dict)
            data_list.append(item_dict)
        
        # 转换为 DataFrame
        df = pd.DataFrame(data_list)
        
        # 动态调整列顺序，将重要字段放在前面
        priority_cols = ["_content_type", "id", "summary", "valid"]
        existing_priority = [col for col in priority_cols if col in df.columns]
        
        # 其他常见字段（如果存在）
        common_cols = ["source_type", "text_content"]
        existing_common = [col for col in common_cols if col in df.columns and col not in existing_priority]
        
        # 剩余字段
        remaining_cols = [col for col in df.columns if col not in existing_priority + existing_common]
        
        # 重新排序
        df = df[existing_priority + existing_common + remaining_cols]
        
        # 导出到 Excel
        df.to_excel(output_path, index=False, engine="openpyxl")
        
        logger.info(f"成功导出 {len(content_list)} 条数据到: {output_path}")
        logger.info(f"Excel 包含 {len(df.columns)} 列（自动映射所有字段）")
        logger.info(f"请在 Excel 中审核数据，完成后使用 build_db.py 导入")
        
        return output_path
        
    except Exception as e:
        logger.error(f"导出 Excel 失败: {str(e)}")
        raise


def load_from_excel(
    excel_path: str,
    target_schema: Type[BaseModel],
    validate: bool = True
) -> List[BaseContent]:
    """
    从审核后的 Excel 中加载数据并转换为 BaseContent 对象（动态字段映射）
    
    特性：
    - 自动识别 Schema 定义的标准字段
    - 非标准字段自动打包回 metadata
    - Schema 新增字段时，自动从 Excel 读取
    
    Args:
        excel_path: Excel 文件路径
        target_schema: 目标 Schema 类（如 StoryClip, ArchitectureDoc）
        validate: 是否只加载 valid=True 的数据（默认 True）
    
    Returns:
        BaseContent 对象列表
    """
    if not os.path.exists(excel_path):
        logger.error(f"Excel 文件不存在: {excel_path}")
        return []
    
    try:
        # 读取 Excel
        df = pd.read_excel(excel_path, engine="openpyxl")
        
        logger.info(f"从 Excel 加载了 {len(df)} 行数据")
        
        # 如果需要过滤，只保留 valid=True 的行
        if validate and "valid" in df.columns:
            df = df[df["valid"] == True]
            logger.info(f"过滤后剩余 {len(df)} 条有效数据")
        
        # 获取目标 Schema 的标准字段集合
        schema_fields = set(target_schema.model_fields.keys())
        logger.debug(f"目标 Schema ({target_schema.__name__}) 标准字段: {schema_fields}")
        
        # 将 DataFrame 转换回 BaseContent 对象
        content_list = []
        for idx, row in df.iterrows():
            try:
                # 转换为字典（处理 NaN 值）
                row_dict = row.to_dict()
                row_dict = {k: v for k, v in row_dict.items() if pd.notna(v)}
                
                # 移除类型标识字段（如果存在）
                row_dict.pop("_content_type", None)
                
                # 重新打包 metadata（将非标准字段放回 metadata）
                reconstructed = _unflatten_metadata(row_dict, schema_fields)
                
                # 反序列化为 Pydantic 对象
                content_obj = target_schema(**reconstructed)
                content_list.append(content_obj)
                
            except ValidationError as e:
                logger.warning(f"第 {idx+2} 行数据验证失败，跳过: {str(e)}")
                continue
            except Exception as e:
                logger.warning(f"第 {idx+2} 行数据解析失败，跳过: {str(e)}")
                continue
        
        logger.info(f"成功加载 {len(content_list)} 条有效数据")
        
        return content_list
        
    except Exception as e:
        logger.error(f"读取 Excel 失败: {str(e)}")
        raise


def preview_excel(excel_path: str, head: int = 10) -> None:
    """
    预览 Excel 文件内容（用于调试）
    
    Args:
        excel_path: Excel 文件路径
        head: 显示前几行，默认 10
    """
    if not os.path.exists(excel_path):
        logger.error(f"Excel 文件不存在: {excel_path}")
        return
    
    try:
        df = pd.read_excel(excel_path, engine="openpyxl")
        print(f"\n{'='*80}")
        print(f"Excel 文件预览: {excel_path}")
        print(f"总行数: {len(df)}")
        print(f"{'='*80}\n")
        print(df.head(head))
        
        if "valid" in df.columns:
            valid_count = df["valid"].sum()
            print(f"\n有效数据: {valid_count}/{len(df)}")
        
    except Exception as e:
        logger.error(f"预览 Excel 失败: {str(e)}")


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("数据审核模块测试")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "preview" and len(sys.argv) > 2:
            # 预览 Excel 文件
            excel_path = sys.argv[2]
            preview_excel(excel_path)
        
        elif command == "load" and len(sys.argv) > 2:
            # 测试加载 Excel
            excel_path = sys.argv[2]
            content_list = load_from_excel(excel_path)
            print(f"\n加载成功，共 {len(content_list)} 条数据")
            
            for i, item in enumerate(content_list[:3], start=1):
                print(f"\n【数据 {i}】")
                print(f"  类型: {type(item).__name__}")
                print(f"  ID: {item.id}")
                print(f"  摘要: {item.summary[:50]}...")
        
        else:
            print("\n使用方法:")
            print("  python -m modules.reviewer preview <excel_path>")
            print("  python -m modules.reviewer load <excel_path>")
    else:
        print("\n使用方法:")
        print("  python -m modules.reviewer preview <excel_path>")
        print("  python -m modules.reviewer load <excel_path>")
