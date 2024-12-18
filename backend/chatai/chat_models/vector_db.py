import os
from typing import List
from django.conf import settings
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

class VectoreDatabase():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    @staticmethod
    def get_db_dir(user):
        path = settings.USER_KNOWLEDGE_DIR / f'{user.email}'
        return path

    @staticmethod
    def store(docs: List, persist_path: str):
        vectordb = Chroma.from_documents(documents=docs, 
                                         embedding=VectoreDatabase.embeddings, 
                                         persist_directory=persist_path)
        vectordb = None # 释放内存
    