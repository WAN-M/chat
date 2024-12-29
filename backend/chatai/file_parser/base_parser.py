from abc import ABC, abstractmethod
from langchain.text_splitter import RecursiveCharacterTextSplitter

class BaseParser(ABC):
    def __init__(self, chunk_size=400, chunk_overlap=50):
        super().__init__()
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split_docs(self, docs):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self._chunk_size, chunk_overlap=self._chunk_overlap)
        return text_splitter.split_documents(docs)
    
    @abstractmethod
    def parse(self, file_path: str):
        pass