from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

class VectoreDatabase():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    def load_doc(self, doc):
        all_splits = self.text_splitter.split_documents(doc)
        vectordb = Chroma.from_documents(documents=all_splits, embedding=self.embeddings)

    