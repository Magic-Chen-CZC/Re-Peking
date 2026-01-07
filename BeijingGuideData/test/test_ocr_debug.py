"""
OCR 调试工具 - 查看 API 原始返回结果

用于调试 PaddleOCR API 的返回格式
"""

import sys
import os
import json
from modules.tools.ocr_tool import PaddleOCRClient
from config import settings


def debug_ocr(file_path: str):
    """调试 OCR 返回结果"""
    
    print("=" * 70)
    print("🐛 OCR API 调试工具")
    print("=" * 70)
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 读取文件
    with open(file_path, "rb") as f:
        image_data = f.read()
    
    file_size = len(image_data)
    print(f"\n📄 文件: {file_path}")
    print(f"📊 大小: {file_size / 1024:.2f} KB")
    
    # 判断文件类型
    file_ext = os.path.splitext(file_path)[1].lower()
    file_type = 0 if file_ext == '.pdf' else 1
    print(f"📝 类型: {'PDF' if file_type == 0 else '图片'}")
    
    # 初始化客户端
    client = PaddleOCRClient()
    
    print(f"\n⏳ 调用 OCR API...")
    
    # 获取详细结果
    result = client.ocr_image_with_details(image_data, file_type=file_type)
    
    if not result:
        print("❌ API 调用失败")
        return
    
    # 保存原始结果
    output_file = "ocr_debug_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ API 调用成功")
    print(f"💾 原始结果已保存到: {output_file}")
    
    # 分析结果结构
    print("\n" + "=" * 70)
    print("📊 结果结构分析:")
    print("=" * 70)
    
    if "result" in result:
        print("\n✓ 包含 'result' 字段")
        result_data = result["result"]
        
        if "ocrResults" in result_data:
            ocr_results = result_data["ocrResults"]
            print(f"✓ 包含 'ocrResults' 字段")
            print(f"✓ 识别结果数量: {len(ocr_results)}")
            
            if ocr_results:
                print(f"\n第 1 个结果的字段:")
                first_result = ocr_results[0]
                for key in first_result.keys():
                    value = first_result[key]
                    value_type = type(value).__name__
                    
                    if isinstance(value, str):
                        preview = value[:100] + "..." if len(value) > 100 else value
                        print(f"  • {key} ({value_type}): {repr(preview)}")
                    elif isinstance(value, list):
                        print(f"  • {key} ({value_type}): {len(value)} 项")
                        if value and len(value) > 0:
                            print(f"    第 1 项类型: {type(value[0]).__name__}")
                            if isinstance(value[0], dict):
                                print(f"    第 1 项字段: {list(value[0].keys())}")
                            elif isinstance(value[0], list):
                                print(f"    第 1 项长度: {len(value[0])}")
                    elif isinstance(value, dict):
                        print(f"  • {key} ({value_type}): {list(value.keys())}")
                    else:
                        print(f"  • {key} ({value_type}): {value}")
    
    print("\n" + "=" * 70)
    print("💡 请检查 ocr_debug_result.json 文件查看完整结果")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python test_ocr_debug.py <文件路径>")
        print('示例: python test_ocr_debug.py "test_data/file.pdf"')
        sys.exit(1)
    
    debug_ocr(sys.argv[1])
