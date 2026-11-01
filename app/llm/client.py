"""
Robust Gemini LLM client wrapper with exponential backoff, model fallbacks,
and Pydantic structured output parsing.
"""

import json
import re
import time
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import LLMExecutionError

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    """Wrapper around Google GenAI client with enterprise-grade resilience."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY provided. LLM calls will fail if invoked.")
            self._client = None
        else:
            self._client = genai.Client(api_key=self.api_key)

        self.primary_model = settings.primary_model
        self.cheap_model = settings.cheap_model
        self.fallback_model = settings.fallback_model

    def _get_client(self) -> genai.Client:
        if not self._client:
            if not self.api_key:
                self.api_key = settings.gemini_api_key
            if not self.api_key:
                raise LLMExecutionError("GEMINI_API_KEY is missing from configuration.")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2
    ) -> str:
        """
        Generate text with automatic fallback to secondary model on failure.
        """
        client = self._get_client()
        target_model = model or self.primary_model

        try:
            return self._call_with_retry(
                client=client,
                model=target_model,
                contents=prompt,
                system_instruction=system_instruction,
                temperature=temperature
            )
        except Exception as primary_err:
            logger.warning(
                "Primary model %s failed: %s. Attempting fallback to %s",
                target_model, primary_err, self.fallback_model
            )
            try:
                return self._call_with_retry(
                    client=client,
                    model=self.fallback_model,
                    contents=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature
                )
            except Exception as fallback_err:
                logger.error("Both primary and fallback models failed: %s", fallback_err)
                raise LLMExecutionError(f"LLM generation failed: {fallback_err}") from fallback_err

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        model: Optional[str] = None,
        system_instruction: Optional[str] = None
    ) -> T:
        """
        Generate structured output adhering to a Pydantic schema using
        native JSON response schema with robust JSON parsing fallback.
        """
        client = self._get_client()
        target_model = model or self.primary_model

        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                system_instruction=system_instruction,
                temperature=0.1
            )
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config
            )
            text = (response.text or "").strip()
            return schema.model_validate_json(text)
        except Exception as err:
            logger.warning("Native structured output failed with %s. Falling back to JSON parsing: %s", target_model, err)
            # Fallback to standard text generation + JSON extractor
            augmented_prompt = (
                f"{prompt}\n\n"
                f"IMPORTANT: You must return ONLY a single valid JSON object strictly matching this schema:\n"
                f"{json.dumps(schema.model_json_schema())}"
            )
            raw_text = self.generate_text(augmented_prompt, model=target_model, system_instruction=system_instruction)
            return self._parse_json_to_schema(raw_text, schema)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _call_with_retry(
        self,
        client: genai.Client,
        model: str,
        contents: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2
    ) -> str:
        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction
        )
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
        if not response.text:
            raise ValueError("Gemini returned an empty response.")
        return response.text

    @staticmethod
    def _parse_json_to_schema(text: str, schema: Type[T]) -> T:
        """Extract and parse JSON from Markdown code fences or free text."""
        cleaned = text.strip()
        # Strip markdown ```json ... ``` blocks
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            data = json.loads(cleaned)
            return schema.model_validate(data)
        except Exception:
            pass

        # Search for first { ... } or [ ... ]
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return schema.model_validate(data)
            except Exception as parse_err:
                raise LLMExecutionError(f"Failed to parse structured response: {parse_err}")

        raise LLMExecutionError(f"Could not extract valid JSON from response: {text[:200]}")


# Global default client instance
gemini_client = GeminiClient()

