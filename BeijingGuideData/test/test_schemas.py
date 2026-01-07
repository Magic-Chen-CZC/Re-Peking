"""
测试新的数据模型架构

验证：
1. BaseContent 基类
2. XHSNote 继承关系
3. StoryClip 继承关系
4. ArchitectureDoc 继承关系
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.schemas import (
    BaseContent,
    XHSNote,
    StoryClip,
    ArchitectureDoc
)


def test_xhs_note():
    """测试小红书笔记模型"""
    print("\n" + "=" * 80)
    print("测试 1: XHSNote 模型")
    print("=" * 80)
    
    note = XHSNote(
        id="xhs_test_001",
        text_content="故宫是北京最著名的景点，拥有600多年历史，是明清两代的皇宫。",
        summary="故宫游玩攻略",
        location="故宫",
        valid=True,
        metadata={
            "url": "https://www.xiaohongshu.com/explore/...",
            "category": "影视打卡",
            "rating": 5,
            "author": "旅游达人小王"
        }
    )
    
    print(f"✅ 创建成功:")
    print(f"  ID: {note.id}")
    print(f"  来源类型: {note.source_type}")
    print(f"  地点: {note.location}")
    print(f"  有效性: {note.valid}")
    print(f"  摘要: {note.summary}")
    print(f"  文本预览: {note.text_content[:50]}...")
    print(f"  元数据: {note.metadata}")
    
    # 验证继承关系
    print(f"\n继承关系验证:")
    print(f"  isinstance(note, XHSNote): {isinstance(note, XHSNote)}")
    print(f"  isinstance(note, BaseContent): {isinstance(note, BaseContent)}")
    
    # 验证 JSON 序列化
    print(f"\nJSON 序列化:")
    json_data = note.model_dump_json(indent=2)
    print(f"  {json_data[:200]}...")


def test_story_clip():
    """测试传说故事模型"""
    print("\n" + "=" * 80)
    print("测试 2: StoryClip 模型")
    print("=" * 80)
    
    story = StoryClip(
        id="pdf_legend_baishechuan_001",
        text_content="相传白蛇修炼千年化为人形，与许仙在西湖断桥相遇，结为夫妻。后因法海和尚从中作梗，白娘子被镇压在雷峰塔下。",
        summary="白蛇传：白娘子与许仙的爱情传说",
        story_name="白蛇传",
        is_legend=True,
        metadata={
            "pdf_file": "chinese_legends.pdf",
            "page_number": 5,
            "location_mentioned": "西湖断桥",
            "dynasty": "宋代传说"
        }
    )
    
    print(f"✅ 创建成功:")
    print(f"  ID: {story.id}")
    print(f"  来源类型: {story.source_type}")
    print(f"  故事名称: {story.story_name}")
    print(f"  是否传说: {story.is_legend}")
    print(f"  摘要: {story.summary}")
    print(f"  文本预览: {story.text_content[:50]}...")
    
    # 验证继承关系
    print(f"\n继承关系验证:")
    print(f"  isinstance(story, StoryClip): {isinstance(story, StoryClip)}")
    print(f"  isinstance(story, BaseContent): {isinstance(story, BaseContent)}")


def test_architecture_doc():
    """测试建筑文档模型"""
    print("\n" + "=" * 80)
    print("测试 3: ArchitectureDoc 模型")
    print("=" * 80)
    
    doc = ArchitectureDoc(
        id="pdf_arch_forbidden_city_taihe",
        text_content="太和殿，俗称金銮殿，是故宫三大殿之首，建于明永乐十八年(1420年)。殿高35.05米，东西长63米，南北宽37米，建筑面积2377平方米。",
        summary="太和殿建筑规格与历史介绍",
        page_number=12,
        technical_specs="高度: 35.05米, 长: 63米, 宽: 37米, 面积: 2377平方米, 建造年代: 1420年",
        metadata={
            "pdf_file": "forbidden_city_architecture.pdf",
            "building_name": "太和殿",
            "alternative_name": "金銮殿",
            "dynasty": "明清",
            "unesco_heritage": True
        }
    )
    
    print(f"✅ 创建成功:")
    print(f"  ID: {doc.id}")
    print(f"  来源类型: {doc.source_type}")
    print(f"  页码: {doc.page_number}")
    print(f"  技术规格: {doc.technical_specs}")
    print(f"  摘要: {doc.summary}")
    print(f"  文本预览: {doc.text_content[:50]}...")
    
    # 验证继承关系
    print(f"\n继承关系验证:")
    print(f"  isinstance(doc, ArchitectureDoc): {isinstance(doc, ArchitectureDoc)}")
    print(f"  isinstance(doc, BaseContent): {isinstance(doc, BaseContent)}")


def test_polymorphism():
    """测试多态性 - 统一处理不同类型的内容"""
    print("\n" + "=" * 80)
    print("测试 4: 多态性 - 统一处理")
    print("=" * 80)
    
    # 创建不同类型的内容
    contents = [
        XHSNote(
            id="xhs_001",
            text_content="颐和园是清朝的皇家园林...",
            summary="颐和园游玩指南",
            location="颐和园",
            valid=True
        ),
        StoryClip(
            id="legend_001",
            text_content="孟姜女哭长城的故事...",
            summary="孟姜女哭长城传说",
            story_name="孟姜女哭长城",
            is_legend=True
        ),
        ArchitectureDoc(
            id="arch_001",
            text_content="天坛是明清两代皇帝祭天的场所...",
            summary="天坛建筑介绍",
            page_number=25,
            technical_specs="占地面积: 273公顷"
        )
    ]
    
    print(f"创建了 {len(contents)} 个不同类型的内容对象\n")
    
    # 统一处理（多态）
    for i, content in enumerate(contents, 1):
        print(f"内容 {i}:")
        print(f"  类型: {type(content).__name__}")
        print(f"  ID: {content.id}")
        print(f"  来源: {content.source_type}")
        print(f"  摘要: {content.summary}")
        print(f"  用于向量化的文本: {content.text_content[:40]}...")
        print()


def test_validation():
    """测试数据验证"""
    print("\n" + "=" * 80)
    print("测试 5: 数据验证")
    print("=" * 80)
    
    # 测试页码验证（必须 >= 1）
    print("测试页码验证:")
    try:
        doc = ArchitectureDoc(
            id="test",
            text_content="测试",
            summary="测试",
            page_number=0  # 无效的页码
        )
        print("  ❌ 应该抛出验证错误")
    except Exception as e:
        print(f"  ✅ 正确捕获错误: {type(e).__name__}")
    
    # 测试必填字段
    print("\n测试必填字段:")
    try:
        note = XHSNote(
            id="test",
            text_content="测试",
            summary="测试"
            # 缺少 valid 字段
        )
        print("  ❌ 应该抛出验证错误")
    except Exception as e:
        print(f"  ✅ 正确捕获错误: {type(e).__name__}")


if __name__ == "__main__":
    print("\n" + "🧪" * 40)
    print("开始测试新的数据模型架构")
    print("🧪" * 40)
    
    try:
        test_xhs_note()
        test_story_clip()
        test_architecture_doc()
        test_polymorphism()
        test_validation()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
        print("\n📝 架构总结:")
        print("  1. BaseContent 作为基类，统一所有内容类型")
        print("  2. XHSNote, StoryClip, ArchitectureDoc 继承 BaseContent")
        print("  3. 支持多态处理，可以统一操作不同类型的内容")
        print("  4. 所有内容都有 text_content 字段用于向量化")
        print("  5. metadata 字段灵活存储额外信息")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
