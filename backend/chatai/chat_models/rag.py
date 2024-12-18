import logging
import os

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

LOGGER = logging.getLogger(__name__)

class RAG():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    @staticmethod
    def search_documents(query: str, db_dir: str, top_k: int = 5):
        all_documents = []
        LOGGER.error(db_dir)
        # 遍历目录中的所有用户文档
        for file_name in os.listdir(db_dir):
            folder_path = os.path.join(db_dir, file_name)
            LOGGER.error(folder_path)
            if os.path.isdir(folder_path):
                vector_store = Chroma(persist_directory=folder_path, embedding_function=RAG.embeddings)
                search_results = vector_store.similarity_search(query, k=top_k)
                all_documents.extend(search_results)

        return all_documents
    