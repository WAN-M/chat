from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama.llms import OllamaLLM
from .base_model import BaseModel

RAG_TEMPLATE = """
You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise. \

<context>
{context}
</context>

Answer the following question:

{question}"""

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
