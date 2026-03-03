from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.app.core.database import Base, engine
from backend.app.api.chat import router as chat_router
from backend.app.api.upload import router as upload_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler.
    Runs once on startup and shutdown.
    """
    # ✅ Startup logic
    Base.metadata.create_all(bind=engine)

    yield

    # ✅ Shutdown logic (if needed later)
    # e.g., close connections


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG Agent API",
        version="1.0.0",
        description="RAG Agent using LangChain, LangGraph, FAISS, Groq, and PostgreSQL",
        lifespan=lifespan,  # 👈 modern replacement
    )

    app.include_router(upload_router)
    app.include_router(chat_router)
    return app


app = create_app()


@app.get("/")
def health_check():
    return {"status": "ok"}
