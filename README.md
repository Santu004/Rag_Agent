# 🚀 RAG Agent (FastAPI + LangGraph + Streamlit)

A full-stack Retrieval-Augmented Generation (RAG) application built using:

- FastAPI (Backend API)
- LangChain + LangGraph (RAG Pipeline)
- FAISS (Vector Store)
- Sentence Transformers (Embeddings)
- Streamlit (Frontend UI)
- SQLAlchemy (Chat History Storage)

---

## 📌 Features

✅ Upload PDF documents  
✅ Automatically chunk & embed documents  
✅ Store embeddings in FAISS  
✅ Retrieval-based question answering  
✅ Chat history stored in database  
✅ FastAPI backend  
✅ Streamlit interactive frontend  

---

## 🏗️ Project Structure

```

RagAgent1/
│
├── backend/
│   └── app/
│       ├── api/              # FastAPI routes
│       ├── core/             # Config & database setup
│       ├── graph/            # LangGraph workflow
│       ├── models/           # SQLAlchemy models
│       ├── rag/              # RAG components
│       ├── services/         # Business logic
│       └── main.py           # FastAPI entry point
│
├── frontend/
│   └── streamlit_app.py      # Streamlit UI
│
├── faiss_index/              # Vector index storage
├── data/uploads/             # Uploaded PDFs
├── requirements.txt
└── .gitignore

```

---

## ⚙️ Installation

### 1️⃣ Clone the repo

```

git clone [https://github.com/Santu004/Rag_Agent.git](https://github.com/Santu004/Rag_Agent.git)
cd Rag_Agent

```

### 2️⃣ Create virtual environment

```

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

```

### 3️⃣ Install dependencies

```

pip install -r requirements.txt

```

---

## 🔐 Environment Variables

Create a `.env` file:

```

GROQ_API_KEY=your_groq_api_key
DATABASE_URL=sqlite:///./rag.db
FAISS_INDEX_PATH=faiss_index

```

---

## ▶️ Run Backend (FastAPI)

```

cd backend
uvicorn app.main:app --reload

```

API runs at:
```

[http://127.0.0.1:8000](http://127.0.0.1:8000)

```

---

## ▶️ Run Frontend (Streamlit)

```

cd frontend
streamlit run streamlit_app.py

```

---

## 🧠 How It Works

1. Upload PDF  
2. Text is chunked  
3. Embeddings generated  
4. Stored in FAISS  
5. Query retrieves relevant chunks  
6. LLM generates contextual answer  

---

## 🛠️ Tech Stack

- FastAPI
- LangChain
- LangGraph
- FAISS
- Sentence Transformers
- Streamlit
- SQLAlchemy

---