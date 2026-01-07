"""
PDF 处理器模块

本模块负责 PDF 文档的完整处理流程：
1. 使用 PDFLoader 加载 PDF 全文
2. 使用 SentenceSplitter 切分文本为 Chunk
3. 根据 doc_type 获取对应的处理策略
4. 遍历 Chunk，调用 LLM 进行清洗/提取
5. 返回结构化内容列表 (List[BaseContent])

Usage:
    from modules.processors.pdf_processor import PDFProcessor
    
    # 初始化处理器
    processor = PDFProcessor()
    
    # 处理传说故事 PDF
    results = processor.process_pdf("legends.pdf", doc_type="legend")
    
    # 处理建筑文档 PDF
    results = processor.process_pdf("architecture.pdf", doc_type="arch")
"""

import os
from typing import List, Optional, Dict, Any, Iterable
from pathlib import Path

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from pydantic import ValidationError

from modules.crawlers.pdf_loader import PDFLoader
from modules.domain_config import get_domain_config, get_chunking_config
from modules.schemas import BaseContent, StoryClip, ArchitectureDoc
from modules.qwen_llm import QwenLLM
from utils.logger import logger
from config import settings


class PDFProcessor:
    """
    PDF 文档处理器
    
    支持不同类型的 PDF 文档处理，包括：
    - legend: 传说故事 PDF
    - arch: 建筑文档 PDF
    
    处理流程：
    1. 加载 PDF 全文（使用 PDFLoader）
    2. 文本切分（使用 SentenceSplitter）
    3. 获取处理策略（根据 doc_type）
    4. LLM 清洗和提取（逐 Chunk 处理）
    5. 返回结构化内容列表
    
    Attributes:
        pdf_loader: PDF 加载器实例
        llm: LLM 客户端实例（用于清洗和提取）
        chunk_size: 文本切分块大小（字符数）
        chunk_overlap: 切分块重叠大小（字符数）
    """
    
    def __init__(
        self,
        pdf_loader: Optional[PDFLoader] = None,
        llm: Optional[QwenLLM] = None,
        chunk_size: int = 1024,
        chunk_overlap: int = 128
    ):
        """
        初始化 PDF 处理器
        
        Args:
            pdf_loader: PDF 加载器实例，如果不提供则自动创建
            llm: LLM 客户端实例，如果不提供则自动创建
            chunk_size: 文本切分块大小（建议 512-2048）
            chunk_overlap: 切分块重叠大小（建议 chunk_size 的 10-20%）
        """
        self.pdf_loader = pdf_loader or PDFLoader()
        self.llm = llm or QwenLLM(api_key=settings.QWEN_API_KEY)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化文本切分器
        self.text_splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator="\n"
        )
        
        logger.info(
            f"PDF 处理器已初始化，"
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )
    
    def process_pdf(
        self,
        pdf_path: str,
        doc_type: str,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        save_intermediate: bool = False,
        *,
        custom_strategy: Optional[Dict[str, Any]] = None,
    ) -> List[BaseContent]:
        """
        处理 PDF 文档，返回结构化内容列表

        Args:
            pdf_path: PDF 文件路径
            doc_type: 文档类型（原有逻辑使用 legend/arch；若传入 custom_strategy 可为任意占位值）
            start_page: 起始页码（从 1 开始），None 表示从第一页开始
            end_page: 结束页码（包含），None 表示到最后一页
            save_intermediate: 是否保存中间结果（用于调试）
            custom_strategy: 依赖注入的运行时策略（DOMAIN_CONFIG 兼容结构）。若提供则优先生效。

        Returns:
            结构化内容列表
        """
        # 0. 检查文件是否存在
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            logger.error(f"PDF 文件不存在: {pdf_path}")
            return []

        # 1. 获取处理配置（优先 custom_strategy，保持对旧 doc_type 的兼容）
        domain_config = custom_strategy if custom_strategy is not None else get_domain_config(doc_type)
        if not domain_config:
            logger.error(f"不支持的文档类型: {doc_type}")
            return []

        logger.info(f"开始处理 PDF: {pdf_path}, 类型: {doc_type}")
        logger.info(f"使用策略: {domain_config.get('description', doc_type)}")

        try:
            # 2. 加载 PDF 全文
            full_text = self.pdf_loader.load_pdf_content(
                pdf_path,
                start_page=start_page,
                end_page=end_page
            )
            
            if not full_text or not full_text.strip():
                logger.warning(f"PDF 未提取到文本: {pdf_path}")
                return []
            
            logger.info(f"PDF 全文加载成功，字符数: {len(full_text)}")
            
            # 保存为 Markdown 格式（始终保存，复用已提取的文本）
            logger.info("正在保存 Markdown 格式...")
            md_path = self.pdf_loader.save_as_markdown(
                pdf_path,
                full_text=full_text,  # 传入已提取的文本，避免重复 OCR
                output_dir="data/processed",
                start_page=start_page,
                end_page=end_page
            )
            if md_path:
                logger.info(f"✓ Markdown 已保存: {md_path}")
            
            # 保存全文（如果需要）
            if save_intermediate:
                self._save_text(full_text, pdf_path, "full_text.txt")
            
            # 3. 文本切分（使用配置中的 chunking 参数）
            chunks = self._split_text(full_text, domain_config)
            
            if not chunks:
                logger.warning(f"文本切分失败: {pdf_path}")
                return []
            
            logger.info(f"文本已切分为 {len(chunks)} 个 Chunk")
            
            # 保存切分结果（如果需要）
            if save_intermediate:
                self._save_chunks(chunks, pdf_path)
            
            # 4. 逐 Chunk 处理（调用 LLM 清洗和提取）
            results = self._process_chunks(
                chunks,
                domain_config,
                pdf_path,
                doc_type
            )
            
            logger.info(
                f"PDF 处理完成: {pdf_path}, "
                f"总 Chunk 数: {len(chunks)}, "
                f"有效结果数: {len(results)}"
            )
            
            return results

        except Exception as e:
            logger.error(f"处理 PDF 失败: {pdf_path}, 错误: {str(e)}")
            return []
    
    def _split_text(self, text: str, domain_config: Dict[str, Any]) -> List[str]:
        """
        使用配置中的 chunking 参数切分文本，并预过滤短文本
        
        Args:
            text: 待切分的文本
            domain_config: 业务领域配置（包含 chunking 参数）
            
        Returns:
            切分后的文本块列表（已过滤掉过短的块）
        """
        try:
            # 获取 chunking 配置
            chunking = domain_config.get('chunking', {})
            mode = chunking.get('mode', 'sentence')
            chunk_size = chunking.get('chunk_size', 512)
            overlap = chunking.get('overlap', 64)
            min_length = chunking.get('min_length', 0)
            
            logger.debug(f"切分配置: mode={mode}, size={chunk_size}, overlap={overlap}, min={min_length}")
            
            # 创建 Document 对象
            doc = Document(text=text)
            
            # 根据 mode 选择切分策略
            if mode == 'none':
                # 不切分，整篇文本作为一个块
                chunks = [text]
            else:
                # 使用 SentenceSplitter（支持 sentence 和 markdown 模式）
                # 根据模式设置分隔符
                separator = "\n\n" if mode == "markdown" else "。"
                
                splitter = SentenceSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=overlap,
                    separator=separator
                )
                nodes = splitter.get_nodes_from_documents([doc])
                chunks = [node.text for node in nodes if node.text.strip()]
            
            # 【源头过滤】在这里过滤掉过短的 chunk，避免无效 LLM 调用
            if min_length > 0:
                original_count = len(chunks)
                chunks = [chunk for chunk in chunks if len(chunk) >= min_length]
                filtered_count = original_count - len(chunks)
                if filtered_count > 0:
                    logger.info(f"已过滤 {filtered_count} 个过短的 chunk (< {min_length} 字符)")
            
            return chunks
            
        except Exception as e:
            logger.error(f"文本切分失败: {str(e)}")
            return []
    
    def _process_chunks(
        self,
        chunks: List[str],
        domain_config: Dict[str, Any],
        pdf_path: str,
        doc_type: str
    ) -> List[BaseContent]:
        """
        遍历 Chunk，调用 LLM 进行清洗和提取
        
        支持单个 Chunk 返回多个结果（例如一个文本块包含多个故事）
        
        Args:
            chunks: 文本块列表
            domain_config: 业务领域配置
            pdf_path: PDF 文件路径（用于生成 ID）
            doc_type: 文档类型
            
        Returns:
            结构化内容列表
        """
        results = []
        pdf_name = Path(pdf_path).stem
        
        for i, chunk in enumerate(chunks, start=1):
            logger.info(f"正在处理 Chunk {i}/{len(chunks)}...")
            
            try:
                # 构造 Prompt（结合配置和 Chunk 内容）
                prompt = self._build_prompt(domain_config, chunk)
                
                # 调用 LLM，使用 Iterable 支持多个结果
                # response 现在是一个可迭代对象（列表/生成器）
                response_list = self.llm.generate(
                    prompt=prompt,
                    response_model=Iterable[domain_config['schema']]
                )
                
                if response_list:
                    # 遍历返回的多个结果
                    item_count = 0
                    for item_idx, item in enumerate(response_list, start=1):
                        # 补充元数据
                        if not hasattr(item, 'id') or not item.id:
                            item.id = f"{doc_type}_{pdf_name}_chunk_{i}_item_{item_idx}"
                        
                        if not hasattr(item, 'metadata'):
                            item.metadata = {}
                        
                        item.metadata.update({
                            "pdf_file": pdf_name,
                            "chunk_index": i,
                            "chunk_total": len(chunks),
                            "item_index": item_idx
                        })
                        
                        # 根据 doc_type 判断是否有效
                        if self._is_valid_result(item, domain_config):
                            results.append(item)
                            item_count += 1
                            logger.info(f"Chunk {i} 的第 {item_idx} 个结果有效，已添加")
                        else:
                            logger.info(f"Chunk {i} 的第 {item_idx} 个结果无效，已过滤")
                    
                    logger.info(f"Chunk {i} 处理完成，提取了 {item_count} 个有效结果")
                else:
                    logger.warning(f"Chunk {i} LLM 响应为空")
            
            except ValidationError as e:
                # Pydantic 验证失败：LLM 提取的数据不符合 Schema（如缺少必填字段 location）
                logger.warning(f"Chunk {i} 数据验证失败（LLM 未提取必填字段）: {str(e)}")
                continue
                    
            except Exception as e:
                logger.error(f"处理 Chunk {i} 失败: {str(e)}")
                continue
        
        return results
    
    def _build_prompt(self, domain_config: Dict[str, Any], chunk: str) -> str:
        """
        构造完整的 Prompt（配置中的 Prompt + Chunk 内容）
        
        Args:
            domain_config: 业务领域配置
            chunk: 文本块内容
            
        Returns:
            完整的 Prompt
        """
        base_prompt = domain_config.get('prompt', '')
        
        # 拼接 Chunk 内容
        full_prompt = f"{base_prompt}\n\n【文本内容】\n{chunk}"
        
        return full_prompt
    
    def _is_valid_result(
        self,
        result: BaseContent,
        domain_config: Dict[str, Any]
    ) -> bool:
        """
        判断处理结果是否有效（简化版，主要依赖 Schema 和 Prompt）
        
        职责分离：
        - 必填验证 → Schema (Pydantic 自动校验)
        - 内容筛选 → Prompt (LLM 判断)
        - 长度过滤 → _split_text (源头过滤)
        
        Args:
            result: 处理结果
            domain_config: 业务领域配置
            
        Returns:
            True if 结果有效，False otherwise
        """
        # 检查 valid 字段（通用，由 LLM 在 Prompt 中判断）
        # 注：is_legend 字段仅用于标记内容类型，不作为过滤条件
        # 只要 LLM 判断 valid=True，就保留（包括历史记载和传说故事）
        if hasattr(result, 'valid'):
            is_valid = result.valid
            if not is_valid:
                logger.debug(f"结果被 valid 字段过滤（LLM 判断为无效）")
            return is_valid
        
        # 默认认为有效
        # 注意：location 等必填字段的验证已由 Pydantic 自动完成
        # 如果 LLM 提取不出 location，Pydantic 会抛出 ValidationError，在上层捕获
        return True
    
    def _save_text(self, text: str, pdf_path: str, suffix: str) -> None:
        """
        保存文本到文件（用于调试）
        
        Args:
            text: 文本内容
            pdf_path: PDF 文件路径
            suffix: 文件名后缀
        """
        try:
            pdf_name = Path(pdf_path).stem
            output_path = f"test_data/{pdf_name}_{suffix}"
            
            os.makedirs("test_data", exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            logger.debug(f"文本已保存: {output_path}")
            
        except Exception as e:
            logger.warning(f"保存文本失败: {str(e)}")
    
    def _save_chunks(self, chunks: List[str], pdf_path: str) -> None:
        """
        保存切分后的 Chunk 到文件（用于调试）
        
        Args:
            chunks: 文本块列表
            pdf_path: PDF 文件路径
        """
        try:
            pdf_name = Path(pdf_path).stem
            output_path = f"test_data/{pdf_name}_chunks.txt"
            
            os.makedirs("test_data", exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                for i, chunk in enumerate(chunks, start=1):
                    f.write(f"{'=' * 60}\n")
                    f.write(f"Chunk {i}/{len(chunks)}\n")
                    f.write(f"{'=' * 60}\n")
                    f.write(chunk)
                    f.write("\n\n")
            
            logger.debug(f"Chunk 列表已保存: {output_path}")
            
        except Exception as e:
            logger.warning(f"保存 Chunk 列表失败: {str(e)}")


# ============================================================================
# 批量处理函数
# ============================================================================

def batch_process_pdfs(
    pdf_dir: str,
    doc_type: str,
    output_dir: Optional[str] = None,
    file_pattern: str = "*.pdf"
) -> Dict[str, List[BaseContent]]:
    """
    批量处理目录下的 PDF 文件
    
    Args:
        pdf_dir: PDF 文件目录
        doc_type: 文档类型 (legend, arch)
        output_dir: 结果输出目录（可选）
        file_pattern: 文件匹配模式（默认 *.pdf）
        
    Returns:
        字典: {pdf_filename: List[BaseContent]}
    """
    processor = PDFProcessor()
    results = {}
    
    # 查找所有匹配的 PDF 文件
    pdf_files = list(Path(pdf_dir).glob(file_pattern))
    
    logger.info(f"找到 {len(pdf_files)} 个 PDF 文件")
    
    for pdf_file in pdf_files:
        logger.info(f"正在处理: {pdf_file.name}")
        
        # 处理 PDF
        content_list = processor.process_pdf(
            str(pdf_file),
            doc_type=doc_type
        )
        
        results[pdf_file.name] = content_list
        
        logger.info(f"{pdf_file.name} 处理完成，提取 {len(content_list)} 条内容")
    
    # 保存结果（如果指定了输出目录）
    if output_dir:
        _save_batch_results(results, output_dir)
    
    return results


def _save_batch_results(
    results: Dict[str, List[BaseContent]],
    output_dir: str
) -> None:
    """
    保存批量处理结果到 JSON 文件
    
    Args:
        results: 处理结果字典
        output_dir: 输出目录
    """
    import json
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        for filename, content_list in results.items():
            output_path = os.path.join(
                output_dir,
                f"{Path(filename).stem}_results.json"
            )
            
            # 将 Pydantic 模型转换为字典
            data = [item.model_dump() for item in content_list]
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"结果已保存: {output_path}")
            
    except Exception as e:
        logger.error(f"保存批量结果失败: {str(e)}")


# ============================================================================
# 使用示例和测试
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("PDF 处理器测试")
    print("=" * 60)
    
    # 初始化处理器
    processor = PDFProcessor(chunk_size=1024, chunk_overlap=128)
    
    # 如果提供了测试 PDF 路径和文档类型，进行测试
    if len(sys.argv) > 2:
        test_pdf_path = sys.argv[1]
        doc_type = sys.argv[2]  # legend 或 arch
        
        print(f"\n测试 PDF: {test_pdf_path}")
        print(f"文档类型: {doc_type}")
        
        # 处理 PDF
        print("\n开始处理 PDF...")
        results = processor.process_pdf(
            test_pdf_path,
            doc_type=doc_type,
            save_intermediate=True  # 保存中间结果以便调试
        )
        
        if results:
            print("\n" + "=" * 60)
            print(f"处理完成，提取 {len(results)} 条有效内容")
            print("=" * 60)
            
            # 显示前 3 条结果
            for i, item in enumerate(results[:3], start=1):
                print(f"\n【结果 {i}】")
                print(f"  ID: {item.id}")
                print(f"  类型: {type(item).__name__}")
                print(f"  摘要: {item.summary}")
                if hasattr(item, 'location'):
                    print(f"  地点: {item.location}")
                print(f"  文本长度: {len(item.text_content)} 字符")
            
            if len(results) > 3:
                print(f"\n... 还有 {len(results) - 3} 条结果")
            
            # 保存结果到 JSON
            import json
            output_dir = "test_data"
            os.makedirs(output_dir, exist_ok=True)
            
            pdf_stem = Path(test_pdf_path).stem
            output_path = os.path.join(output_dir, f"{pdf_stem}_results.json")
            
            try:
                data = [item.model_dump() for item in results]
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"\n✅ 结果已保存至: {output_path}")
            except Exception as e:
                print(f"\n❌ 保存结果失败: {str(e)}")

        else:
            print("\n❌ PDF 处理失败或未提取到有效内容")
    else:
        print("\n使用方法:")
        print("  python -m modules.processors.pdf_processor <pdf_path> <doc_type>")
        print("\n参数:")
        print("  pdf_path: PDF 文件路径")
        print("  doc_type: 文档类型，支持 'legend' (传说故事) 或 'arch' (建筑文档)")
        print("\n示例:")
        print("  python -m modules.processors.pdf_processor test_data/legends.pdf legend")
        print("  python -m modules.processors.pdf_processor test_data/architecture.pdf arch")
