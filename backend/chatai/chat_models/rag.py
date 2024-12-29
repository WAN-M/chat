import logging
import os

from langchain_chroma import Chroma
from langchain_elasticsearch import ElasticsearchStore
from langchain_ollama import OllamaEmbeddings

LOGGER = logging.getLogger(__name__)

class RAG():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    similarity_threshold = 0.75

    @staticmethod
    def search_documents(query: str, db_dir: str, top_k: int = 5):
        # 用户还没上传任何知识库
        if not os.path.exists(db_dir):
            return []
        all_documents = []
        # 遍历目录中的所有用户文档
        for file_name in os.listdir(db_dir):
            folder_path = os.path.join(db_dir, file_name)
            if os.path.isdir(folder_path):
                vector_store = Chroma(persist_directory=folder_path, embedding_function=RAG.embeddings)
                search_results = vector_store.similarity_search(query, k=top_k)
                all_documents.extend(search_results)

        return all_documents
    
class ElasticSearchRAG(RAG):
    @staticmethod
    def search_documents(query: str, db_dir: str, top_k: int = 5):
        user = db_dir.split('/')[-2]
        es = ElasticsearchStore(
            index_name=user,
            embedding=RAG.embeddings,
            es_url="https://localhost:9200/",
            es_user='elastic',
            es_password='e4nkJk6FHIFUKfIukRhn',
            es_params={'ca_certs': False, 'verify_certs': False}
        )
        all_documents = es.search(query, search_type="similarity")
        LOGGER.error('test')
        LOGGER.error(all_documents)
        return all_documents