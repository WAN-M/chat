from langchain_community.document_loaders import PyPDFLoader
from .base_parser import BaseParser

class PDFParser(BaseParser):

    def parse(self, file_path):
        loader=PyPDFLoader(file_path)
        docs = loader.load()
        split_docs = self.split_docs(docs)
        return split_docs
        