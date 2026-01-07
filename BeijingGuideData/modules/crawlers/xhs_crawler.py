"""
小红书爬虫模块

负责从不同数据源获取小红书笔记的原始数据。
支持本地文件加载和网络爬取两种模式。
"""
import asyncio
import json
from pathlib import Path
from typing import List

from modules.schemas import RawNote
from utils.logger import logger


class XHSCrawler:
    """
    小红书数据采集器
    
    支持多种数据源：
    - Local Mode: 从本地 JSON 文件加载
    - Web Mode: 从网络爬取（待实现）
    """
    
    def __init__(self, default_local_path: str = "data/raw/xhs_manual_collection.json"):
        """
        初始化爬虫
        
        Args:
            default_local_path: 默认的本地数据文件路径
        """
        self.default_local_path = default_local_path
        logger.info(f"XHSCrawler 初始化完成，默认本地数据路径: {default_local_path}")
    
    def load_local_json_data(self, file_path: str = None) -> List[RawNote]:
        """
        Local Mode: 从本地 JSON 文件加载数据并转换为标准格式
        
        这个函数的核心工作是"格式清洗与装箱"：
        - 读取杂乱的 JSON 数据（可能是手动采集的，格式不统一）
        - 统一转换为标准的 RawNote 对象
        - 处理缺失字段、格式异常等问题
        
        Args:
            file_path: JSON 文件路径，如果为 None 则使用默认路径
            
        Returns:
            List[RawNote]: 标准化后的原始笔记列表
            
        Raises:
            FileNotFoundError: 文件不存在时抛出
            json.JSONDecodeError: JSON 格式错误时抛出
        """
        # 使用指定路径或默认路径
        file_path = file_path or self.default_local_path
        
        logger.info(f"[Local Mode] 开始加载本地数据: {file_path}")
        
        # 检查文件是否存在
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"未找到文件: {file_path}")
        
        # 读取 JSON 文件
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        logger.info(f"读取到 {len(raw_data)} 条原始数据")
        
        # 格式清洗与装箱：将杂乱的字典转换为标准的 RawNote 对象
        notes = []
        for idx, item in enumerate(raw_data, 1):
            try:
                # 1. URL处理：优先取 url 字段，如果没有则生成一个本地ID
                url = item.get("url", f"unknown_local_id_{idx}")
                
                # 2. 文本处理 (Raw Text)：拼接所有文本信息
                # 优先使用 raw_text 字段，如果没有则拼接 title 和 desc
                if "raw_text" in item and item["raw_text"]:
                    raw_text = item["raw_text"]
                else:
                    # 拼接标题和正文，用换行符分隔
                    title = item.get("title", "")
                    desc = item.get("desc", "")
                    # 过滤掉空字符串，避免多余的换行
                    parts = [p for p in [title, desc] if p.strip()]
                    raw_text = "\n".join(parts) if parts else "无内容"
                
                # 3. 图片处理：确保 images 字段是列表
                images = item.get("images", [])
                if not isinstance(images, list):
                    # 如果是单个字符串，转换为列表
                    images = [images] if images else []
                
                # 4. 来源标记：统一标记为本地手动采集
                source = "local_manual"
                
                # 5. 创建标准 RawNote 对象
                note = RawNote(
                    url=url,
                    raw_text=raw_text,
                    images=images,
                    source=source
                )
                notes.append(note)
                
                logger.debug(f"成功转换第 {idx} 条数据: {url[:50]}...")
                
            except Exception as e:
                # 转换失败不影响其他数据，记录日志后继续
                logger.warning(f"第 {idx} 条数据转换失败: {str(e)}")
                continue
        
        logger.info(f"[Local Mode] 成功加载 {len(notes)} 条有效数据")
        return notes
    
    async def fetch_from_web(self, keyword: str, limit: int = 10) -> List[RawNote]:
        """
        Web Mode: 从网络爬取数据
        
        这个函数负责调用真实的爬虫逻辑（如 MediaCrawler）来获取数据。
        目前保留接口，后续可以集成实际的爬虫实现。
        
        Args:
            keyword: 搜索关键词
            limit: 抓取数量限制
            
        Returns:
            List[RawNote]: 爬取到的原始笔记列表
            
        TODO:
            - 集成 MediaCrawler 或其他爬虫框架
            - 实现登录认证
            - 处理反爬机制
            - 数据去重
        """
        logger.warning("[Web Mode] 功能尚未完全实现 - 返回 Mock 数据用于测试")
        
        # 模拟网络延迟
        await asyncio.sleep(1)
        
        # 返回 Mock 数据用于测试（后续替换为真实爬虫）
        mock_notes = []
        for i in range(min(limit, 3)):  # 限制 Mock 数据数量
            note = RawNote(
                url=f"https://www.xiaohongshu.com/explore/mock_{keyword}_{i+1}",
                raw_text=f"Mock数据 - 关于{keyword}的笔记内容 #{keyword} #北京打卡",
                images=[f"https://fake-img.com/{keyword}_{i+1}.jpg"],
                source="xhs_mock"
            )
            mock_notes.append(note)
        
        logger.info(f"[Web Mode] 返回 {len(mock_notes)} 条 Mock 数据")
        return mock_notes
    
    async def crawl(self, mode: str = "local", keyword: str = "", limit: int = 10, 
                   file_path: str = None) -> List[RawNote]:
        """
        统一数据采集入口 - 根据模式调度不同的数据源
        
        这是一个工厂模式的实现：
        - 根据 mode 参数决定使用哪种数据采集方式
        - 屏蔽底层实现细节，对外提供统一接口
        - 便于后续扩展新的采集模式（如数据库、API等）
        
        Args:
            mode: 采集模式，可选值：
                  - "local": 从本地 JSON 文件加载
                  - "web": 从网络爬取（需要 keyword 和 limit 参数）
            keyword: 搜索关键词（仅 web 模式需要）
            limit: 抓取数量限制（仅 web 模式需要）
            file_path: 本地文件路径（仅 local 模式可选）
            
        Returns:
            List[RawNote]: 标准化后的原始笔记列表
            
        Raises:
            ValueError: mode 参数不合法时抛出
            
        Example:
            >>> crawler = XHSCrawler()
            
            # 本地模式
            >>> notes = await crawler.crawl(mode="local")
            
            # 网络模式
            >>> notes = await crawler.crawl(mode="web", keyword="北京故宫", limit=20)
        """
        logger.info("=" * 60)
        logger.info(f"开始数据采集 | 模式: {mode.upper()}")
        if mode == "web":
            logger.info(f"参数: 关键词='{keyword}', 数量限制={limit}")
        elif mode == "local" and file_path:
            logger.info(f"参数: 文件路径='{file_path}'")
        logger.info("=" * 60)
        
        # 根据模式调度不同的采集函数
        if mode == "local":
            # Local Mode: 加载本地文件
            notes = self.load_local_json_data(file_path=file_path)
            
        elif mode == "web":
            # Web Mode: 网络爬取
            notes = await self.fetch_from_web(keyword=keyword, limit=limit)
            
        else:
            # 不支持的模式
            error_msg = f"不支持的采集模式: {mode}，可选值为 ['local', 'web']"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 采集结果汇总
        logger.info("=" * 60)
        logger.info(f"数据采集完成 | 共获取 {len(notes)} 条原始数据")
        logger.info("=" * 60)
        
        return notes


