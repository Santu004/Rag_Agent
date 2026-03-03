from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    # ===== LLM / GROQ =====
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

    # ===== Database =====
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # ===== Vector Store =====
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "faiss_index")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton settings object
settings = Settings()
