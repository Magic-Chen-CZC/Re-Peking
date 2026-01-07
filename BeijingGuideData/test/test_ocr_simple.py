"""
OCR 测试脚本 - 简单易用版

使用方法：
1. 将要测试的 PDF 页面或图片放到 test_data/ 目录下
2. 运行命令：
   source venv/bin/activate
   python test_ocr_simple.py <文件名>

示例：
   python test_ocr_simple.py test_data/example.jpg
   python test_ocr_simple.py test_data/page1.png
"""

import sys
import os
from modules.tools.ocr_tool import PaddleOCRClient
from config import settings


def test_ocr_file(file_path: str):
    """
    测试 OCR 识别单个文件
    
    Args:
        file_path: 图片或 PDF 页面的文件路径
    """
    print("=" * 70)
    print("🔍 PaddleOCR 测试")
    print("=" * 70)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 错误：文件不存在 - {file_path}")
        print(f"\n💡 提示：请将文件放到以下位置：")
        print(f"   - {os.path.abspath('test_data/')}")
        print(f"   - {os.path.abspath('.')}")
        return False
    
    # 检查配置
    print(f"\n📋 配置检查:")
    print(f"   API URL: {settings.PADDLE_OCR_API_URL}")
    print(f"   Token: {'已配置 ✓' if settings.PADDLE_OCR_TOKEN else '未配置 ✗'}")
    
    if not settings.PADDLE_OCR_API_URL:
        print(f"\n❌ 错误：PADDLE_OCR_API_URL 未配置")
        print(f"   请在 config.py 或 .env 文件中配置")
        return False
    
    # 读取文件
    print(f"\n📄 读取文件: {file_path}")
    try:
        with open(file_path, "rb") as f:
            image_data = f.read()
        file_size = len(image_data)
        print(f"   文件大小: {file_size:,} 字节 ({file_size / 1024:.2f} KB)")
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
    else:
        file_type = 1  # 图片
        print(f"   文件类型: 图片 ({file_ext})")
    
    # 执行 OCR
    print(f"\n⏳ 正在识别文字，请稍候...")
    text = ocr_client.ocr_image(image_data, file_type=file_type)
    
    # 显示结果
    print("\n" + "=" * 70)
    if text:
        print("✅ OCR 识别成功！")
        print("=" * 70)
        print("\n📝 识别结果:\n")
        print(text)
        print("\n" + "=" * 70)
        print(f"📊 统计信息:")
        print(f"   字符数: {len(text)}")
        print(f"   行数: {text.count(chr(10)) + 1}")
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
        print("=" * 70)
        print("\n可能的原因:")
        print("   1. 图片质量不佳")
        print("   2. 图片中没有文字")
        print("   3. API 调用失败（检查网络或 API 配置）")
        print("   4. 文件格式不支持")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🎯 PaddleOCR 图像文字识别测试工具")
    print("=" * 70)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("\n📖 使用说明:")
        print("=" * 70)
        print("\n1️⃣  将要测试的文件放到以下位置之一:")
        print(f"   • test_data/ 目录（推荐）")
        print(f"   • 项目根目录")
        print(f"   • 任意位置（需提供完整路径）")
        
        print("\n2️⃣  运行测试命令:")
        print("   source venv/bin/activate")
        print("   python test_ocr_simple.py <文件路径>")
        
        print("\n3️⃣  示例:")
        print("   python test_ocr_simple.py test_data/page1.jpg")
        print("   python test_ocr_simple.py test_data/document.pdf")
        print("   python test_ocr_simple.py /path/to/image.png")
        
        print("\n" + "=" * 70)
        print("\n💡 支持的文件格式:")
        print("   • 图片: .jpg, .jpeg, .png, .bmp, .tiff")
        print("   • 文档: .pdf")
        
        # 检查 test_data 目录中是否有文件
        test_data_dir = "test_data"
        if os.path.exists(test_data_dir):
            files = [f for f in os.listdir(test_data_dir) 
                    if not f.startswith('.') and os.path.isfile(os.path.join(test_data_dir, f))]
            if files:
                print(f"\n📁 test_data/ 目录中的文件:")
                for f in files:
                    file_path = os.path.join(test_data_dir, f)
                    size = os.path.getsize(file_path)
                    print(f"   • {f} ({size / 1024:.2f} KB)")
                print(f"\n   可以运行: python test_ocr_simple.py test_data/{files[0]}")
        
        print("\n" + "=" * 70)
        sys.exit(0)
    
    # 获取文件路径
    file_path = sys.argv[1]
    
    # 执行测试
    success = test_ocr_file(file_path)
    
    # 退出
    if success:
        print("\n✅ 测试完成！\n")
        sys.exit(0)
    else:
        print("\n❌ 测试失败\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
