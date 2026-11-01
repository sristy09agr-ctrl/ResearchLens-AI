"""
Configuration module for ResearchLens AI.
Loads settings from environment variables or .env file with intelligent defaults and fallbacks.
"""

from pathlib import Path
import os
from typing import Optional
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Prevent huggingface hub from trying online requests when cached models exist
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    USE_PYDANTIC_SETTINGS = True
except ImportError:
    from pydantic import BaseModel
    USE_PYDANTIC_SETTINGS = False


if USE_PYDANTIC_SETTINGS:
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=str(BASE_DIR / ".env"),
            env_file_encoding="utf-8",
            extra="ignore"
        )

        # Gemini LLM Settings
        gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        primary_model: str = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-2.0-flash")
        cheap_model: str = os.getenv("GEMINI_CHEAP_MODEL", "gemini-2.0-flash-lite")
        fallback_model: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash")
        llm_timeout_seconds: float = 45.0
        llm_max_retries: int = 3

        # Hugging Face Settings
        hf_token: Optional[str] = os.getenv("HF_TOKEN", None)

        # Local Embedding & Reranking Models
        embedding_model_name: str = "all-MiniLM-L6-v2"
        reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

        # Storage & Limits
        max_file_size_bytes: int = 20 * 1024 * 1024  # 20 MB
        max_pdf_pages: int = 100
        data_dir: Path = BASE_DIR / "data"
        upload_dir: Path = BASE_DIR / "data" / "uploads"
        database_path: Path = BASE_DIR / "data" / "researchlens.db"

        # Qdrant Vector Store
        qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
        qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "researchlens_chunks")
        use_persistent_qdrant: bool = True

        # Retrieval & Agent Thresholds
        default_alpha: float = 0.5  # Hybrid fusion weight
        default_top_k: int = 5
        default_candidate_k: int = 30
        sufficiency_threshold: float = 0.35
        abstention_threshold: float = 0.45
        confidence_high_threshold: float = 0.75
        confidence_med_threshold: float = 0.50
        max_agent_iterations: int = 2
        per_paper_diversity_cap: float = 0.40  # Max 40% passages from a single paper when multi-paper

        # Application
        app_name: str = "ResearchLens AI"
        app_version: str = "2.0.0"
        debug: bool = False
else:
    class Settings(BaseModel):
        gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        primary_model: str = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-2.0-flash")
        cheap_model: str = os.getenv("GEMINI_CHEAP_MODEL", "gemini-2.0-flash-lite")
        fallback_model: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash")
        llm_timeout_seconds: float = 45.0
        llm_max_retries: int = 3

        hf_token: Optional[str] = os.getenv("HF_TOKEN", None)

        embedding_model_name: str = "all-MiniLM-L6-v2"
        reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

        max_file_size_bytes: int = 20 * 1024 * 1024
        max_pdf_pages: int = 100
        data_dir: Path = BASE_DIR / "data"
        upload_dir: Path = BASE_DIR / "data" / "uploads"
        database_path: Path = BASE_DIR / "data" / "researchlens.db"

        qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
        qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "researchlens_chunks")
        use_persistent_qdrant: bool = True

        default_alpha: float = 0.5
        default_top_k: int = 5
        default_candidate_k: int = 30
        sufficiency_threshold: float = 0.35
        abstention_threshold: float = 0.45
        confidence_high_threshold: float = 0.75
        confidence_med_threshold: float = 0.50
        max_agent_iterations: int = 2
        per_paper_diversity_cap: float = 0.40

        app_name: str = "ResearchLens AI"
        app_version: str = "2.0.0"
        debug: bool = False


# Instantiate singleton settings and ensure required directories exist
settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.data_dir.mkdir(parents=True, exist_ok=True)
