from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def chat_response(self, message: str) -> str:
        ...

    @abstractmethod
    def chat_stream(self, message: str):
        ...