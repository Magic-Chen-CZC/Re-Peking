"""
通义千问（Qwen）嵌入模型的 LlamaIndex 集成
"""
from typing import Any, List

import dashscope
from llama_index.core.base.embeddings.base import BaseEmbedding
from pydantic import Field


class QwenEmbedding(BaseEmbedding):
    """通义千问嵌入模型"""
    
    api_key: str = Field(description="DashScope API Key")
    model_name: str = Field(default="text-embedding-v4", description="模型名称")
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "text-embedding-v4",
        **kwargs: Any
    ):
        """
        初始化 Qwen 嵌入模型
        
        Args:
            api_key: DashScope API Key
            model_name: 模型名称，默认 text-embedding-v4
        """
        super().__init__(api_key=api_key, model_name=model_name, **kwargs)
        # 设置 dashscope 的全局 API Key
        dashscope.api_key = api_key
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """
        获取查询文本的嵌入向量
        
        Args:
            query: 查询文本
            
        Returns:
            嵌入向量
        """
        resp = dashscope.TextEmbedding.call(
            model=self.model_name,
            input=query
        )
        
        if resp.status_code == 200:
            return resp.output['embeddings'][0]['embedding']
        else:
            raise RuntimeError(f"Qwen Embedding 调用失败: {resp.message}")
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """
        获取文本的嵌入向量
        
        Args:
            text: 文本
            
        Returns:
            嵌入向量
        """
        return self._get_query_embedding(text)
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        """异步获取查询嵌入（当前使用同步实现）"""
        return self._get_query_embedding(query)
    
    async def _aget_text_embedding(self, text: str) -> List[float]:
        """异步获取文本嵌入（当前使用同步实现）"""
        return self._get_text_embedding(text)
