import os

from langchain_community.vectorstores import FAISS
from langchain_core.retrievers import BaseRetriever

from backend.app.core.config import settings
from backend.app.rag.embeddings import get_embedding_model


def get_retriever(k: int = 3) -> BaseRetriever:
    """
    Load FAISS vector store and return a retriever.
    """
    embeddings = get_embedding_model()

    if not os.path.exists(settings.FAISS_INDEX_PATH):
        raise FileNotFoundError(
            "FAISS index not found. Please upload documents first."
        )

    vectorstore = FAISS.load_local(
        settings.FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    return retriever
