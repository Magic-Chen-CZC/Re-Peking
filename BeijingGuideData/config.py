from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """项目全局配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # ==================== 必填字段 ====================
    DEEPSEEK_API_KEY: str
    DASHSCOPE_API_KEY: str  # 阿里云通义千问 API Key
    QWEN_API_KEY: str  # 新增：Qwen LLM API Key，可从 .env 加载
    
    # ==================== LLM 相关配置 ====================
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-plus"  # 通义千问 LLM 模型
    EMBEDDING_MODEL: str = "text-embedding-v4"  # 通义千问嵌入模型
    
    # ==================== 数据库配置 ====================
    DB_PATH: str = "data/chroma_db"
    
    # ==================== OCR 配置 ====================
    PADDLE_OCR_API_URL: str = "https://7395p7b8bfv811sd.aistudio-app.com/ocr"  # PaddleOCR API 地址（如果为空则使用本地模式）
    PADDLE_OCR_TOKEN: str = "404a433676ab6d5224a0f297c302142d6f690e50"     # PaddleOCR API 访问令牌
    
    # ==================== 日志和爬取配置 ====================
    LOG_LEVEL: str = "INFO"
    CRAWL_LIMIT: int = 10


# 实例化全局配置对象
settings = Settings()
