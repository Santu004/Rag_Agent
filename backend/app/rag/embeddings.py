from langchain_community.embeddings import HuggingFaceEmbeddings


def get_embedding_model():
    """
    Load and return embedding model for vector store.
    Using HuggingFace because Groq does not provide embeddings.
    """

    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name
    )

    return embeddings
