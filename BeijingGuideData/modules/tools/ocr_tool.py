"""
OCR 工具模块

本模块提供 PaddleOCR 图像文字识别功能，支持调用 PaddleOCR API 服务。

Usage:
    from modules.tools.ocr_tool import PaddleOCRClient
    
    # 初始化客户端
    ocr_client = PaddleOCRClient()
    
    # 识别图片
    with open("image.jpg", "rb") as f:
        image_data = f.read()
    text = ocr_client.ocr_image(image_data)
    print(text)
"""

import base64
import requests
from typing import Optional, Dict, Any

from config import settings
from utils.logger import logger


class PaddleOCRClient:
    """
    PaddleOCR 客户端
    
    用于调用 PaddleOCR API 服务进行图像文字识别。
    
    Attributes:
        api_url: PaddleOCR API 地址
        token: API 访问令牌（从 API_URL 中提取）
    """
    
    def __init__(self, api_url: Optional[str] = None, token: Optional[str] = None):
        """
        初始化 PaddleOCR 客户端
        
        Args:
            api_url: PaddleOCR API 地址，如果不提供则从 settings 中读取
            token: API 访问令牌，如果不提供则从 settings 中读取
        """
        self.api_url = api_url or settings.PADDLE_OCR_API_URL
        self.token = token or getattr(settings, "PADDLE_OCR_TOKEN", "")
        
        if not self.api_url:
            logger.warning("PADDLE_OCR_API_URL 未配置，OCR 功能将不可用")
        if not self.token:
            logger.warning("PADDLE_OCR_TOKEN 未配置，可能无法访问 API")
    
    def ocr_image(
        self,
        image_data: bytes,
        file_type: int = 1,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
        use_textline_orientation: bool = False
    ) -> str:
        """
        对图像进行 OCR 识别，提取文本内容
        
        Args:
            image_data: 图像的二进制数据
            file_type: 文件类型，0=PDF文档，1=图片（默认）
            use_doc_orientation_classify: 是否使用文档方向分类
            use_doc_unwarping: 是否使用文档矫正
            use_textline_orientation: 是否使用文本行方向检测
            
        Returns:
            str: 识别出的所有文本内容，多行文本用换行符分隔。
                 如果识别失败或未配置 API，返回空字符串。
        """
        # 检查 API URL 配置
        if not self.api_url:
            logger.error("PADDLE_OCR_API_URL 未配置，无法进行 OCR 识别")
            return ""
        
        try:
            logger.info("开始调用 PaddleOCR API 进行图像识别")
            
            # 将图像数据编码为 base64
            file_data = base64.b64encode(image_data).decode("ascii")
            
            # 构造请求头
            headers = {
                "Content-Type": "application/json"
            }
            
            # 如果提供了 token，添加到请求头
            if self.token:
                headers["Authorization"] = f"token {self.token}"
            
            # 构造请求体
            payload = {
                "file": file_data,
                "fileType": file_type,
                "useDocOrientationClassify": use_doc_orientation_classify,
                "useDocUnwarping": use_doc_unwarping,
                "useTextlineOrientation": use_textline_orientation,
            }
            
            # 发送 POST 请求（增加超时时间到 120 秒，因为 PDF 处理可能较慢）
            logger.debug(f"发送 OCR 请求到: {self.api_url}")
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=120  # 120秒超时，适合大文件
            )
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(
                    f"PaddleOCR API 请求失败，状态码: {response.status_code}, "
                    f"响应: {response.text}"
                )
                return ""
            
            # 解析响应
            result = response.json()
            
            # 提取 OCR 结果
            extracted_text = self._extract_text_from_result(result)
            
            logger.info(f"OCR 识别成功，提取文本长度: {len(extracted_text)} 字符")
            return extracted_text
            
        except requests.exceptions.Timeout:
            logger.error("PaddleOCR API 请求超时")
            return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"PaddleOCR API 请求异常: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"OCR 识别过程发生错误: {str(e)}")
            return ""
    
    def _extract_text_from_result(self, result: Dict[str, Any]) -> str:
        """
        从 PaddleOCR API 响应中提取文本内容
        
        Args:
            result: PaddleOCR API 返回的 JSON 结果
            
        Returns:
            str: 提取的文本内容，多行文本用换行符分隔
        """
        try:
            # 根据 PaddleOCR API 文档，结果在 result.result.ocrResults 中
            ocr_results = result.get("result", {}).get("ocrResults", [])
            
            if not ocr_results:
                logger.warning("OCR 结果为空，未识别出任何文本")
                return ""
            
            # 提取所有识别结果中的文本
            all_texts = []
            for i, res in enumerate(ocr_results):
                # prunedResult 是一个字典，包含 rec_texts 字段
                pruned_result = res.get("prunedResult", {})
                
                if isinstance(pruned_result, dict):
                    # 从 rec_texts 字段中提取文本列表
                    rec_texts = pruned_result.get("rec_texts", [])
                    if isinstance(rec_texts, list):
                        # 将列表中的所有文本添加到结果中
                        for text in rec_texts:
                            if isinstance(text, str) and text.strip():
                                all_texts.append(text.strip())
                        logger.debug(f"OCR 结果 {i + 1}: 提取 {len(rec_texts)} 行文本")
                elif isinstance(pruned_result, str):
                    # 如果 prunedResult 是字符串（旧版本API格式）
                    if pruned_result.strip():
                        all_texts.append(pruned_result.strip())
                        logger.debug(f"OCR 结果 {i + 1}: {len(pruned_result)} 字符")
            
            # 用换行符拼接所有文本
            combined_text = "\n".join(all_texts)
            logger.debug(f"总共提取 {len(all_texts)} 行，{len(combined_text)} 字符")
            return combined_text
            
        except Exception as e:
            logger.error(f"解析 OCR 结果时发生错误: {str(e)}")
            logger.debug(f"原始结果结构: {result}")
            return ""
    
    def ocr_image_with_details(
        self,
        image_data: bytes,
        file_type: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        对图像进行 OCR 识别，返回详细结果（包含位置信息等）
        
        Args:
            image_data: 图像的二进制数据
            file_type: 文件类型，0=PDF文档，1=图片（默认）
            **kwargs: 其他可选参数
            
        Returns:
            Dict: 完整的 OCR 结果字典，包含文本、位置、置信度等信息。
                  如果识别失败，返回空字典。
        """
        if not self.api_url:
            logger.error("PADDLE_OCR_API_URL 未配置，无法进行 OCR 识别")
            return {}
        
        try:
            logger.info("开始调用 PaddleOCR API 进行详细识别")
            
            # 将图像数据编码为 base64
            file_data = base64.b64encode(image_data).decode("ascii")
            
            # 构造请求
            headers = {
                "Content-Type": "application/json"
            }
            if self.token:
                headers["Authorization"] = f"token {self.token}"
            
            payload = {
                "file": file_data,
                "fileType": file_type,
                **kwargs
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"PaddleOCR API 请求失败，状态码: {response.status_code}")
                return {}
            
            result = response.json()
            logger.info("OCR 详细识别成功")
            return result
            
        except Exception as e:
            logger.error(f"OCR 详细识别失败: {str(e)}")
            return {}


# ============================================================================
# 使用示例和测试
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("PaddleOCR 客户端测试")
    print("=" * 60)
    
    # 初始化客户端
    ocr_client = PaddleOCRClient()
    
    # 检查配置
    if not ocr_client.api_url:
        print("❌ PADDLE_OCR_API_URL 未配置")
        print("请在 .env 文件中设置 PADDLE_OCR_API_URL")
        sys.exit(1)
    
    print(f"✓ API URL: {ocr_client.api_url}")
    
    # 如果提供了测试图片路径，进行测试
    if len(sys.argv) > 1:
        test_image_path = sys.argv[1]
        print(f"\n测试图片: {test_image_path}")
        
        try:
            with open(test_image_path, "rb") as f:
                image_data = f.read()
            
            print(f"图片大小: {len(image_data)} 字节")
            print("\n开始 OCR 识别...")
            
            # 进行 OCR 识别
            text = ocr_client.ocr_image(image_data)
            
            if text:
                print("\n" + "=" * 60)
                print("识别结果:")
                print("=" * 60)
                print(text)
                print("=" * 60)
                print(f"\n✓ 识别成功，提取 {len(text)} 字符")
            else:
                print("\n❌ OCR 识别失败或未识别出文本")
                
        except FileNotFoundError:
            print(f"❌ 文件不存在: {test_image_path}")
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    else:
        print("\n使用方法:")
        print("  python -m modules.tools.ocr_tool <image_path>")
        print("\n示例:")
        print("  python -m modules.tools.ocr_tool test_image.jpg")
