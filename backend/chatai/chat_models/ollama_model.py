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

RAG_MULITARY_TEMPLATE = """
You are an AI assistant focused on answering questions related to military topics. You have access to a document collection that may help in answering the question. Follow the steps below to generate your response:

1. **Language Consistency**: The question may be in either Chinese or English. Ensure your response is in the same language as the question. For Chinese questions, reply in Chinese. For English questions, reply in English.

2. **Answer Directly**: Your response must be **only the answer**, without any additional sentences, explanations, or phrases. No introduction, summary, or further context is needed. Just provide the shortest, most accurate answer to the question.

3. **Determine Relevance**: First, check if the question relates directly to the provided documents. If it does, extract only the most relevant information and give the precise answer. If the question is unrelated to the documents, use only your own knowledge and provide a concise answer.

4. **Avoid Hallucination**: If neither the documents nor your knowledge can provide an accurate answer, simply respond with "Unknown" in English or "未知" in Chinese. Do not attempt to guess or invent information.

5. **Response Format**: The answer must be delivered in a single, direct statement with no additional elaboration.

**Examples:**

Question (in English): "What are the latest advancements in military drone technology?"

- If documents are relevant: "AI-driven target identification, enhanced stealth."
  
- If no relevant documents: "AI-driven target identification, enhanced stealth."

问题（中文）: “军用无人机技术的最新进展是什么？”

- 如果文档相关: “AI驱动的目标识别，增强隐身能力。”
  
- 如果没有相关文档: “AI驱动的目标识别，增强隐身能力。”

**Below is the context retrieved from documents. Answer the following question using the above steps:**

Context:
<context>
{context}
</context>

Question:
{question}

Answer:
"""

rag_prompt = ChatPromptTemplate.from_template(RAG_MULITARY_TEMPLATE)

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
        return "\n\n".join(doc[0].page_content for doc in docs)
    
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
