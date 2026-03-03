from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from backend.app.core.config import settings
from backend.app.rag.retriever import get_retriever


def get_rag_chain():
    """
    Create and return a RAG chain using Groq LLM.
    """

    # 1️⃣ Load Retriever
    retriever = get_retriever(k=3)

    # 2️⃣ Load Groq LLM
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.2,
    )

    # 3️⃣ Prompt Template
    prompt = ChatPromptTemplate.from_template(
        """
        You are a helpful AI assistant.
        Answer the question ONLY using the provided context.
        If the answer is not in the context, say "I don't know".

        Context:
        {context}

        Question:
        {question}
        """
    )

    # 4️⃣ Chain logic
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {
            "context": retriever | format_docs,
            "question": lambda x: x,
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
