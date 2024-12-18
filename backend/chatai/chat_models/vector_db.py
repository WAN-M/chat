from typing import List

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

class VectoreDatabase():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    @staticmethod
    def store(docs: List, persist_path: str):
        vectordb = Chroma.from_documents(documents=docs, 
                                         embedding=VectoreDatabase.embeddings, 
                                         persist_directory=persist_path)
        # vectordb.persist()
        vectordb = None # 释放内存
    