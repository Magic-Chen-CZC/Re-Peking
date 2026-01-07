#!/usr/bin/env python3
"""
数据入库脚本

功能：负责"将审核后的 Excel 存入向量数据库"

使用示例：
    # 导入审核后的 Excel 数据
    python build_db.py --file data/review/pending_20231210_153045.xlsx
    
    # 导入时不验证 valid 字段（导入所有数据）
    python build_db.py --file data/review/pending_20231210_153045.xlsx --no-validate

工作流程：
    1. 从 Excel 读取审核后的数据
    2. 转换为 BaseContent 对象
    3. 批量存入向量数据库
"""

import argparse
import asyncio
from pathlib import Path
import pandas as pd

from utils.logger import logger

# 导入审核和存储模块
from modules.reviewer import load_from_excel, CONTENT_TYPE_MAP
from modules.vector_store import save_to_db


def detect_schema_from_excel(excel_path: str):
    """
    从 Excel 文件中检测数据类型（自动识别 Schema）
    
    Args:
        excel_path: Excel 文件路径
    
    Returns:
        Schema 类，如果无法识别返回 None
    """
    try:
        df = pd.read_excel(excel_path, engine="openpyxl", nrows=1)
        
        if "_content_type" in df.columns:
            content_type = df["_content_type"].iloc[0]
            schema = CONTENT_TYPE_MAP.get(content_type)
            if schema:
                logger.info(f"检测到数据类型: {content_type} ({schema.__name__})")
                return schema
        
        logger.warning("Excel 中没有 _content_type 字段，将尝试推断")
        
        # 简单推断：根据列名判断
        columns = set(df.columns)
        if "story_name" in columns and "is_legend" in columns:
            logger.info("根据列名推断数据类型: StoryClip")
            return CONTENT_TYPE_MAP["StoryClip"]
        elif "page_number" in columns and "technical_specs" in columns:
            logger.info("根据列名推断数据类型: ArchitectureDoc")
            return CONTENT_TYPE_MAP["ArchitectureDoc"]
        else:
            logger.info("根据列名推断数据类型: XHSNote")
            return CONTENT_TYPE_MAP["XHSNote"]
            
    except Exception as e:
        logger.error(f"检测 Schema 失败: {str(e)}")
        return None


async def build_database(excel_path: str, validate: bool = True) -> int:
    """
    从 Excel 读取数据并批量存入数据库（自动识别 Schema）
    
    Args:
        excel_path: Excel 文件路径
        validate: 是否只导入 valid=True 的数据
    
    Returns:
        成功入库的数据条数
    """
    logger.info("=" * 80)
    logger.info("开始构建向量数据库")
    logger.info("=" * 80)
    
    # 检查文件是否存在
    if not Path(excel_path).exists():
        logger.error(f"Excel 文件不存在: {excel_path}")
        return 0
    
    # 自动检测 Schema 类型
    schema_class = detect_schema_from_excel(excel_path)
    if not schema_class:
        logger.error("无法检测数据类型，请检查 Excel 文件格式")
        return 0
    
    # 从 Excel 加载数据（使用检测到的 Schema）
    content_list = load_from_excel(excel_path, target_schema=schema_class, validate=validate)
    
    if not content_list:
        logger.warning("没有数据可导入")
        return 0
    
    logger.info(f"加载了 {len(content_list)} 条待入库数据")
    
    # 批量存入向量数据库
    logger.info("=" * 80)
    logger.info("开始批量存入向量数据库")
    logger.info("=" * 80)
    
    success_count = 0
    failed_count = 0
    
    for idx, item in enumerate(content_list, start=1):
        try:
            await save_to_db(item)
            success_count += 1
            
            # 每 10 条打印一次进度
            if idx % 10 == 0:
                logger.info(f"进度: {idx}/{len(content_list)}")
                
        except Exception as e:
            logger.error(f"第 {idx} 条数据入库失败 (ID: {item.id}): {str(e)}")
            failed_count += 1
            continue
    
    logger.info("=" * 80)
    logger.info("批量入库完成")
    logger.info("=" * 80)
    logger.info(f"成功: {success_count} 条")
    if failed_count > 0:
        logger.warning(f"失败: {failed_count} 条")
    
    return success_count


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="北京导览 AI - 数据入库脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 导入审核后的数据（默认只导入 valid=True 的数据）
  python build_db.py --file data/review/pending_20231210_153045.xlsx
  
  # 导入所有数据（不验证 valid 字段）
  python build_db.py --file data/review/pending_20231210_153045.xlsx --no-validate
        """
    )
    
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="审核后的 Excel 文件路径"
    )
    
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="不验证 valid 字段，导入所有数据（默认只导入 valid=True 的数据）"
    )
    
    args = parser.parse_args()
    
    # 验证文件是否存在
    if not Path(args.file).exists():
        logger.error(f"Excel 文件不存在: {args.file}")
        return
    
    # 执行入库
    validate = not args.no_validate
    success_count = await build_database(args.file, validate=validate)
    
    # 打印结果
    print("\n" + "=" * 80)
    if success_count > 0:
        print("✅ 数据入库完成")
        print("=" * 80)
        print(f"📊 成功入库 {success_count} 条数据")
        print(f"📁 Excel 文件: {args.file}")
        print("\n💡 提示：")
        print("   - 数据已存入向量数据库")
        print("   - 可以使用 search.py 进行检索测试")
        print("   - 向量数据库路径: data/chroma_db/")
    else:
        print("❌ 没有数据被导入")
        print("=" * 80)
        print("⚠️  请检查：")
        print("   - Excel 文件中是否有 valid=True 的数据")
        print("   - 如需导入所有数据，请使用 --no-validate 参数")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
