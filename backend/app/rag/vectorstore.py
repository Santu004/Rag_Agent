import os
import shutil
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from backend.app.core.config import settings
from backend.app.rag.embeddings import get_embedding_model


def load_documents(file_path: str) -> List[Document]:
    """
    Load documents from a PDF file.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into smaller chunks for better retrieval.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_documents(documents)


def create_or_update_faiss_index(documents: List[Document]):
    """
    Create or update FAISS vector store.

    NOTE:
    This function is called ONLY during document upload,
    NOT during chat queries.
    """
    embeddings = get_embedding_model()

    if os.path.exists(settings.FAISS_INDEX_PATH):
        # Load existing FAISS index
        vectorstore = FAISS.load_local(
            settings.FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        vectorstore.add_documents(documents)
    else:
        # Create new FAISS index
        vectorstore = FAISS.from_documents(documents, embeddings)

    # Save FAISS index locally
    vectorstore.save_local(settings.FAISS_INDEX_PATH)


# def process_pdf_and_store(file_path: str):
#     """
#     Complete pipeline:
#     PDF → chunks → embeddings → FAISS

#     IMPORTANT:
#     - This function should run ONLY when a new PDF is uploaded
#     - It should NOT run on every chat query
#     """

#     # 🔒 SAFETY CHECK:
#     # If FAISS index already exists, we assume documents are already indexed.
#     # This prevents re-processing the same PDF again and again.
#     if os.path.exists(settings.FAISS_INDEX_PATH):
#         print("FAISS index already exists. Skipping PDF processing.")
#         return

#     # 1️⃣ Load PDF
#     documents = load_documents(file_path)

#     # 2️⃣ Split into chunks
#     split_docs = split_documents(documents)

#     # 3️⃣ Create FAISS index (only once)
#     create_or_update_faiss_index(split_docs)



def process_pdf_and_store(file_path: str):
    """
    Complete pipeline:
    PDF → chunks → embeddings → FAISS

    BEHAVIOR:
    - If a FAISS index already exists, it is DELETED
    - New PDF replaces old knowledge base
    - Chat queries will now use ONLY the latest uploaded PDF
    """

    # 🔄 STEP 0: Remove old FAISS index (if any)
    if os.path.exists(settings.FAISS_INDEX_PATH):
        shutil.rmtree(settings.FAISS_INDEX_PATH)
        print("Old FAISS index removed.")

    # 1️⃣ Load PDF
    documents = load_documents(file_path)

    # 2️⃣ Split into chunks
    split_docs = split_documents(documents)

    # 3️⃣ Create fresh FAISS index
    create_or_update_faiss_index(split_docs)

    print("New FAISS index created successfully.")