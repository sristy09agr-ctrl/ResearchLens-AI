"""
FastAPI dependency injection utilities.
"""

from app.config import settings, Settings
from app.llm.client import gemini_client, GeminiClient


def get_settings() -> Settings:
    return settings


def get_gemini_client() -> GeminiClient:
    return gemini_client

