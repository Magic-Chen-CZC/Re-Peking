#!/usr/bin/env python
"""
新架构快速验证脚本

用于验证新架构的各个组件是否正常工作。
"""
import asyncio
from pathlib import Path

from modules.schemas import RawNote, XHSNote, StoryClip, ArchitectureDoc
from modules.crawlers.xhs_crawler import XHSCrawler
from modules.processors.xhs_processor import XHSProcessor
from modules.vector_store import save_to_db
from utils.logger import logger


async def test_xhs_pipeline():
    """测试 XHS 处理流程"""
    print("\n" + "=" * 60)
    print("测试 1: XHS 数据处理流程")
    print("=" * 60)
    
    # 创建测试数据
    test_note = RawNote(
        url="https://test.com/note1",
        raw_text="故宫太和殿，北京最壮观的建筑之一！#北京打卡 #故宫",
        images=["test.jpg"],
        source="test"
    )
    
    try:
        # 初始化处理器
        processor = XHSProcessor(use_instructor=True)
        
        # 处理笔记
        xhs_note = await processor.process(test_note)
        
        print(f"✅ 处理成功")
        print(f"   ID: {xhs_note.id}")
        print(f"   地点: {xhs_note.location}")
        print(f"   摘要: {xhs_note.summary}")
        print(f"   有效: {xhs_note.valid}")
        
        # 测试保存到向量数据库
        await save_to_db(xhs_note)
        print(f"✅ 成功保存到向量数据库")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_schema_polymorphism():
    """测试 Schema 多态性"""
    print("\n" + "=" * 60)
    print("测试 2: BaseContent 多态性")
    print("=" * 60)
    
    # 创建不同类型的对象
    xhs_note = XHSNote(
        id="xhs_test1",
        text_content="故宫测试内容",
        source_type="xhs",
        summary="故宫打卡",
        location="故宫",
        valid=True,
        metadata={"category": "景点"}
    )
    
    story_clip = StoryClip(
        id="story_test1",
        text_content="白蛇传的故事内容",
        source_type="pdf_legend",
        summary="白蛇传故事",
        story_name="白蛇传",
        is_legend=True,
        metadata={"page": 1}
    )
    
    arch_doc = ArchitectureDoc(
        id="arch_test1",
        text_content="故宫建筑规格说明",
        source_type="pdf_architecture",
        summary="故宫太和殿规格",
        page_number=5,
        technical_specs="高35米",
        metadata={"building": "太和殿"}
    )
    
    # 测试 model_dump
    try:
        xhs_dict = xhs_note.model_dump()
        story_dict = story_clip.model_dump()
        arch_dict = arch_doc.model_dump()
        
        print(f"✅ XHSNote model_dump 成功")
        print(f"   text_content: {xhs_dict['text_content'][:20]}...")
        print(f"   location: {xhs_dict.get('location')}")
        
        print(f"✅ StoryClip model_dump 成功")
        print(f"   story_name: {story_dict.get('story_name')}")
        
        print(f"✅ ArchitectureDoc model_dump 成功")
        print(f"   page_number: {arch_dict.get('page_number')}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_local_data_loading():
    """测试本地数据加载"""
    print("\n" + "=" * 60)
    print("测试 3: 本地 XHS 数据加载")
    print("=" * 60)
    
    # 检查是否存在本地数据文件
    default_path = "data/raw/xhs_manual_collection.json"
    
    if not Path(default_path).exists():
        print(f"⚠️  本地数据文件不存在: {default_path}")
        print(f"   跳过此测试")
        return True
    
    try:
        crawler = XHSCrawler(default_local_path=default_path)
        raw_notes = crawler.load_local_json_data()
        
        print(f"✅ 成功加载 {len(raw_notes)} 条原始数据")
        if raw_notes:
            first_note = raw_notes[0]
            print(f"   第一条 URL: {first_note.url[:50]}...")
            print(f"   文本长度: {len(first_note.raw_text)} 字符")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("🚀 新架构验证测试")
    print("=" * 60)
    
    results = []
    
    # 测试 1: Schema 多态性（不需要 API）
    results.append(("Schema 多态性", test_schema_polymorphism()))
    
    # 测试 2: 本地数据加载（不需要 API）
    results.append(("本地数据加载", test_local_data_loading()))
    
    # 测试 3: XHS 处理流程（需要 DeepSeek API）
    print("\n⚠️  测试 XHS 处理流程需要 DeepSeek API Key")
    print("   如果未配置，测试可能失败")
    input("   按 Enter 继续测试，或 Ctrl+C 取消...")
    results.append(("XHS 处理流程", await test_xhs_pipeline()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
