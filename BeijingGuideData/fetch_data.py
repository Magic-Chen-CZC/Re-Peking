#!/usr/bin/env python3
"""
数据采集脚本

功能：负责数据的"采集 + 清洗 + 导出到 Excel"
支持数据源：XHS（小红书）、PDF（文档）、Web（网页）

使用方式：
    1. 交互式模式（推荐）：
       python fetch_data.py
       
    2. 命令行模式：
       python fetch_data.py --source xhs --file data/raw/xhs_notes.json
       python fetch_data.py --source pdf --file test_data/legends.pdf --doc_type legend
       python fetch_data.py --source web --url https://example.com/article --doc_type legend

输出：
    - Excel 文件保存在 data/review/pending_{timestamp}.xlsx
    - 需要人工审核后，使用 build_db.py 导入数据库
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

from config import settings
from utils.logger import logger

# 导入新的业务配置
from modules.domain_config import DOMAIN_CONFIG, get_domain_config, list_domain_types

# 导入爬虫和处理器
from modules.crawlers.xhs_crawler import XHSCrawler
from modules.crawlers.web_crawler import crawl_url
from modules.processors.xhs_processor import XHSProcessor
from modules.processors.pdf_processor import PDFProcessor

# 导入审核模块
from modules.reviewer import export_to_excel


async def fetch_xhs_data(file_path: str) -> list:
    """
    采集并处理小红书数据
    
    Args:
        file_path: 本地 JSON 文件路径
    
    Returns:
        处理后的 XHSNote 对象列表
    """
    logger.info("=" * 80)
    logger.info("开始处理小红书数据")
    logger.info("=" * 80)
    
    # 加载本地数据
    crawler = XHSCrawler(default_local_path=file_path)
    raw_notes = crawler.load_local_json_data(file_path)
    
    if not raw_notes:
        logger.warning("未获取到任何小红书数据")
        return []
    
    logger.info(f"加载了 {len(raw_notes)} 条原始笔记")
    
    # 批量处理
    processor = XHSProcessor()
    xhs_notes = await processor.process_batch(raw_notes)
    
    logger.info(f"处理完成，共 {len(xhs_notes)} 条数据")
    
    return xhs_notes


def fetch_pdf_data(file_path: str, doc_type: str) -> list:
    """
    采集并处理 PDF 数据
    
    Args:
        file_path: PDF 文件路径
        doc_type: 文档类型（legend 或 arch）
    
    Returns:
        处理后的 StoryClip 或 ArchitectureDoc 对象列表
    """
    logger.info("=" * 80)
    logger.info("开始处理 PDF 文档")
    logger.info("=" * 80)
    
    # 处理 PDF
    processor = PDFProcessor()
    results = processor.process_pdf(
        file_path,
        doc_type=doc_type,
        save_intermediate=True  # 保存中间结果供调试
    )
    
    logger.info(f"处理完成，共 {len(results)} 条有效数据")
    
    return results


def fetch_web_data(url: str, doc_type: str) -> list:
    """
    采集并处理网页数据
    
    Args:
        url: 网页 URL 地址
        doc_type: 文档类型（legend、arch 等）
    
    Returns:
        处理后的结构化内容列表
    """
    logger.info("=" * 80)
    logger.info("开始处理网页数据")
    logger.info("=" * 80)
    
    # 爬取网页内容
    full_text = crawl_url(url)
    
    if not full_text or not full_text.strip():
        logger.warning(f"未能从网页提取内容: {url}")
        return []
    
    logger.info(f"成功提取网页内容，字符数: {len(full_text)}")
    
    # 获取业务配置
    domain_config = get_domain_config(doc_type)
    if not domain_config:
        logger.error(f"不支持的文档类型: {doc_type}")
        return []
    
    # 使用 PDF 处理器的统一文本处理逻辑
    processor = PDFProcessor()
    
    # 文本切分（使用配置中的 chunking 参数）
    chunks = processor._split_text(full_text, domain_config)
    
    if not chunks:
        logger.warning(f"文本切分失败或过滤后无有效 chunk")
        return []
    
    logger.info(f"文本已切分为 {len(chunks)} 个 Chunk")
    
    # 处理 chunks（使用统一的处理逻辑）
    results = processor._process_chunks(
        chunks,
        domain_config,
        url,  # 用 URL 作为来源标识
        doc_type
    )
    
    logger.info(f"处理完成，共 {len(results)} 条有效数据")
    
    return results


# ============================================================================
# 交互式菜单模式 - 重构版
# ============================================================================

def print_banner():
    """打印欢迎横幅"""
    print("\n" + "=" * 60)
    print("🤖 BeijingGuideAI 数据采集向导")
    print("=" * 60)


def select_data_source() -> Tuple[str, Optional[str], Optional[str]]:
    """
    第一步：选择数据来源
    
    Returns:
        (loader_type, file_path_or_url, file_extension):
        - loader_type: 'pdf', 'json', 'web'
        - file_path_or_url: 文件路径或 URL
        - file_extension: 文件扩展名（仅本地文件）
    """
    print("\n【步骤 1/2】请选择数据来源：")
    print("[1] 本地文件 (Local File)")
    print("[2] 网络链接 (Web URL)")
    
    while True:
        try:
            choice = input("\n请输入序号 (1-2): ").strip()
            
            if choice == "1":
                # 本地文件分支
                return _select_local_file()
            elif choice == "2":
                # 网络链接分支
                return _select_web_url()
            else:
                print("❌ 无效输入，请输入 1 或 2")
        except KeyboardInterrupt:
            print("\n\n👋 已取消")
            sys.exit(0)


def _select_local_file() -> Tuple[str, str, str]:
    """
    选择本地文件
    
    Returns:
        (loader_type, file_path, file_extension)
    """
    data_dir = "data/raw"
    data_path = Path(data_dir)
    
    if not data_path.exists():
        os.makedirs(data_dir, exist_ok=True)
    
    # 扫描所有非隐藏文件
    all_files = [
        f for f in data_path.iterdir()
        if f.is_file() and not f.name.startswith('.')
    ]
    
    if not all_files:
        print(f"\n❌ {data_dir}/ 目录下没有文件")
        print(f"💡 请先将数据文件（.pdf 或 .json）放入该目录")
        sys.exit(0)
    
    # 按文件名排序
    all_files.sort(key=lambda x: x.name)
    
    print("\n" + "-" * 60)
    print("📂 发现以下文件：")
    
    for i, file_path in enumerate(all_files, start=1):
        file_size = file_path.stat().st_size
        size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
        file_ext = file_path.suffix.lower()
        print(f"[{i}] {file_path.name} ({size_str}) {file_ext}")
    
    while True:
        try:
            choice = input(f"\n请选择要处理的文件序号 (1-{len(all_files)}): ").strip()
            
            if not choice:
                continue
            
            idx = int(choice) - 1
            
            if 0 <= idx < len(all_files):
                selected_file = all_files[idx]
                file_ext = selected_file.suffix.lower()
                
                # 判断 loader_type
                if file_ext == '.pdf':
                    loader_type = 'pdf'
                elif file_ext == '.json':
                    loader_type = 'json'
                else:
                    print(f"⚠️  不支持的文件格式: {file_ext}")
                    print("   支持的格式: .pdf, .json")
                    continue
                
                return loader_type, str(selected_file), file_ext
            else:
                print(f"❌ 无效输入，请输入 1-{len(all_files)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n👋 已取消")
            sys.exit(0)


def _select_web_url() -> Tuple[str, str, None]:
    """
    输入网络 URL
    
    Returns:
        ('web', url, None)
    """
    print("\n" + "-" * 60)
    
    while True:
        try:
            url = input("📝 请输入网页 URL 地址: ").strip()
            
            if not url:
                continue
            
            if not url.startswith(('http://', 'https://')):
                print("❌ URL 格式无效，必须以 http:// 或 https:// 开头")
                continue
            
            return 'web', url, None
            
        except KeyboardInterrupt:
            print("\n\n👋 已取消")
            sys.exit(0)


def select_processing_strategy(loader_type: str) -> str:
    """
    第二步：选择处理策略
    
    Args:
        loader_type: 数据加载器类型 ('pdf', 'json', 'web')
    
    Returns:
        doc_type: 策略类型（如 'legend', 'arch', 'xhs'）
    """
    print("\n【步骤 2/2】请选择该数据的处理策略（内容类型）：")
    
    # 根据 loader_type 过滤可用策略
    if loader_type == 'json':
        # JSON 文件只能用 XHS 策略
        available_strategies = {'xhs': DOMAIN_CONFIG['xhs']}
    else:
        # PDF 和 Web 可以用所有策略（除了 xhs）
        available_strategies = {
            key: value for key, value in DOMAIN_CONFIG.items()
            if key != 'xhs'
        }
    
    # 显示策略选项
    strategy_list = list(available_strategies.items())
    for i, (key, config) in enumerate(strategy_list, start=1):
        print(f"[{i}] {key} - {config['description']}")
    
    while True:
        try:
            choice = input(f"\n请输入序号 (1-{len(strategy_list)}): ").strip()
            
            if not choice:
                continue
            
            idx = int(choice) - 1
            
            if 0 <= idx < len(strategy_list):
                doc_type = strategy_list[idx][0]
                return doc_type
            else:
                print(f"❌ 无效输入，请输入 1-{len(strategy_list)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n👋 已取消")
            sys.exit(0)


async def run_interactive_mode():
    """运行交互式菜单模式 - 重构版"""
    print_banner()
    
    # 步骤 1: 选择数据来源
    loader_type, source_input, file_ext = select_data_source()
    
    # 步骤 2: 选择处理策略
    doc_type = select_processing_strategy(loader_type)
    
    # 步骤 3: 执行处理
    print("\n" + "-" * 60)
    source_type_name = {
        'pdf': 'PDF 文档',
        'json': 'JSON 文件',
        'web': '网页'
    }.get(loader_type, '未知')
    
    strategy_name = DOMAIN_CONFIG[doc_type]['description']
    
    if loader_type == 'web':
        print(f"🚀 开始处理：{source_input}")
    else:
        print(f"🚀 开始处理：{Path(source_input).name}")
    
    print(f"   数据类型: {source_type_name}")
    print(f"   处理策略: {strategy_name}")
    print("-" * 60 + "\n")
    
    # 根据 (loader_type + doc_type) 调用对应的处理逻辑
    results = []
    
    if loader_type == 'web':
        # Web + 任意策略
        results = fetch_web_data(source_input, doc_type)
    
    elif loader_type == 'pdf':
        # PDF File + 任意策略
        results = fetch_pdf_data(source_input, doc_type)
    
    elif loader_type == 'json' and doc_type == 'xhs':
        # JSON File + XHS 策略
        results = await fetch_xhs_data(source_input)
    
    else:
        # 不支持的组合
        logger.error(f"不支持的组合: loader_type={loader_type}, doc_type={doc_type}")
        print(f"\n❌ 不支持的数据源和策略组合")
        return
    
    if not results:
        logger.warning("没有数据可导出")
        print("\n⚠️  未提取到有效数据")
        return
    
    # 导出到 Excel
    logger.info("=" * 80)
    logger.info("导出数据到 Excel")
    logger.info("=" * 80)
    
    excel_path = export_to_excel(results, output_dir="data/review")
    
    if excel_path:
        print("\n" + "=" * 80)
        print("✅ 数据采集和处理完成")
        print("=" * 80)
        print(f"📊 共处理 {len(results)} 条数据")
        print(f"📁 Excel 文件: {excel_path}")
        print("\n⚠️  请在 Excel 中人工审核数据：")
        print("   - 检查 valid 字段（True/False）")
        print("   - 修改或删除不合格的数据")
        print("   - 完成后使用以下命令导入数据库：")
        print(f"\n   python build_db.py --file {excel_path}")
        print("=" * 80 + "\n")


async def main():
    """主函数"""
    # 检查是否有命令行参数
    if len(sys.argv) == 1:
        # 没有参数，启动交互式模式
        await run_interactive_mode()
        return
    
    # 有参数，使用命令行模式
    parser = argparse.ArgumentParser(
        description="北京导览 AI - 数据采集脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 处理本地小红书数据
  python fetch_data.py --source xhs --file data/raw/xhs_notes.json
  
  # 处理 PDF 传说故事
  python fetch_data.py --source pdf --file test_data/legends.pdf --doc_type legend
  
  # 处理 PDF 建筑文档
  python fetch_data.py --source pdf --file data/raw/architecture.pdf --doc_type arch
        """
    )
    
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        choices=["xhs", "pdf", "web"],
        help="数据源类型：xhs（小红书）、pdf（PDF文档）或 web（网页）"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="数据文件路径（XHS 的 JSON 文件或 PDF 文件）"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="网页 URL 地址（仅当 source=web 时需要）"
    )
    
    parser.add_argument(
        "--doc_type",
        type=str,
        choices=["legend", "arch", "generic"],
        help="文档类型：legend（传说故事）、arch（建筑文档）或 generic（通用）"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="data/review",
        help="Excel 输出目录，默认为 data/review"
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if args.source in ["xhs", "pdf"] and not args.file:
        logger.error("处理 XHS 或 PDF 时必须指定 --file 参数")
        return
    
    if args.source == "web" and not args.url:
        logger.error("处理网页时必须指定 --url 参数")
        return
    
    if args.source in ["pdf", "web"] and not args.doc_type:
        logger.error("处理 PDF 或网页时必须指定 --doc_type (legend, arch 或 generic)")
        return
    
    if not Path(args.file).exists() if args.file else False:
        logger.error(f"文件不存在: {args.file}")
        return
    
    # 执行采集和处理
    results = []
    
    if args.source == "xhs":
        results = await fetch_xhs_data(args.file)
    elif args.source == "pdf":
        results = fetch_pdf_data(args.file, args.doc_type)
    elif args.source == "web":
        results = fetch_web_data(args.url, args.doc_type)
    
    if not results:
        logger.warning("没有数据可导出")
        return
    
    # 导出到 Excel 供人工审核
    logger.info("=" * 80)
    logger.info("导出数据到 Excel")
    logger.info("=" * 80)
    
    excel_path = export_to_excel(results, output_dir=args.output)
    
    if excel_path:
        print("\n" + "=" * 80)
        print("✅ 数据采集和处理完成")
        print("=" * 80)
        print(f"📊 共处理 {len(results)} 条数据")
        print(f"📁 Excel 文件: {excel_path}")
        print("\n⚠️  请在 Excel 中人工审核数据：")
        print("   - 检查 valid 字段（True/False）")
        print("   - 修改或删除不合格的数据")
        print("   - 完成后使用以下命令导入数据库：")
        print(f"\n   python build_db.py --file {excel_path}")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    # 判断是否为交互式模式
    if len(sys.argv) == 1:
        # 无参数，进入交互式模式
        asyncio.run(run_interactive_mode())
    else:
        # 有参数，进入命令行模式
        asyncio.run(main())
