"""
PDF 处理模块测试脚本

测试 PDFLoader 和 PDFProcessor 的完整功能。

测试流程：
1. 测试 PDFLoader - PDF 转图片 + OCR
2. 测试 PDFProcessor - 文本切分 + LLM 清洗
3. 测试完整流程 - 从 PDF 到结构化数据

Usage:
    python test/test_pdf_processing.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.crawlers.pdf_loader import PDFLoader
from modules.processors.pdf_processor import PDFProcessor
from modules.strategies import get_strategy
from utils.logger import logger


def test_pdf_loader():
    """测试 PDFLoader - PDF 转图片 + OCR"""
    print("=" * 80)
    print("测试 1: PDFLoader - PDF 转图片 + OCR")
    print("=" * 80)
    
    # 查找测试 PDF 文件
    test_pdf_dir = project_root / "test_data"
    pdf_files = list(test_pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ 未找到测试 PDF 文件，请将 PDF 文件放在 test_data/ 目录下")
        return None
    
    test_pdf = pdf_files[0]
    print(f"\n使用测试文件: {test_pdf.name}")
    
    # 初始化 PDFLoader
    loader = PDFLoader(dpi=200)
    
    # 加载 PDF 内容
    print("\n开始加载 PDF 内容...")
    full_text = loader.load_pdf_content(
        str(test_pdf),
        save_images=True,  # 保存图片以便检查
        output_dir=str(test_pdf_dir / "pdf_images")
    )
    
    # 检查结果
    if full_text:
        print(f"\n✓ PDF 加载成功")
        print(f"  - 总字符数: {len(full_text)}")
        print(f"  - 前 200 字符:\n{full_text[:200]}...")
        
        # 保存全文
        output_path = test_pdf_dir / f"{test_pdf.stem}_full_text.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"  - 全文已保存到: {output_path}")
        
        return test_pdf, full_text
    else:
        print("\n❌ PDF 加载失败")
        return None


def test_pdf_processor(test_pdf: Path, doc_type: str = "legend"):
    """测试 PDFProcessor - 文本切分 + LLM 清洗"""
    print("\n" + "=" * 80)
    print(f"测试 2: PDFProcessor - 文本切分 + LLM 清洗 (doc_type={doc_type})")
    print("=" * 80)
    
    # 检查策略是否存在
    strategy = get_strategy(doc_type)
    if not strategy:
        print(f"❌ 策略不存在: {doc_type}")
        print("支持的策略: legend, arch")
        return None
    
    print(f"\n使用策略:")
    print(f"  - 数据源类型: {strategy.source_type}")
    print(f"  - Schema: {strategy.schema.__name__}")
    print(f"  - 描述: {strategy.description}")
    
    # 初始化 PDFProcessor
    processor = PDFProcessor(
        chunk_size=1024,
        chunk_overlap=128
    )
    
    # 处理 PDF
    print(f"\n开始处理 PDF: {test_pdf.name}")
    results = processor.process_pdf(
        str(test_pdf),
        doc_type=doc_type,
        save_intermediate=True  # 保存中间结果
    )
    
    # 检查结果
    if results:
        print(f"\n✓ PDF 处理成功")
        print(f"  - 有效结果数: {len(results)}")
        
        # 显示前 3 条结果的详细信息
        for i, item in enumerate(results[:3], start=1):
            print(f"\n  【结果 {i}】")
            print(f"    ID: {item.id}")
            print(f"    类型: {type(item).__name__}")
            print(f"    摘要: {item.summary}")
            
            if hasattr(item, 'location'):
                print(f"    地点: {item.location}")
            
            if hasattr(item, 'story_name'):
                print(f"    故事名称: {item.story_name}")
            
            if hasattr(item, 'page_number'):
                print(f"    页码: {item.page_number}")
            
            print(f"    文本长度: {len(item.text_content)} 字符")
            print(f"    文本预览: {item.text_content[:100]}...")
        
        if len(results) > 3:
            print(f"\n  ... 还有 {len(results) - 3} 条结果")
        
        # 保存结果到 JSON
        import json
        output_path = project_root / "test_data" / f"{test_pdf.stem}_{doc_type}_results.json"
        data = [item.model_dump() for item in results]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n  - 结果已保存到: {output_path}")
        
        return results
    else:
        print("\n❌ PDF 处理失败或未提取到有效内容")
        return None


def test_complete_workflow():
    """测试完整流程"""
    print("\n" + "=" * 80)
    print("开始完整测试流程")
    print("=" * 80)
    
    # 第 1 步：测试 PDFLoader
    loader_result = test_pdf_loader()
    
    if not loader_result:
        print("\n❌ PDFLoader 测试失败，终止测试")
        return
    
    test_pdf, full_text = loader_result
    
    # 第 2 步：测试 PDFProcessor (legend 类型)
    print("\n" + "~" * 80)
    print("测试文档类型: legend (传说故事)")
    print("~" * 80)
    
    legend_results = test_pdf_processor(test_pdf, doc_type="legend")
    
    # 第 3 步：测试 PDFProcessor (arch 类型)
    print("\n" + "~" * 80)
    print("测试文档类型: arch (建筑文档)")
    print("~" * 80)
    
    arch_results = test_pdf_processor(test_pdf, doc_type="arch")
    
    # 汇总测试结果
    print("\n" + "=" * 80)
    print("测试完成 - 汇总结果")
    print("=" * 80)
    
    print(f"\n✓ PDFLoader 测试通过")
    print(f"  - 提取字符数: {len(full_text)}")
    
    if legend_results:
        print(f"\n✓ PDFProcessor (legend) 测试通过")
        print(f"  - 有效结果数: {len(legend_results)}")
    else:
        print(f"\n⚠ PDFProcessor (legend) 未提取到有效内容（可能是文档不包含传说故事）")
    
    if arch_results:
        print(f"\n✓ PDFProcessor (arch) 测试通过")
        print(f"  - 有效结果数: {len(arch_results)}")
    else:
        print(f"\n⚠ PDFProcessor (arch) 未提取到有效内容（可能是文档不包含建筑信息）")
    
    print("\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)


def test_specific_pdf(pdf_path: str, doc_type: str):
    """测试指定的 PDF 文件"""
    print("=" * 80)
    print(f"测试指定 PDF: {pdf_path}")
    print(f"文档类型: {doc_type}")
    print("=" * 80)
    
    test_pdf = Path(pdf_path)
    if not test_pdf.exists():
        print(f"❌ 文件不存在: {pdf_path}")
        return
    
    # 测试 PDFLoader
    print("\n步骤 1: PDFLoader - 加载 PDF 内容")
    print("-" * 80)
    
    loader = PDFLoader(dpi=200)
    full_text = loader.load_pdf_content(
        str(test_pdf),
        save_images=True,
        output_dir=str(test_pdf.parent / "pdf_images")
    )
    
    if not full_text:
        print("❌ PDF 加载失败")
        return
    
    print(f"✓ 加载成功，字符数: {len(full_text)}")
    
    # 测试 PDFProcessor
    print("\n步骤 2: PDFProcessor - 处理 PDF 内容")
    print("-" * 80)
    
    processor = PDFProcessor(chunk_size=1024, chunk_overlap=128)
    results = processor.process_pdf(
        str(test_pdf),
        doc_type=doc_type,
        save_intermediate=True
    )
    
    if not results:
        print("❌ PDF 处理失败或未提取到有效内容")
        return
    
    print(f"✓ 处理成功，有效结果数: {len(results)}")
    
    # 显示结果
    print("\n结果预览:")
    print("-" * 80)
    for i, item in enumerate(results[:5], start=1):
        print(f"\n【{i}】 {item.summary}")
        if hasattr(item, 'location') and item.location:
            print(f"    地点: {item.location}")
    
    if len(results) > 5:
        print(f"\n... 还有 {len(results) - 5} 条结果")


# ============================================================================
# 主函数
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" PDF 处理模块测试")
    print("=" * 80)
    
    # 检查是否提供了命令行参数
    if len(sys.argv) > 2:
        # 测试指定的 PDF 文件
        pdf_path = sys.argv[1]
        doc_type = sys.argv[2]
        test_specific_pdf(pdf_path, doc_type)
    else:
        # 运行完整测试流程
        print("\n提示: 请确保在 test_data/ 目录下放置了测试 PDF 文件")
        print("如需测试指定文件，请使用: python test_pdf_processing.py <pdf_path> <doc_type>")
        print("例如: python test_pdf_processing.py test_data/sample.pdf legend\n")
        
        input("按 Enter 键开始测试...")
        
        try:
            test_complete_workflow()
        except KeyboardInterrupt:
            print("\n\n测试被用户中断")
        except Exception as e:
            logger.error(f"测试过程中发生错误: {str(e)}")
            print(f"\n❌ 测试失败: {str(e)}")
