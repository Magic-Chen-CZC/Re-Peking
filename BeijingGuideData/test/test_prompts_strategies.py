"""
测试 prompts.py 和 strategies.py 集成

本脚本测试新架构的功能：
1. Prompt 注册和检索
2. 策略注册和查找
3. Schema 和 Prompt 的映射关系
4. 数据验证和转换
"""

from modules.prompts import PromptRegistry
from modules.strategies import (
    get_strategy,
    list_strategies,
    validate_strategy,
    apply_strategy,
)
from modules.schemas import XHSNote, StoryClip, ArchitectureDoc


def test_prompt_registry():
    """测试 Prompt 注册表"""
    print("=" * 60)
    print("测试 1: Prompt Registry")
    print("=" * 60)
    
    # 列出所有 Prompt
    keys = PromptRegistry.list_keys()
    print(f"已注册 {len(keys)} 个 Prompt:")
    for key in keys:
        print(f"  ✓ {key}")
    
    # 获取特定 Prompt
    xhs_prompt = PromptRegistry.get("xhs_clean")
    assert xhs_prompt is not None, "XHS Prompt 不应为空"
    print(f"\n✓ XHS Prompt 长度: {len(xhs_prompt)} 字符")
    
    # 测试不存在的 Prompt
    none_prompt = PromptRegistry.get("non_existent")
    assert none_prompt is None, "不存在的 Prompt 应返回 None"
    print("✓ 不存在的 Prompt 正确返回 None")
    
    print("\n✅ Prompt Registry 测试通过!\n")


def test_strategy_registry():
    """测试策略注册表"""
    print("=" * 60)
    print("测试 2: Strategy Registry")
    print("=" * 60)
    
    # 列出所有策略
    strategies = list_strategies()
    print(f"已注册 {len(strategies)} 个策略:")
    for source_type, desc in strategies.items():
        is_valid = validate_strategy(source_type)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {source_type}: {desc}")
    
    # 验证所有策略
    for source_type in strategies.keys():
        assert validate_strategy(source_type), f"{source_type} 策略无效"
    
    print("\n✅ Strategy Registry 测试通过!\n")


def test_strategy_components():
    """测试策略组件"""
    print("=" * 60)
    print("测试 3: Strategy Components")
    print("=" * 60)
    
    # 测试 XHS 策略
    xhs_strategy = get_strategy("xhs")
    assert xhs_strategy is not None, "XHS 策略不应为空"
    assert xhs_strategy.schema == XHSNote, "XHS Schema 不匹配"
    assert xhs_strategy.prompt is not None, "XHS Prompt 不应为空"
    assert "min_content_length" in xhs_strategy.config, "XHS config 缺少配置项"
    print("✓ XHS 策略组件完整")
    
    # 测试 Legend 策略
    legend_strategy = get_strategy("legend")
    assert legend_strategy.schema == StoryClip, "Legend Schema 不匹配"
    print("✓ Legend 策略组件完整")
    
    # 测试 Arch 策略
    arch_strategy = get_strategy("arch")
    assert arch_strategy.schema == ArchitectureDoc, "Arch Schema 不匹配"
    print("✓ Arch 策略组件完整")
    
    # 测试不存在的策略（应返回 generic）
    unknown_strategy = get_strategy("unknown_type")
    assert unknown_strategy is not None, "未知策略应返回 generic"
    assert unknown_strategy.source_type == "generic", "未知策略应降级到 generic"
    print("✓ 未知策略正确降级到 generic")
    
    print("\n✅ Strategy Components 测试通过!\n")


def test_data_validation():
    """测试数据验证"""
    print("=" * 60)
    print("测试 4: Data Validation")
    print("=" * 60)
    
    # 测试 XHS 数据验证
    xhs_data = {
        "source_type": "xhs",
        "id": "xhs_test_001",
        "text_content": "故宫是北京必去的景点之一，拥有悠久的历史...",
        "summary": "详细介绍故宫游玩路线和注意事项",
        "location": "故宫",
        "valid": True,
        "metadata": {
            "url": "https://www.xiaohongshu.com/explore/123456",
            "author": "旅行达人小王",
            "category": "景点",
            "rating": 5
        }
    }
    
    result = apply_strategy("xhs", xhs_data)
    assert result is not None, "XHS 数据验证失败"
    assert isinstance(result, XHSNote), "返回类型不正确"
    assert result.location == "故宫", "地点不匹配"
    print(f"✓ XHS 数据验证通过: {result.location}")
    
    # 测试 Legend 数据
    legend_data = {
        "source_type": "legend",
        "id": "legend_test_001",
        "text_content": "相传元朝时期，为了报时建造了钟鼓楼...",
        "summary": "钟鼓楼建造的历史传说",
        "story_name": "钟鼓楼传说",
        "is_legend": True,
        "metadata": {
            "location": "钟鼓楼",
            "story_type": "建筑典故",
        }
    }
    
    result = apply_strategy("legend", legend_data)
    assert result is not None, "Legend 数据验证失败"
    assert isinstance(result, StoryClip), "返回类型不正确"
    print(f"✓ Legend 数据验证通过: {result.story_name}")
    
    # 测试无效数据
    invalid_data = {
        "source_type": "xhs",
        "id": "invalid_001",
        # 缺少必需字段 text_content, summary, valid
    }
    
    result = apply_strategy("xhs", invalid_data)
    assert result is None, "无效数据应返回 None"
    print("✓ 无效数据正确处理")
    
    print("\n✅ Data Validation 测试通过!\n")


def test_integration():
    """测试完整集成流程"""
    print("=" * 60)
    print("测试 5: Integration Flow")
    print("=" * 60)
    
    # 模拟完整处理流程
    source_type = "xhs"
    
    # 1. 获取策略
    strategy = get_strategy(source_type)
    print(f"1. 获取策略: {strategy.source_type}")
    
    # 2. 获取 Prompt
    prompt = strategy.prompt
    print(f"2. 获取 Prompt: {len(prompt)} 字符")
    
    # 3. 获取 Schema
    schema_class = strategy.schema
    print(f"3. 获取 Schema: {schema_class.__name__}")
    
    # 4. 获取配置
    config = strategy.config
    print(f"4. 获取配置: {len(config)} 项")
    
    # 5. 验证数据
    test_data = {
        "source_type": "xhs",
        "id": "integration_test_001",
        "text_content": "测试内容",
        "summary": "测试摘要",
        "valid": True,
    }
    
    validated_data = schema_class(**test_data)
    print(f"5. 数据验证: {validated_data.id}")
    
    print("\n✅ Integration Flow 测试通过!\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试 Prompts & Strategies 架构")
    print("=" * 60 + "\n")
    
    try:
        test_prompt_registry()
        test_strategy_registry()
        test_strategy_components()
        test_data_validation()
        test_integration()
        
        print("=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
        print("\n架构已成功集成，可以开始使用。")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        raise
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        raise


if __name__ == "__main__":
    main()
