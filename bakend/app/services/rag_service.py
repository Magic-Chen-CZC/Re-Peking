import os
from typing import List, Dict
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.core.postprocessor import SimilarityPostprocessor

# Configure LlamaIndex to use DashScope embeddings
# Note: We assume DASHSCOPE_API_KEY is in env
embedding_model = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-v1")
Settings.embed_model = DashScopeEmbedding(model_name=embedding_model)

class RAGService:
    def __init__(self, data: List[Dict[str, str]]):
        # Initialize persistence
        self.persist_dir = "./storage"
        
        # Try to load from storage
        if os.path.exists(self.persist_dir):
            try:
                from llama_index.core import StorageContext, load_index_from_storage
                storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
                self.index = load_index_from_storage(storage_context)
                print("Loaded RAG index from storage.")
            except Exception as e:
                print(f"Failed to load index from storage: {e}. Rebuilding from memory.")
                self._build_index(data)
        else:
            self._build_index(data)
            
    def _build_index(self, data: List[Dict[str, str]]):
        documents = []
        for item in data:
            doc = Document(
                text=item['text'],
                metadata={
                    "id": item['id'],
                    "tags": item.get('tags', [])
                }
            )
            documents.append(doc)
        
        if documents:
            self.index = VectorStoreIndex.from_documents(documents)
        else:
            self.index = VectorStoreIndex.from_documents([]) # Empty index

    def build_from_data(self, data: List[Dict[str, str]]):
        """
        Rebuild index from new data and persist it.
        """
        self._build_index(data)
        # Persist
        if not os.path.exists(self.persist_dir):
            os.makedirs(self.persist_dir)
        self.index.storage_context.persist(persist_dir=self.persist_dir)
        print(f"Persisted RAG index to {self.persist_dir}")

    def retrieve_context(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve context for a given query.
        Returns a concatenated string of retrieved texts.
        """
        if not self.index:
            return ""
            
        # Configure retriever
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        
        # Retrieve nodes
        nodes = retriever.retrieve(query)
        
        # Concatenate text
        context_str = "\n\n".join([node.get_content() for node in nodes])
        return context_str

# --- Mock Data & Global Instance ---

MOCK_RAG_DATA = [
    # ... (Keep existing mock data as fallback or initial seed)
]

# Initialize global service
# We pass empty list initially if we want to rely on storage, 
# but for safety we pass MOCK_RAG_DATA so it has something if storage is missing.
# However, seed_data.py will overwrite this.
rag_service = RAGService([]) 

