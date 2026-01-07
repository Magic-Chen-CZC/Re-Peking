"""
PDF 内容加载器模块

本模块负责从 PDF 文件中提取文本内容，流程如下：
1. 使用 pdf2image 将 PDF 转换为图片
2. 使用 OCR 工具识别图片中的文字
3. 返回拼接后的全文文本

Usage:
    from modules.crawlers.pdf_loader import PDFLoader
    
    # 初始化加载器
    loader = PDFLoader()
    
    # 加载 PDF 内容
    full_text = loader.load_pdf_content("path/to/document.pdf")
    print(full_text)
"""

import os
from typing import Optional, List
from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image
import io

from modules.tools.ocr_tool import PaddleOCRClient
from utils.logger import logger


class PDFLoader:
    """
    PDF 内容加载器
    
    使用 pdf2image 将 PDF 转为图片，然后通过 OCR 识别文字。
    
    Attributes:
        ocr_client: PaddleOCR 客户端实例
        dpi: PDF 转图片的 DPI 分辨率（越高越清晰，但处理越慢）
    """
    
    def __init__(
        self,
        ocr_client: Optional[PaddleOCRClient] = None,
        dpi: int = 200
    ):
        """
        初始化 PDF 加载器
        
        Args:
            ocr_client: PaddleOCR 客户端实例，如果不提供则自动创建
            dpi: PDF 转图片的 DPI 分辨率，默认 200（建议范围 150-300）
        """
        self.ocr_client = ocr_client or PaddleOCRClient()
        self.dpi = dpi
        
        logger.info(f"PDF 加载器已初始化，DPI={self.dpi}")
    
    def load_pdf_content(
        self,
        pdf_path: str,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        save_images: bool = False,
        output_dir: Optional[str] = None
    ) -> str:
        """
        从 PDF 文件中提取全文文本
        
        流程：
        1. 检查 PDF 文件是否存在
        2. 使用 pdf2image 将 PDF 转换为图片列表
        3. 遍历每张图片，调用 OCR 识别文字
        4. 拼接所有页的文本并返回
        
        Args:
            pdf_path: PDF 文件路径
            start_page: 起始页码（从 1 开始），None 表示从第一页开始
            end_page: 结束页码（包含），None 表示到最后一页
            save_images: 是否保存转换后的图片（用于调试）
            output_dir: 保存图片的目录，仅在 save_images=True 时有效
            
        Returns:
            str: 提取的全文文本，多页内容用双换行符分隔。
                 如果提取失败，返回空字符串。
        """
        # 1. 检查文件是否存在
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            logger.error(f"PDF 文件不存在: {pdf_path}")
            return ""
        
        if not pdf_file.suffix.lower() == ".pdf":
            logger.error(f"文件不是 PDF 格式: {pdf_path}")
            return ""
        
        logger.info(f"开始加载 PDF: {pdf_path}")
        
        try:
            # 2. 将 PDF 转换为图片列表
            images = self._convert_pdf_to_images(
                pdf_path,
                start_page=start_page,
                end_page=end_page
            )
            
            if not images:
                logger.warning(f"PDF 转换图片失败或无内容: {pdf_path}")
                return ""
            
            logger.info(f"PDF 已转换为 {len(images)} 张图片")
            
            # 3. 遍历图片，进行 OCR 识别
            all_texts = []
            for i, image in enumerate(images, start=1):
                page_num = (start_page or 1) + i - 1
                logger.info(f"正在识别第 {page_num} 页 ({i}/{len(images)})...")
                
                # 保存图片（如果需要）
                if save_images and output_dir:
                    self._save_image(image, output_dir, pdf_file.stem, page_num)
                
                # OCR 识别
                text = self._ocr_image(image)
                
                if text.strip():
                    all_texts.append(text)
                    logger.info(f"第 {page_num} 页识别成功，提取 {len(text)} 字符")
                else:
                    logger.warning(f"第 {page_num} 页未识别出文字")
            
            # 4. 拼接所有页的文本（用双换行符分隔）
            full_text = "\n\n".join(all_texts)
            
            logger.info(
                f"PDF 加载完成: {pdf_path}, "
                f"总页数: {len(images)}, "
                f"总字符数: {len(full_text)}"
            )
            
            return full_text
            
        except Exception as e:
            logger.error(f"加载 PDF 失败: {pdf_path}, 错误: {str(e)}")
            return ""
    
    def _convert_pdf_to_images(
        self,
        pdf_path: str,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None
    ) -> List[Image.Image]:
        """
        将 PDF 转换为图片列表
        
        Args:
            pdf_path: PDF 文件路径
            start_page: 起始页码（从 1 开始）
            end_page: 结束页码（包含）
            
        Returns:
            PIL.Image 对象列表
        """
        try:
            # 使用 pdf2image 转换
            # first_page 和 last_page 都是从 1 开始的索引
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                first_page=start_page,
                last_page=end_page,
                fmt='jpeg'  # 使用 JPEG 格式，节省内存
            )
            
            return images
            
        except Exception as e:
            logger.error(f"PDF 转图片失败: {str(e)}")
            return []
    
    def _ocr_image(self, image: Image.Image) -> str:
        """
        对 PIL.Image 对象进行 OCR 识别
        
        Args:
            image: PIL.Image 对象
            
        Returns:
            识别出的文本
        """
        try:
            # 将 PIL.Image 转换为字节流
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # 调用 OCR
            text = self.ocr_client.ocr_image(img_byte_arr, file_type=1)
            
            return text
            
        except Exception as e:
            logger.error(f"OCR 识别失败: {str(e)}")
            return ""
    
    def _save_image(
        self,
        image: Image.Image,
        output_dir: str,
        pdf_name: str,
        page_num: int
    ) -> None:
        """
        保存图片到指定目录
        
        Args:
            image: PIL.Image 对象
            output_dir: 输出目录
            pdf_name: PDF 文件名（不含扩展名）
            page_num: 页码
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 构造文件名
            image_path = os.path.join(
                output_dir,
                f"{pdf_name}_page_{page_num:03d}.jpg"
            )
            
            # 保存图片
            image.save(image_path, 'JPEG', quality=85)
            logger.debug(f"图片已保存: {image_path}")
            
        except Exception as e:
            logger.warning(f"保存图片失败: {str(e)}")
    
    def save_as_markdown(
        self,
        pdf_path: str,
        full_text: Optional[str] = None,
        output_dir: str = "data/processed",
        start_page: Optional[int] = None,
        end_page: Optional[int] = None
    ) -> str:
        """
        将 PDF 转换为 Markdown 格式并保存
        
        Args:
            pdf_path: PDF 文件路径
            full_text: 已提取的 PDF 文本内容（如已提取则直接使用，避免重复 OCR）
            output_dir: Markdown 输出目录，默认为 data/processed
            start_page: 起始页码（从 1 开始）
            end_page: 结束页码（包含）
            
        Returns:
            保存的 Markdown 文件路径，失败则返回空字符串
        """
        # 如果未提供文本，则加载 PDF 内容
        if full_text is None:
            full_text = self.load_pdf_content(
                pdf_path,
                start_page=start_page,
                end_page=end_page
            )
        
        if not full_text:
            logger.warning(f"PDF 未提取到文本，无法生成 Markdown: {pdf_path}")
            return ""
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 构造 Markdown 文件路径
        pdf_file = Path(pdf_path)
        md_filename = f"{pdf_file.stem}.md"
        md_path = os.path.join(output_dir, md_filename)
        
        try:
            # 生成 Markdown 内容
            pdf_name = pdf_file.stem
            page_range = ""
            if start_page or end_page:
                page_range = f" (页码: {start_page or 1}-{end_page or '末页'})"
            
            markdown_content = f"""# {pdf_name}{page_range}

