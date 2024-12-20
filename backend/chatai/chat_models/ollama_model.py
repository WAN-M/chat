from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama.llms import OllamaLLM
from .base_model import BaseModel

RAG_TEMPLATE = """
You are an assistant for question-answering tasks. Below is the context retrieved from documents. 
If the question is related to the context, use the information to generate an answer. 
If the question is unrelated to the context, answer based on your own knowledge. 
If you do not know the answer, just say that you do not know. Be concise.

Context:
<context>
{context}
</context>

Question:
{question}

Answer:
"""

rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

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
            yield token

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    def chat_stream_rag(self, message, docs):
        chain = (
            RunnablePassthrough.assign(context=lambda input: self._format_docs(input["context"]))
            | rag_prompt
            | self._llm
            | StrOutputParser()
        )
        res = chain.stream({"context": docs, "question": message})
        for token in res:
            yield token
