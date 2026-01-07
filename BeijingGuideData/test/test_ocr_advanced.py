"""
OCR 测试脚本 - 支持大文件和重试

改进功能：
1. 更长的超时时间（120秒）
2. 显示进度信息
3. 更详细的错误提示
"""

import sys
import os
import time
from modules.tools.ocr_tool import PaddleOCRClient
from config import settings


def test_ocr_with_progress(file_path: str):
    """
    测试 OCR 识别，显示进度
    
    Args:
        file_path: 图片或 PDF 页面的文件路径
    """
    print("=" * 70)
    print("🔍 PaddleOCR 测试（改进版 - 支持大文件）")
    print("=" * 70)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 错误：文件不存在 - {file_path}")
        return False
    
    # 检查配置
    print(f"\n📋 配置检查:")
    print(f"   API URL: {settings.PADDLE_OCR_API_URL}")
    print(f"   Token: {'已配置 ✓' if settings.PADDLE_OCR_TOKEN else '未配置 ✗'}")
    
    if not settings.PADDLE_OCR_API_URL:
        print(f"\n❌ 错误：PADDLE_OCR_API_URL 未配置")
        return False
    
    # 读取文件
    print(f"\n📄 读取文件: {file_path}")
    try:
        with open(file_path, "rb") as f:
            image_data = f.read()
        file_size = len(image_data)
        print(f"   文件大小: {file_size:,} 字节 ({file_size / 1024:.2f} KB)")
        
        # 检查文件大小
        if file_size > 1024 * 1024:  # > 1MB
            print(f"   ⚠️  文件较大，识别可能需要较长时间（1-2分钟）")
        elif file_size > 500 * 1024:  # > 500KB
            print(f"   ⚠️  文件较大，识别可能需要 30-60 秒")
            
    except Exception as e:
        print(f"❌ 读取文件失败: {str(e)}")
        return False
    
    # 初始化 OCR 客户端
    print(f"\n🚀 初始化 OCR 客户端...")
    ocr_client = PaddleOCRClient()
    
    # 判断文件类型
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.pdf':
        file_type = 0  # PDF
        print(f"   文件类型: PDF 文档")
        print(f"   提示: PDF 处理较慢，请耐心等待...")
    else:
        file_type = 1  # 图片
        print(f"   文件类型: 图片 ({file_ext})")
    
    # 执行 OCR
    print(f"\n⏳ 正在识别文字...")
    print(f"   超时设置: 120 秒")
    print(f"   请耐心等待，不要中断...")
    
    start_time = time.time()
    
    try:
        text = ocr_client.ocr_image(image_data, file_type=file_type)
        elapsed_time = time.time() - start_time
        
        # 显示结果
        print("\n" + "=" * 70)
        if text:
            print("✅ OCR 识别成功！")
            print(f"⏱️  耗时: {elapsed_time:.1f} 秒")
            print("=" * 70)
            print("\n📝 识别结果:\n")
            print(text)
            print("\n" + "=" * 70)
            print(f"📊 统计信息:")
            print(f"   字符数: {len(text)}")
            print(f"   行数: {text.count(chr(10)) + 1}")
            print(f"   识别速度: {len(text) / elapsed_time:.1f} 字符/秒")
            print("=" * 70)
            
            # 保存结果到文件
            output_file = file_path + ".txt"
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"\n💾 结果已保存到: {output_file}")
            except Exception as e:
                print(f"\n⚠️  保存结果失败: {str(e)}")
            
            return True
        else:
            print("❌ OCR 识别失败")
            print(f"⏱️  耗时: {elapsed_time:.1f} 秒")
            print("=" * 70)
            print_troubleshooting()
            return False
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ 发生错误: {str(e)}")
        print(f"⏱️  耗时: {elapsed_time:.1f} 秒")
        print_troubleshooting()
        return False


def print_troubleshooting():
    """打印故障排查建议"""
    print("\n🔧 故障排查建议:")
    print("=" * 70)
    print("\n1. 网络问题")
    print("   • 检查网络连接是否正常")
    print("   • 尝试访问 API URL 看是否能连接")
    print("   • 检查是否有防火墙或代理设置")
    
    print("\n2. 文件问题")
    print("   • PDF 文件是否损坏？尝试用其他工具打开")
    print("   • 文件是否太大？建议 < 1MB")
    print("   • 尝试转换为图片格式（JPG/PNG）")
    
    print("\n3. API 配置")
    print("   • API URL 是否正确？")
    print("   • Token 是否有效？")
    print("   • API 服务是否正常运行？")
    
    print("\n4. 尝试方案")
    print("   A. 将 PDF 转换为图片后重试")
    print("      • 使用截图工具截取 PDF 页面")
    print("      • 保存为 JPG 或 PNG 格式")
    print("      • 再次运行 OCR")
    
    print("\n   B. 减小文件大小")
    print("      • 压缩图片质量")
    print("      • 降低分辨率（保持清晰度）")
    
    print("\n   C. 测试网络连接")
    print("      • 运行: curl -I https://7395p7b8bfv811sd.aistudio-app.com/ocr")
    
    print("\n   D. 使用更小的测试文件")
    print("      • 先用一个小图片测试（< 100KB）")
    print("      • 确认 OCR 功能正常后再处理大文件")
    
    print("\n" + "=" * 70)


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🎯 PaddleOCR 图像文字识别测试工具（改进版）")
    print("=" * 70)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("\n使用方法:")
        print("  python test_ocr_advanced.py <文件路径>")
        print("\n示例:")
        print('  python test_ocr_advanced.py "test_data/page1.jpg"')
        print('  python test_ocr_advanced.py "test_data/document.pdf"')
        print("\n改进功能:")
        print("  ✓ 支持大文件（120秒超时）")
        print("  ✓ 显示识别进度和速度")
        print("  ✓ 详细的故障排查建议")
        sys.exit(0)
    
    # 获取文件路径
    file_path = sys.argv[1]
    
    # 执行测试
    success = test_ocr_with_progress(file_path)
    
    # 退出
    if success:
        print("\n✅ 测试完成！\n")
        sys.exit(0)
    else:
        print("\n❌ 测试失败\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