# ============================================================================
# 便捷函数：保持向后兼容
# ============================================================================

async def get_xhs_data(mode: str = "local", keyword: str = "", limit: int = 10,
                      file_path: str = None) -> List[RawNote]:
    """
    快捷函数：获取小红书数据
    
    这是一个便捷的包装函数，内部创建 XHSCrawler 实例并调用。
    
    Args:
        mode: 采集模式 ("local" 或 "web")
        keyword: 搜索关键词（web 模式）
        limit: 抓取数量（web 模式）
        file_path: 本地文件路径（local 模式）
        
    Returns:
        List[RawNote]: 原始笔记列表
    """
    crawler = XHSCrawler()
    return await crawler.crawl(mode=mode, keyword=keyword, limit=limit, file_path=file_path)


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_crawler():
        """测试爬虫功能"""
        print("=" * 60)
        print("测试 XHSCrawler")
        print("=" * 60)
        
        crawler = XHSCrawler()
        
        # 测试 Local Mode
        try:
            print("\n[测试 1] Local Mode")
            notes = crawler.load_local_json_data()
            print(f"✓ 加载成功: {len(notes)} 条数据")
            if notes:
                print(f"  第一条: {notes[0].url[:50]}...")
        except FileNotFoundError as e:
            print(f"✗ 文件未找到: {e}")
        
        # 测试 Web Mode
        print("\n[测试 2] Web Mode")
        notes = await crawler.fetch_from_web(keyword="北京故宫", limit=5)
        print(f"✓ 爬取成功: {len(notes)} 条数据")
        if notes:
            print(f"  第一条: {notes[0].url}")
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
    
    asyncio.run(test_crawler())
