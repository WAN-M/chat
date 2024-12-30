import chromadb.api
import logging
import os
import shutil
from typing import List
from django.conf import settings
from langchain_chroma import Chroma
from langchain_elasticsearch import ElasticsearchStore
from langchain_ollama import OllamaEmbeddings

LOGGER = logging.getLogger(__name__)

class VectoreDatabase():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    @staticmethod
    def get_db_dir(user):
        path = settings.USER_KNOWLEDGE_DIR / f'{user.email}'
        return path

    @staticmethod
    def store(docs: List, user, knowledge_name: str):
        persist_path = VectoreDatabase.get_db_dir(user) / 'vector' / knowledge_name
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        vectordb = Chroma.from_documents(documents=docs, 
                                         embedding=VectoreDatabase.embeddings, 
                                         persist_directory=persist_path)
        vectordb = None # 释放内存

    @staticmethod
    def delete(user, knowledge_name: str):
        db_dir = VectoreDatabase.get_db_dir(user) / 'vector' / knowledge_name
        if os.path.exists(db_dir):
            shutil.rmtree(db_dir)
        else:
            raise FileNotFoundError(f"Directory {db_dir} not found")
    
class ElasticSearchVDB(VectoreDatabase):
    @staticmethod
    def store(docs: List, user, knowledge_name: str):
        vectordb = ElasticsearchStore.from_documents(
            docs,
            index_name=user.email,
            embedding=VectoreDatabase.embeddings,
            es_url="https://localhost:9200/",
            es_user='elastic',
            es_password='e4nkJk6FHIFUKfIukRhn',
            es_params={'ca_certs': False, 'verify_certs': False}
        )
        vectordb = None

    @staticmethod
    def delete(user, knowledge_name: str):
        vectordb = ElasticsearchStore(
            index_name=user.email,
            es_url="https://localhost:9200/",
            es_user='elastic',
            es_password='e4nkJk6FHIFUKfIukRhn',
            es_params={'ca_certs': False, 'verify_certs': False}
        )
        file_path = VectoreDatabase.get_db_dir(user) / 'file' / knowledge_name
        LOGGER.info(f"Delete knowledge base {file_path}")
        query = {
            "query": {
                "match": {
                    "metadata.source": str(file_path)
                }
            }
        }
        vectordb.delete(query)
        vectordb = None
