import chromadb.api
import os
from typing import List
from django.conf import settings
from langchain_chroma import Chroma
from langchain_elasticsearch import ElasticsearchStore
from langchain_ollama import OllamaEmbeddings

class VectoreDatabase():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    @staticmethod
    def get_db_dir(user):
        path = settings.USER_KNOWLEDGE_DIR / f'{user.email}'
        return path

    @staticmethod
    def store(docs: List, persist_path: str):
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        vectordb = Chroma.from_documents(documents=docs, 
                                         embedding=VectoreDatabase.embeddings, 
                                         persist_directory=persist_path)
        vectordb = None # 释放内存
    
class ElasticSearchVDB(VectoreDatabase):
    @staticmethod
    def store(docs: List, persist_path: str):
        user = persist_path.split('/')[-3]
        vectordb = ElasticsearchStore.from_documents(
            docs,
            index_name=user,
            embedding=VectoreDatabase.embeddings,
            es_url="https://localhost:9200/",
            es_user='elastic',
            es_password='e4nkJk6FHIFUKfIukRhn',
            es_params={'ca_certs': False, 'verify_certs': False}
        )
        vectordb = None