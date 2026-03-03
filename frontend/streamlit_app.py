import streamlit as st
import requests
import uuid
import os

# =====================================================
# CONFIG
# =====================================================

BACKEND_URL = "http://127.0.0.1:8000"
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(
    page_title="RAG Agent",
    page_icon="🤖",
    layout="wide",
)

# =====================================================
# SESSION / THREAD MANAGEMENT
# =====================================================

# Persist session_id (thread) using query params
query_params = st.query_params

if "session_id" in query_params:
    st.session_state.session_id = query_params["session_id"]
else:
    new_session_id = str(uuid.uuid4())
    st.session_state.session_id = new_session_id
    st.query_params["session_id"] = new_session_id

# UI chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Track current thread to detect switching
if "active_thread" not in st.session_state:
    st.session_state.active_thread = st.session_state.session_id

# Track PDF processing
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# =====================================================
# LOAD THREAD LIST FROM BACKEND
# =====================================================

if "threads" not in st.session_state:
    try:
        resp = requests.get(f"{BACKEND_URL}/chat/threads", timeout=10)
        st.session_state.threads = resp.json() if resp.status_code == 200 else []
    except Exception:
        st.session_state.threads = []

# Ensure current thread is in list
if st.session_state.session_id not in st.session_state.threads:
    st.session_state.threads.insert(0, st.session_state.session_id)

# =====================================================
# LOAD CHAT HISTORY WHEN THREAD CHANGES
# =====================================================

if st.session_state.active_thread != st.session_state.session_id:
    try:
        resp = requests.get(
            f"{BACKEND_URL}/chat/history/{st.session_state.session_id}",
            timeout=10,
        )
        st.session_state.messages = resp.json() if resp.status_code == 200 else []
    except Exception:
        st.session_state.messages = []

    st.session_state.active_thread = st.session_state.session_id

# =====================================================
# UI
# =====================================================

st.title("📄 RAG Chatbot (Groq + LangGraph)")
st.caption("Upload PDFs and chat with your documents")

# =====================================================
# SIDEBAR — THREAD CONTROLS
# =====================================================

st.sidebar.header("🧵 Conversations")

# Create a new thread explicitly
if st.sidebar.button("➕ New Thread"):
    new_thread = str(uuid.uuid4())
    st.session_state.session_id = new_thread
    st.query_params["session_id"] = new_thread
    st.session_state.messages = []
    st.session_state.pdf_processed = True
    st.session_state.threads.insert(0, new_thread)

# Switch between threads
selected_thread = st.sidebar.selectbox(
    "Select thread",
    st.session_state.threads,
    index=st.session_state.threads.index(st.session_state.session_id),
)

if selected_thread != st.session_state.session_id:
    st.session_state.session_id = selected_thread
    st.query_params["session_id"] = selected_thread

# =====================================================
# SIDEBAR — PDF UPLOAD
# =====================================================

st.sidebar.header("📂 Upload Document")

uploaded_file = st.sidebar.file_uploader(
    "Upload a PDF file",
    type=["pdf"]
)

# Detect new PDF upload (document replacement)
if uploaded_file is not None:
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.last_uploaded_file = uploaded_file.name
        st.session_state.pdf_processed = False
        st.session_state.messages = []

# Process PDF (replace FAISS index)
if uploaded_file and not st.session_state.pdf_processed:
    if st.sidebar.button("📥 Process PDF"):
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.sidebar:
            with st.spinner("Processing document..."):
                response = requests.post(
                    f"{BACKEND_URL}/upload",
                    json={"file_path": file_path},
                    timeout=300,
                )

                if response.status_code == 200:
                    st.session_state.pdf_processed = True
                    st.sidebar.success("✅ Document indexed successfully!")
                else:
                    st.sidebar.error(response.text)

# =====================================================
# SIDEBAR — CHAT & THREAD CONTROLS
# =====================================================

st.sidebar.divider()
st.sidebar.header("🧹 Chat Controls")

# Clear chat messages ONLY (thread remains)
if st.sidebar.button("🗑️ Clear This Chat"):
    try:
        response = requests.delete(
            f"{BACKEND_URL}/chat/history/{st.session_state.session_id}",
            timeout=30,
        )

        if response.status_code == 200:
            st.session_state.messages = []
            st.sidebar.success("Chat cleared successfully!")
        else:
            st.sidebar.error(response.text)

    except Exception as e:
        st.sidebar.error(str(e))


st.sidebar.divider()
st.sidebar.header("❌ Thread Controls")

# ❌ DELETE ENTIRE THREAD
if st.sidebar.button("❌ Delete This Thread"):
    try:
        response = requests.delete(
            f"{BACKEND_URL}/chat/thread/{st.session_state.session_id}",
            timeout=30,
        )

        if response.status_code == 200:
            # Remove from local thread list
            if st.session_state.session_id in st.session_state.threads:
                st.session_state.threads.remove(st.session_state.session_id)

            # Create and switch to a new thread
            new_thread = str(uuid.uuid4())
            st.session_state.session_id = new_thread
            st.query_params["session_id"] = new_thread
            st.session_state.messages = []
            st.session_state.pdf_processed = True
            st.session_state.threads.insert(0, new_thread)

            st.sidebar.success("Thread deleted successfully!")

            # 🔁 FORCE UI TO REBUILD DROPDOWN
            st.rerun()

        else:
            st.sidebar.error(response.text)

    except Exception as e:
        st.sidebar.error(str(e))

# =====================================================
# CHAT UI
# =====================================================

st.subheader("💬 Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask a question about your documents...")

if user_input:
    # User message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "session_id": st.session_state.session_id,
                        "question": user_input,
                    },
                    timeout=120,
                )

                if response.status_code == 200:
                    answer = response.json()["answer"]
                else:
                    answer = f"❌ Error: {response.text}"

                st.markdown(answer)

            except Exception as e:
                answer = str(e)
                st.error(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
