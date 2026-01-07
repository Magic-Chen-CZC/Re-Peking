"""
工具模块

本模块包含各种工具类和函数，包括：
- OCR 文字识别
- PDF 处理
- 图像处理
- 其他辅助工具
"""

from modules.tools.ocr_tool import PaddleOCRClient

__all__ = [
    "PaddleOCRClient",
]