> 来源: {pdf_file.name}  
> 生成时间: {self._get_current_time()}  
> OCR DPI: {self.dpi}

---

{full_text}

---

*本文档由 PaddleOCR 自动识别生成，可能存在识别错误*
"""
            
            # 保存 Markdown 文件
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown 文件已保存: {md_path}")
            logger.info(f"文件大小: {len(markdown_content)} 字符")
            
            return md_path
            
        except Exception as e:
            logger.error(f"保存 Markdown 文件失败: {str(e)}")
            return ""
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def load_pdf_pages(
        self,
        pdf_path: str,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None
    ) -> List[str]:
        """
        加载 PDF 的每一页文本，返回文本列表（每页一个元素）
        
        与 load_pdf_content 的区别：
        - load_pdf_content: 返回拼接后的全文（单个字符串）
        - load_pdf_pages: 返回每页文本的列表（List[str]）
        
        Args:
            pdf_path: PDF 文件路径
            start_page: 起始页码（从 1 开始）
            end_page: 结束页码（包含）
            
        Returns:
            每页文本的列表，如果提取失败返回空列表
        """
        # 检查文件
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            logger.error(f"PDF 文件不存在: {pdf_path}")
            return []
        
        try:
            # 转换为图片
            images = self._convert_pdf_to_images(pdf_path, start_page, end_page)
            
            if not images:
                return []
            
            # OCR 识别每一页
            page_texts = []
            for i, image in enumerate(images, start=1):
                page_num = (start_page or 1) + i - 1
                logger.info(f"正在识别第 {page_num} 页...")
                
                text = self._ocr_image(image)
                page_texts.append(text)
            
            logger.info(f"PDF 加载完成: {pdf_path}, 总页数: {len(page_texts)}")
            return page_texts
            
        except Exception as e:
            logger.error(f"加载 PDF 分页内容失败: {pdf_path}, 错误: {str(e)}")
            return []


# ============================================================================
# 使用示例和测试
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("PDF 加载器测试")
    print("=" * 60)
    
    # 初始化加载器
    loader = PDFLoader(dpi=200)
    
    # 如果提供了测试 PDF 路径，进行测试
    if len(sys.argv) > 1:
        test_pdf_path = sys.argv[1]
        print(f"\n测试 PDF: {test_pdf_path}")
        
        # 加载全文
        print("\n开始加载 PDF 内容...")
        full_text = loader.load_pdf_content(
            test_pdf_path,
            save_images=True,  # 保存图片以便调试
            output_dir="test_data/pdf_images"
        )
        
        if full_text:
            print("\n" + "=" * 60)
            print("提取的文本内容（前 500 字符）:")
            print("=" * 60)
            print(full_text[:500])
            print("=" * 60)
            print(f"\n✓ 加载成功，总字符数: {len(full_text)}")
            
            # 保存到文本文件
            output_path = test_pdf_path + ".txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"✓ 文本已保存到: {output_path}")
        else:
            print("\n❌ PDF 加载失败或未提取到文本")
    else:
        print("\n使用方法:")
        print("  python -m modules.crawlers.pdf_loader <pdf_path>")
        print("\n示例:")
        print("  python -m modules.crawlers.pdf_loader test_data/document.pdf")
