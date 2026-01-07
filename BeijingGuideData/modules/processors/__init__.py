"""
Processors 模块

包含各种数据源的处理器实现。
"""

from modules.processors.xhs_processor import (
    XHSProcessor,
    process_xhs_note,
    process_xhs_notes_batch
)
from modules.processors.pdf_processor import (
    PDFProcessor,
    batch_process_pdfs
)

__all__ = [
    "XHSProcessor",
    "process_xhs_note",
    "process_xhs_notes_batch",
    "PDFProcessor",
    "batch_process_pdfs",
]
