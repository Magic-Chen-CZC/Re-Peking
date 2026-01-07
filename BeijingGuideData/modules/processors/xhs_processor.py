"""
小红书数据处理器

负责将原始的小红书笔记数据清洗、结构化为标准的 XHSNote 格式。
使用统一的业务配置模式，从 domain_config.py 获取 Schema 和 Prompt。
"""
import instructor
from openai import OpenAI
from typing import Optional

from config import settings
from modules.schemas import RawNote, XHSNote
from modules.domain_config import get_domain_config
from utils.logger import logger


class XHSProcessor:
    """
    小红书笔记处理器
    
    使用 LLM 将原始笔记数据清洗并结构化为 XHSNote 格式。
    通过策略模式获取处理配置（Schema + Prompt）。
    """
    
    def __init__(self, use_instructor: bool = True):
        """
        初始化处理器
        
        Args:
            use_instructor: 是否使用 instructor 库进行结构化输出
                          True: 使用 instructor + DeepSeek（推荐）
                          False: 使用原生 Qwen LLM
        """
        self.use_instructor = use_instructor
        
        # 获取 XHS 业务配置
        self.domain_config = get_domain_config("xhs")
        if not self.domain_config:
            logger.error("未找到 XHS 业务配置")
            raise ValueError("XHS domain config not found")
        
        logger.info(f"XHSProcessor 初始化完成")
        logger.info(f"  使用 Schema: {self.domain_config['schema'].__name__}")
        logger.info(f"  Chunking: {self.domain_config['chunking']}")
        logger.info(f"  使用 Instructor: {use_instructor}")
        
        # 初始化 LLM 客户端
        if use_instructor:
            # 使用 instructor + DeepSeek（结构化输出）
            self.client = instructor.from_openai(
                OpenAI(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url=settings.DEEPSEEK_BASE_URL
                )
            )
            self.model = settings.DEEPSEEK_MODEL
            logger.info(f"  LLM: DeepSeek ({self.model})")
        else:
            # 使用 Qwen LLM（原生）
            self.client = OpenAI(
                api_key=settings.DASHSCOPE_API_KEY,
                base_url=settings.QWEN_BASE_URL
            )
            self.model = settings.QWEN_MODEL
            logger.info(f"  LLM: Qwen ({self.model})")
    
    async def process(self, note: RawNote) -> XHSNote:
        """
        处理单条小红书笔记
        
        Args:
            note: 原始笔记数据（RawNote）
            
        Returns:
            XHSNote: 清洗后的结构化数据
            
        Raises:
            Exception: 处理失败时抛出
        """
        try:
            logger.info(f"开始处理笔记: {note.url}")
            
            # 获取业务配置的 Prompt
            system_prompt = self.domain_config['prompt']
            if not system_prompt:
                logger.warning("配置中未找到 Prompt，使用默认 Prompt")
                system_prompt = "你是北京资深导游。请分析这篇小红书笔记，提取地点、摘要，并判断是否值得打卡。"
            
            # 调用 LLM 进行结构化提取
            if self.use_instructor:
                # 使用 instructor 自动解析为 XHSNote
                result = self._process_with_instructor(note, system_prompt)
            else:
                # 使用原生 LLM + 手动解析
                result = await self._process_with_native_llm(note, system_prompt)
            
            # 构建 XHSNote 对象
            xhs_note = self._build_xhs_note(note, result)
            
            logger.info(
                f"处理成功: {note.url[:50]}... | "
                f"地点: {xhs_note.location}, 有效: {xhs_note.valid}"
            )
            
            return xhs_note
            
        except Exception as e:
            logger.error(f"处理失败 {note.url}: {str(e)}")
            
            # 返回一个无效的默认对象，避免程序崩溃
            return self._build_fallback_note(note, error=str(e))
    
    def _process_with_instructor(self, note: RawNote, system_prompt: str) -> dict:
        """
        使用 instructor 库进行结构化输出
        
        Args:
            note: 原始笔记
            system_prompt: 系统提示词
            
        Returns:
            dict: LLM 返回的结构化数据
        """
        # 直接使用 domain_config 中定义的 Schema
        schema_class = self.domain_config['schema']
        
        # 调用 instructor（直接返回 XHSNote 对象）
        extraction = self.client.chat.completions.create(
            model=self.model,
            response_model=schema_class,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": note.raw_text}
            ],
        )
        
        # 转换为字典
        return extraction.model_dump()
    
    async def _process_with_native_llm(self, note: RawNote, system_prompt: str) -> dict:
        """
        使用原生 LLM + JSON 解析
        
        Args:
            note: 原始笔记
            system_prompt: 系统提示词
            
        Returns:
            dict: 解析后的结构化数据
        """
        import json
        
        # 构建 JSON 格式的提示
        enhanced_prompt = system_prompt + "\n\n请以 JSON 格式返回，包含以下字段：\n"
        enhanced_prompt += "{\n"
        enhanced_prompt += '  "location": "地点名称（如果有）",\n'
        enhanced_prompt += '  "summary": "内容摘要",\n'
        enhanced_prompt += '  "valid": true/false,\n'
        enhanced_prompt += '  "category": "分类",\n'
        enhanced_prompt += '  "rating": 1-5\n'
        enhanced_prompt += "}"
        
        # 调用 LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": enhanced_prompt},
                {"role": "user", "content": note.raw_text}
            ],
            temperature=0.3,  # 降低温度以获得更稳定的输出
        )
        
        # 提取响应文本
        content = response.choices[0].message.content
        
        # 尝试解析 JSON
        try:
            # 移除可能的 markdown 代码块标记
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 解析失败: {e}, 使用默认值")
            return {
                "location": None,
                "summary": content[:200] if content else "解析失败",
                "valid": False,
                "category": "其他",
                "rating": 1
            }
    
    def _build_xhs_note(self, note: RawNote, extraction: dict) -> XHSNote:
        """
        根据提取结果构建 XHSNote 对象
        
        Args:
            note: 原始笔记
            extraction: LLM 提取的结构化数据
            
        Returns:
            XHSNote: 标准化的小红书笔记对象
        """
        # 生成 ID（基于 URL 的 hash）
        import hashlib
        note_id = f"xhs_{hashlib.md5(note.url.encode()).hexdigest()[:16]}"
        
        # 构建 XHSNote
        xhs_note = XHSNote(
            id=note_id,
            text_content=note.raw_text,
            source_type="xhs",
            summary=extraction.get("summary", "无摘要"),
            location=extraction.get("location"),
            valid=extraction.get("valid", False),
            metadata={
                "url": note.url,
                "images": note.images,
                "source": note.source,
                "category": extraction.get("category", "其他"),
                "rating": extraction.get("rating", 3),
            }
        )
        
        return xhs_note
    
    def _build_fallback_note(self, note: RawNote, error: str) -> XHSNote:
        """
        构建失败时的默认对象
        
        Args:
            note: 原始笔记
            error: 错误信息
            
        Returns:
            XHSNote: 标记为无效的默认对象
        """
        import hashlib
        note_id = f"xhs_{hashlib.md5(note.url.encode()).hexdigest()[:16]}"
        
        return XHSNote(
            id=note_id,
            text_content=note.raw_text,
            source_type="xhs",
            summary="数据处理失败",
            location=None,
            valid=False,
            metadata={
                "url": note.url,
                "images": note.images,
                "source": note.source,
                "error": error,
                "category": "其他",
                "rating": 1,
            }
        )
    
    async def process_batch(self, notes: list[RawNote]) -> list[XHSNote]:
        """
        批量处理笔记
        
        Args:
            notes: 原始笔记列表
            
        Returns:
            list[XHSNote]: 处理后的笔记列表
        """
        logger.info(f"开始批量处理 {len(notes)} 条笔记")
        
        results = []
        for i, note in enumerate(notes, 1):
            try:
                xhs_note = await self.process(note)
                results.append(xhs_note)
                logger.info(f"进度: {i}/{len(notes)}")
            except Exception as e:
                logger.error(f"批量处理第 {i} 条失败: {e}")
                # 添加失败的默认对象
                fallback = self._build_fallback_note(note, error=str(e))
                results.append(fallback)
        
        logger.info(f"批量处理完成，成功 {len(results)} 条")
        return results


