from langchain_ollama.llms import OllamaLLM
from .base_model import BaseModel

class OllamaModel(BaseModel):
    def __init__(self) -> None:
        super().__init__()
        self._llm = OllamaLLM(model='llama3.3')

    def chat_response(self, message: str) -> str:
        res = self._llm.invoke(message)
        return res
    
    def chat_stream(self, message: str):
        res = self._llm.stream(message)
        for token in res:
            print(token)
            yield token