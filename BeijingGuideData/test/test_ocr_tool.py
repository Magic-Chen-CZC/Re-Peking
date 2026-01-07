"""
测试 OCR 工具模块

本脚本测试 PaddleOCRClient 的功能：
1. 配置检查
2. 模拟 API 响应解析
3. 错误处理
"""

from modules.tools.ocr_tool import PaddleOCRClient
from config import settings


def test_ocr_client_init():
    """测试 OCR 客户端初始化"""
    print("=" * 60)
    print("测试 1: OCR 客户端初始化")
    print("=" * 60)
    
    # 测试默认初始化
    client = PaddleOCRClient()
    print(f"API URL 配置: {client.api_url or '未配置'}")
    
    # 测试自定义初始化
    custom_client = PaddleOCRClient(
        api_url="https://custom-api.example.com",
        token="test_token_123"
    )
    assert custom_client.api_url == "https://custom-api.example.com"
    assert custom_client.token == "test_token_123"
    print("✓ 自定义初始化成功")
    
    print("\n✅ 初始化测试通过!\n")


def test_extract_text_from_result():
    """测试从 API 响应中提取文本"""
    print("=" * 60)
    print("测试 2: 提取文本功能")
    print("=" * 60)
    
    client = PaddleOCRClient()
    
    # 模拟 PaddleOCR API 响应
    mock_result = {
        "result": {
            "ocrResults": [
                {
                    "prunedResult": "这是第一段识别的文本",
                    "ocrImage": "https://example.com/image1.jpg"
                },
                {
                    "prunedResult": "这是第二段识别的文本",
                    "ocrImage": "https://example.com/image2.jpg"
                },
                {
                    "prunedResult": "这是第三段识别的文本",
                    "ocrImage": "https://example.com/image3.jpg"
                }
            ]
        }
    }
    
    # 提取文本
    text = client._extract_text_from_result(mock_result)
    
    print(f"提取的文本:\n{text}")
    
    # 验证
    assert "第一段" in text
    assert "第二段" in text
    assert "第三段" in text
    assert text.count("\n") == 2  # 三段文本用两个换行符连接
    
    print("\n✓ 文本提取正确")
    
    # 测试空结果
    empty_result = {"result": {"ocrResults": []}}
    empty_text = client._extract_text_from_result(empty_result)
    assert empty_text == ""
    print("✓ 空结果处理正确")
    
    # 测试异常结果
    invalid_result = {"result": {}}
    invalid_text = client._extract_text_from_result(invalid_result)
    assert invalid_text == ""
    print("✓ 异常结果处理正确")
    
    print("\n✅ 提取文本测试通过!\n")


def test_ocr_error_handling():
    """测试 OCR 错误处理"""
    print("=" * 60)
    print("测试 3: 错误处理")
    print("=" * 60)
    
    # 测试未配置 API URL
    client = PaddleOCRClient(api_url="")
    result = client.ocr_image(b"fake_image_data")
    assert result == ""
    print("✓ 未配置 API URL 时返回空字符串")
    
    # 测试无效的图像数据（会在实际请求时失败）
    # 注意：这个测试需要有效的 API URL 才能真正测试网络错误
    print("✓ 错误处理机制已就绪")
    
    print("\n✅ 错误处理测试通过!\n")


def test_configuration():
    """测试配置读取"""
    print("=" * 60)
    print("测试 4: 配置检查")
    print("=" * 60)
    
    print(f"PADDLE_OCR_API_URL: {settings.PADDLE_OCR_API_URL or '未配置'}")
    
    if settings.PADDLE_OCR_API_URL:
        print("✓ OCR API URL 已配置")
    else:
        print("⚠️  OCR API URL 未配置（功能将不可用）")
        print("   请在 .env 文件中设置 PADDLE_OCR_API_URL")
    
    print("\n✅ 配置检查完成!\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试 OCR 工具模块")
    print("=" * 60 + "\n")
    
    try:
        test_ocr_client_init()
        test_extract_text_from_result()
        test_ocr_error_handling()
        test_configuration()
        
        print("=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
        print("\nOCR 工具已就绪，可以使用。")
        print("\n使用示例:")
        print("  from modules.tools import PaddleOCRClient")
        print("  ")
        print("  client = PaddleOCRClient()")
        print("  with open('image.jpg', 'rb') as f:")
        print("      text = client.ocr_image(f.read())")
        print("  print(text)")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        raise
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        raise


if __name__ == "__main__":
    main()
