import os
os.environ["OPENAI_API_KEY"] = ""   # TODO get activate api key

from langchain_openai.chat_models import ChatOpenAI
from .base_model import BaseModel

class OpenAIModel(BaseModel):

    def chat_response(self, message: str) -> str:
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        res = llm.invoke(message)
        
        return res