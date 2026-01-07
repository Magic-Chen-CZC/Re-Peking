#!/usr/bin/env python3
"""
数据检索脚本

功能：负责"从向量数据库检索数据"

使用示例：
    # 命令行模式：直接检索
    python search.py 北京有哪些适合夏天去的景点
    
    # 交互式模式：持续对话
    python search.py

输出：
    - 返回语义检索结果
    - 显示相关来源文档和元数据
"""
import chromadb
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import settings
from modules.qwen_embedding import QwenEmbedding
from modules.qwen_llm import QwenLLM
from utils.logger import logger


def initialize_index():
    """
    初始化向量索引，使用与存储时相同的配置
    
    Returns:
        VectorStoreIndex: 向量索引对象
    """
    logger.info("正在初始化检索系统...")
    
    # 初始化全局 Qwen Embedding 模型（与 vector_store.py 中完全一致）
    Settings.embed_model = QwenEmbedding(
        api_key=settings.DASHSCOPE_API_KEY,
        model_name=settings.EMBEDDING_MODEL
    )
    logger.info(f"已加载嵌入模型: {settings.EMBEDDING_MODEL}")
    
    # 初始化全局 Qwen LLM 模型
    Settings.llm = QwenLLM(
        api_key=settings.DASHSCOPE_API_KEY,
        model_name=settings.QWEN_MODEL,
        base_url=settings.QWEN_BASE_URL,
        temperature=0.7
    )
    logger.info(f"已加载 LLM 模型: {settings.QWEN_MODEL}")
    
    # 初始化 ChromaDB 持久化客户端
    chroma_client = chromadb.PersistentClient(path=settings.DB_PATH)
    
    # 获取集合
    chroma_collection = chroma_client.get_or_create_collection(
        name="beijing_guide",
        metadata={"description": "北京导览打卡点数据"}
    )
    
    # 创建向量存储
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # 创建存储上下文
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # 从向量存储加载索引
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context
    )
    
    logger.info(f"成功加载向量索引，数据库路径: {settings.DB_PATH}")
    return index


def search(query: str, top_k: int = 3):
    """
    执行语义检索
    
    Args:
        query: 查询文本
        top_k: 返回结果数量
    """
    try:
        # 初始化索引
        index = initialize_index()
        
        # 构建查询引擎
        query_engine = index.as_query_engine(
            similarity_top_k=top_k,
            response_mode="compact"
        )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"查询: {query}")
        logger.info(f"{'='*60}\n")
        
        # 执行查询
        response = query_engine.query(query)
        
        # 打印答案
        print("\n" + "="*60)
        print("📝 检索结果:")
        print("="*60)
        print(f"\n{response.response}\n")
        
        # 打印来源文档
        if response.source_nodes:
            print("="*60)
            print("📚 来源文档:")
            print("="*60)
            
            for i, node in enumerate(response.source_nodes, 1):
                print(f"\n【来源 {i}】")
                print(f"相似度: {node.score:.4f}" if node.score else "相似度: N/A")
                
                # 打印元数据
                metadata = node.metadata
                if metadata:
                    print(f"地点: {metadata.get('location', 'N/A')}")
                    print(f"分类: {metadata.get('category', 'N/A')}")
                    print(f"推荐指数: {metadata.get('rating', 'N/A')}/5")
                    print(f"有效: {'是' if metadata.get('valid') else '否'}")
                    print(f"URL: {metadata.get('url', 'N/A')}")
                
                # 打印摘要内容
                print(f"\n摘要:\n{node.text[:200]}..." if len(node.text) > 200 else f"\n摘要:\n{node.text}")
                print("-" * 60)
        else:
            print("\n⚠️ 未找到相关文档")
        
        print("\n")
        
    except Exception as e:
        logger.error(f"检索失败: {str(e)}")
        raise


def interactive_search():
    """交互式检索模式"""
    print("\n" + "="*60)
    print("🔍 北京导览 AI - 交互式检索系统")
    print("="*60)
    print("\n输入查询内容，输入 'quit' 或 'exit' 退出\n")
    
    # 预加载索引
    try:
        index = initialize_index()
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )
        print("✅ 检索系统已就绪！\n")
    except Exception as e:
        logger.error(f"初始化失败: {str(e)}")
        return
    
    while True:
        try:
            query = input("🔎 请输入查询: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见！")
                break
            
            print(f"\n正在检索: {query}...")
            
            # 执行查询
            response = query_engine.query(query)
            
            # 打印结果
            print("\n" + "="*60)
            print("📝 检索结果:")
            print("="*60)
            print(f"\n{response.response}\n")
            
            # 打印来源
            if response.source_nodes:
                print("="*60)
                print("📚 来源文档:")
                print("="*60)
                
                for i, node in enumerate(response.source_nodes, 1):
                    metadata = node.metadata
                    print(f"\n【{i}】 {metadata.get('location', 'N/A')} | "
                          f"评分: {metadata.get('rating', 'N/A')}/5 | "
                          f"分类: {metadata.get('category', 'N/A')}")
                    print(f"    {node.text[:100]}...")
            
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            logger.error(f"查询出错: {str(e)}")
            continue


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 命令行模式：直接检索
        query_text = " ".join(sys.argv[1:])
        search(query_text)
    else:
        # 交互式模式
        interactive_search()
