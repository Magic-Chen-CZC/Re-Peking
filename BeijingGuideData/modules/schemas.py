"""
数据模型定义模块 - Schemas

架构说明：
- 使用 Pydantic 继承结构，所有内容类型继承自 BaseContent
- BaseContent: 基类，定义所有内容的通用字段
- XHSNote: 小红书笔记数据
- StoryClip: 传说故事片段（来自 PDF）
- ArchitectureDoc: 建筑文档（来自 PDF）
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# ==================== 基础模型 ====================

class BaseContent(BaseModel):
    """
    所有内容的基类
    
    作用：统一不同数据源的数据结构，方便向量化和入库
    
    字段说明：
    - id: 唯一标识，格式建议：{source_type}_{unique_id}
    - text_content: 用于向量化的核心文本内容
    - source_type: 数据源类型，如 "xhs", "pdf_legend", "pdf_architecture"
    - summary: 内容摘要（一句话总结）
    - metadata: 额外元数据（灵活存储其他信息）
    """
    
    id: str = Field(description="唯一标识，格式：{source_type}_{unique_id}")
    text_content: str = Field(description="用于向量化的核心文本内容")
    source_type: str = Field(description="数据源类型，如 xhs, pdf_legend, pdf_architecture")
    summary: str = Field(description="内容摘要（一句话总结）")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="额外元数据（灵活存储其他信息）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "xhs_66fad51c000000001b0224b8",
                "text_content": "故宫是北京最著名的景点...",
                "source_type": "xhs",
                "summary": "故宫游玩攻略",
                "metadata": {"author": "旅游达人", "publish_date": "2024-01-01"}
            }
        }


# ==================== 小红书笔记模型 ====================

class XHSNote(BaseContent):
    """
    小红书笔记数据模型
    
    继承自 BaseContent，添加小红书特有字段
    
    特有字段：
    - location: 地点名称（必填）- Pydantic 自动验证
    - valid: 是否为有效的北京打卡点
    """
    
    # 覆盖 source_type 的默认值
    source_type: str = Field(default="xhs", description="数据源类型，固定为 xhs")
    
    # 小红书特有字段
    location: str = Field(
        description="地点名称（必填，如'故宫'、'颐和园'）"
    )
    valid: bool = Field(
        description="是否为有效的北京打卡点（通过 LLM 判断）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "xhs_66fad51c000000001b0224b8",
                "text_content": "故宫是北京最著名的景点，拥有悠久的历史...",
                "source_type": "xhs",
                "summary": "故宫游玩攻略，适合全家游玩",
                "location": "故宫",
                "valid": True,
                "metadata": {
                    "url": "https://www.xiaohongshu.com/explore/...",
                    "category": "影视打卡",
                    "rating": 5
                }
            }
        }


# ==================== 传说故事片段模型 ====================

class StoryClip(BaseContent):
    """
    传说故事片段数据模型（来自 PDF）
    
    继承自 BaseContent，添加传说故事特有字段
    
    特有字段：
    - story_name: 故事名称（必填）
    - location: 故事发生地点（必填）- Pydantic 自动验证
    - is_legend: 是否为传说故事（区分历史事件和神话传说）
    """
    
    # 覆盖 source_type 的默认值
    source_type: str = Field(
        default="pdf_legend",
        description="数据源类型，固定为 pdf_legend"
    )
    
    # 传说故事特有字段
    story_name: str = Field(
        description="故事名称（必填，如'白蛇传'、'梁祝'、'孟姜女哭长城'）"
    )
    location: str = Field(
        description="故事发生的具体地点（必填，如'雍和宫'、'钟鼓楼'、'什刹海'）"
    )
    is_legend: bool = Field(
        description="是否为传说故事（True=神话传说/民间故事，False=历史事件/真实记载）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "pdf_legend_001_page_5",
                "text_content": "相传白蛇修炼千年化为人形，与许仙在西湖断桥相遇...",
                "source_type": "pdf_legend",
                "summary": "白蛇传：白娘子与许仙的爱情故事",
                "story_name": "白蛇传",
                "location": "西湖断桥",
                "is_legend": True,
                "metadata": {
                    "pdf_file": "chinese_legends.pdf",
                    "page_number": 5
                }
            }
        }


# ==================== 建筑文档模型 ====================

class ArchitectureDoc(BaseContent):
    """
    建筑文档数据模型（来自 PDF）
    
    继承自 BaseContent，添加建筑文档特有字段
    
    特有字段：
    - location: 建筑名称（必填）- Pydantic 自动验证
    - page_number: 页码
    - technical_specs: 技术规格说明（可选）
    """
    
    # 覆盖 source_type 的默认值
    source_type: str = Field(
        default="pdf_architecture",
        description="数据源类型，固定为 pdf_architecture"
    )
    
    # 建筑文档特有字段
    location: str = Field(
        description="建筑名称（必填，如'太和殿'、'天坛祈年殿'、'颐和园佛香阁'）"
    )
    page_number: int = Field(
        ge=1,
        description="PDF 文档页码（从1开始）"
    )
    technical_specs: Optional[str] = Field(
        default=None,
        description="技术规格说明（如建筑尺寸、材料、年代等）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "pdf_arch_forbidden_city_page_12",
                "text_content": "故宫太和殿建于明永乐十八年，高35.05米，是故宫最高的建筑...",
                "source_type": "pdf_architecture",
                "summary": "太和殿建筑规格与历史",
                "location": "太和殿",
                "page_number": 12,
                "technical_specs": "高度: 35.05米, 面积: 2377平方米, 建造年代: 明永乐十八年(1420)",
                "metadata": {
                    "pdf_file": "forbidden_city_architecture.pdf",
                    "dynasty": "明清"
                }
            }
        }


# ==================== 兼容旧架构的模型（可选保留） ====================

class RawNote(BaseModel):
    """
    爬虫采集的原始数据模型（兼容旧版本）
    
    注意：新架构推荐直接使用 XHSNote，此模型仅用于兼容旧代码
    """
    
    url: str = Field(description="笔记链接")
    raw_text: str = Field(description="原始文案内容")
    images: List[str] = Field(default_factory=list, description="图片链接列表")
    source: str = Field(default="xhs", description="数据来源平台")


class ProcessedNote(BaseModel):
    """
    清洗后的成品数据模型（兼容旧版本）
    
    注意：新架构推荐直接使用 XHSNote，此模型仅用于兼容旧代码
    """
    
    url: str = Field(description="笔记链接")
    location: Optional[str] = Field(default=None, description="清洗出的地点名称，允许为空")
    category: str = Field(description="分类，如'影视打卡'、'美食'、'其他'")
    summary: str = Field(description="一句话摘要")
    rating: int = Field(ge=1, le=5, description="推荐指数，1-5分")
    valid: bool = Field(description="是否为有效打卡点")
    metadata: Dict = Field(default_factory=dict, description="保留其他元数据")