# ============================================================================
# 便捷函数：保持向后兼容
# ============================================================================

async def process_xhs_note(note: RawNote, use_instructor: bool = True) -> XHSNote:
    """
    快捷函数：处理单条小红书笔记
    
    Args:
        note: 原始笔记
        use_instructor: 是否使用 instructor
        
    Returns:
        XHSNote: 处理后的笔记
    """
    processor = XHSProcessor(use_instructor=use_instructor)
    return await processor.process(note)


async def process_xhs_notes_batch(notes: list[RawNote], 
                                  use_instructor: bool = True) -> list[XHSNote]:
    """
    快捷函数：批量处理小红书笔记
    
    Args:
        notes: 原始笔记列表
        use_instructor: 是否使用 instructor
        
    Returns:
        list[XHSNote]: 处理后的笔记列表
    """
    processor = XHSProcessor(use_instructor=use_instructor)
    return await processor.process_batch(notes)


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_processor():
        """测试处理器功能"""
        print("=" * 60)
        print("测试 XHSProcessor")
        print("=" * 60)
        
        # 创建测试数据
        test_note = RawNote(
            url="https://www.xiaohongshu.com/explore/test123",
            raw_text="""终于打卡了《邪不压正》的屋顶！
            就在东四六条附近，夕阳绝美，李天然同款机位！
            #北京 #影视打卡 #邪不压正""",
            images=["https://fake-img.com/roof.jpg"],
            source="test"
        )
        
        # 测试处理
        processor = XHSProcessor(use_instructor=True)
        result = await processor.process(test_note)
        
        print("\n处理结果:")
        print(f"  ID: {result.id}")
        print(f"  地点: {result.location}")
        print(f"  摘要: {result.summary}")
        print(f"  有效: {result.valid}")
        print(f"  分类: {result.metadata.get('category')}")
        print(f"  评分: {result.metadata.get('rating')}")
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
    
    asyncio.run(test_processor())
