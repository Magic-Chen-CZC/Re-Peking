"""
通义千问（Qwen）LLM 的 LlamaIndex 集成
"""
import instructor
from typing import Any, List, Optional, Type
from pydantic import Field, BaseModel

from llama_index.core.base.llms.types import ChatMessage, ChatResponse, ChatResponseGen, CompletionResponse, CompletionResponseGen, LLMMetadata
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback
from llama_index.core.llms.custom import CustomLLM
from openai import OpenAI


class QwenLLM(CustomLLM):
    """通义千问 LLM"""
    
    api_key: str = Field(description="DashScope API Key")
    model_name: str = Field(default="qwen-plus", description="模型名称")
    base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", description="API Base URL")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=2000, description="最大生成长度")
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "qwen-plus",
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any
    ):
        """
        初始化 Qwen LLM
        
        Args:
            api_key: DashScope API Key
            model_name: 模型名称，默认 qwen-plus
            base_url: API Base URL
            temperature: 温度参数
            max_tokens: 最大生成长度
        """
        super().__init__(
            api_key=api_key,
            model_name=model_name,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        self._client = OpenAI(api_key=api_key, base_url=base_url)
    
    def generate(self, prompt: str, response_model: Any) -> Any:
        """
        生成结构化数据
        
        Args:
            prompt: 提示词
            response_model: 响应模型类 (Pydantic Model)
            
        Returns:
            结构化数据实例
        """
        import instructor
        
        # 使用 instructor 包装 client
        client = instructor.from_openai(self._client)
        
        try:
            # 调用 API 生成结构化数据
            # 注意：instructor 默认不支持一次返回多个对象，如果需要返回列表，需要包装在另一个模型中
            # 这里我们假设每次只返回一个对象，或者 prompt 引导 LLM 返回单个对象
            response = client.chat.completions.create(
                model=self.model_name,
                response_model=response_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response
            
        except Exception as e:
            # 处理 instructor 不支持多工具调用的错误
            if "Instructor does not support multiple tool calls" in str(e):
                from utils.logger import logger
                logger.warning(f"LLM 尝试返回多个结果，正在重试以获取单个结果: {str(e)}")
                
                # 尝试修改 prompt 强制返回单个结果
                single_prompt = prompt + "\n\n请只返回一个最相关的结果，不要返回列表。"
                try:
                    response = client.chat.completions.create(
                        model=self.model_name,
                        response_model=response_model,
                        messages=[
                            {"role": "user", "content": single_prompt}
                        ],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                    )
                    return response
                except Exception as retry_e:
                    logger.error(f"重试失败: {str(retry_e)}")
                    return None
            
            # 记录其他错误并返回 None
            from utils.logger import logger
            logger.error(f"LLM 生成失败: {str(e)}")
            return None

    @property
    def metadata(self) -> LLMMetadata:
        """获取 LLM 元数据"""
        return LLMMetadata(
            context_window=8192,
            num_output=self.max_tokens,
            model_name=self.model_name,
        )
    
    @llm_chat_callback()
    def chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        """
        Chat 接口
        
        Args:
            messages: 消息列表
            
        Returns:
            ChatResponse: 聊天响应
        """
        # 转换消息格式
        openai_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
        
        # 调用 API
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=openai_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        )
        
        return ChatResponse(
            message=ChatMessage(
                role="assistant",
                content=response.choices[0].message.content
            ),
            raw=response.model_dump()
        )
    
    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """
        Completion 接口
        
        Args:
            prompt: 提示词
            
        Returns:
            CompletionResponse: 完成响应
        """
        # 过滤掉 LlamaIndex 特有的参数
        kwargs.pop('formatted', None)
        
        # 使用 chat 接口实现 completion
        messages = [{"role": "user", "content": prompt}]
        
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        )
        
        return CompletionResponse(
            text=response.choices[0].message.content,
            raw=response.model_dump()
        )
    
    @llm_chat_callback()
    def stream_chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponseGen:
        """流式 Chat（当前使用非流式实现）"""
        response = self.chat(messages, **kwargs)
        yield response
    
    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        """流式 Completion（当前使用非流式实现）"""
        response = self.complete(prompt, **kwargs)
        yield response
