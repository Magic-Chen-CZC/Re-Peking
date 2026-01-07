import chromadb
from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import settings
from modules.qwen_embedding import QwenEmbedding
from modules.schemas import BaseContent
from utils.logger import logger

# 初始化全局 Qwen Embedding 模型
Settings.embed_model = QwenEmbedding(
    api_key=settings.DASHSCOPE_API_KEY,
    model_name=settings.EMBEDDING_MODEL
)

# 初始化 ChromaDB 持久化客户端
chroma_client = chromadb.PersistentClient(path=settings.DB_PATH)

# 获取或创建集合
chroma_collection = chroma_client.get_or_create_collection(
    name="beijing_guide",
    metadata={"description": "北京导览打卡点数据"}
)

# 创建向量存储
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 创建存储上下文
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 创建或加载索引
try:
    # 尝试从现有数据加载索引
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context
    )
    logger.info("成功加载现有向量索引")
except Exception:
    # 如果没有数据，创建新索引
    index = VectorStoreIndex(
        [],
        storage_context=storage_context
    )
    logger.info("创建新的向量索引")


async def save_to_db(item: BaseContent) -> None:
    """
    将任意 BaseContent 子类对象保存到向量数据库。

    实现细节：
    - 使用 pydantic 的 model_dump() 将对象转为字典
    - 提取 `text_content` 作为要向量化的文本
    - 将其余字段作为 metadata 存入 ChromaDB

    Args:
        item: 继承自 BaseContent 的对象（如 XHSNote, StoryClip, ArchitectureDoc）
    """
    try:
        # 将 Pydantic 对象转为字典（可序列化）
        item_dict = item.model_dump()

        # 提取用于向量化的文本内容
        text_content = item_dict.pop("text_content", "") or ""

        # 提取 id（如果存在），否则使用对象 id
        doc_id = item_dict.get("id") or item.id
        # 不把 id 重复存入 metadata
        item_dict.pop("id", None)

        # 将剩余字段作为 metadata
        metadata = item_dict

        logger.info(f"开始存入向量数据库: {doc_id}")

        # 构造 LlamaIndex Document，并插入索引
        document = Document(
            text=text_content,
            metadata=metadata,
            id_=doc_id
        )

        index.insert(document)

        logger.info(f"成功存入向量数据库: {doc_id}")

    except Exception as e:
        logger.error(f"存入向量数据库失败 {getattr(item, 'id', str(item))}: {str(e)}")
        raise
