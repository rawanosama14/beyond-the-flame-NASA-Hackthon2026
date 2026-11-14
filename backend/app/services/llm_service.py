
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMUnavailable(RuntimeError):
    pass


class LLMService:
    """Provider-agnostic LLM adapter with bounded concurrency and safe fallback."""

    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.configured = settings.llm_enabled and (
            self.provider == "ollama" or bool(settings.llm_api_key)
        )
        self._semaphore = asyncio.Semaphore(
            max(1, settings.llm_max_concurrency)
        )

    def health(self) -> Dict[str, Any]:
        if not settings.llm_enabled:
            mode = "extractive_fallback"
        elif not self.configured:
            mode = "extractive_fallback_missing_key"
        else:
            mode = "llm_configured_with_extract_fallback"

        return {
            "provider": self.provider,
            "model": self.model if self.configured else None,
            "configured": bool(self.configured),
            "mode": mode,
        }

    async def generate(self, prompt: str) -> Optional[str]:
        if not self.configured:
            return None

        async with self._semaphore:
            return await self._generate_inner(prompt)

    async def _generate_inner(self, prompt: str) -> Optional[str]:
        headers = {"Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(
                timeout=settings.llm_timeout_seconds
            ) as client:

                # ==========================================
                # GEMINI
                # ==========================================
                if self.provider == "gemini":
                    model = self.model or "gemini-2.5-flash"

                    url = settings.llm_base_url or (
                        "https://generativelanguage.googleapis.com/"
                        f"v1beta/models/{model}:generateContent"
                    )

                    headers["x-goog-api-key"] = settings.llm_api_key

                    payload = {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": prompt}],
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.1,
                            "responseMimeType": "text/plain",
                        },
                    }

                    response = await client.post(
                        url,
                        headers=headers,
                        json=payload,
                    )

                    # Log Google's detailed error response for debugging.
                    # Never log API keys or request headers.
                    if response.is_error:
                        logger.error(
                            "Gemini API error: status=%s response=%s",
                            response.status_code,
                            response.text[:2000],
                        )

                    response.raise_for_status()

                    data = response.json()

                    candidates = data.get("candidates", [])

                    if not candidates:
                        logger.warning(
                            "Gemini returned no candidates. Response keys: %s",
                            list(data.keys()),
                        )
                        return None

                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])

                    value = "".join(
                        part.get("text", "")
                        for part in parts
                        if isinstance(part, dict)
                    )

                    return value.strip() or None

                # ==========================================
                # GROQ / OPENAI / OPENAI-COMPATIBLE
                # ==========================================
                if self.provider in {
                    "groq",
                    "openai",
                    "openai-compatible",
                }:

                    if self.provider == "groq":
                        base = (
                            settings.llm_base_url
                            or "https://api.groq.com/openai/v1"
                        )

                    elif self.provider == "openai":
                        base = (
                            settings.llm_base_url
                            or "https://api.openai.com/v1"
                        )

                    else:
                        base = settings.llm_base_url

                    if not base:
                        raise LLMUnavailable(
                            "LLM_BASE_URL is required for "
                            "openai-compatible provider"
                        )

                    headers["Authorization"] = (
                        f"Bearer {settings.llm_api_key}"
                    )

                    payload = {
                        "model": self.model,
                        "temperature": 0.1,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Answer only from supplied scientific evidence. "
                                    "Never invent facts. "
                                    "Cite every factual claim with [S1], [S2] "
                                    "source markers. "
                                    "If evidence is missing, say not found in "
                                    "the data. "
                                    "Respect partial-gravity and rocket-scope "
                                    "guardrails."
                                ),
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],
                    }

                    response = await client.post(
                        base.rstrip("/") + "/chat/completions",
                        headers=headers,
                        json=payload,
                    )

                    response.raise_for_status()

                    data = response.json()

                    value = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content")
                    )

                    return (
                        value.strip()
                        if isinstance(value, str) and value.strip()
                        else None
                    )

                # ==========================================
                # OLLAMA
                # ==========================================
                if self.provider == "ollama":
                    payload = {
                        "model": settings.ollama_model,
                        "stream": False,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        "options": {
                            "temperature": 0.1,
                            "num_ctx": 4096,
                            "num_predict": 700,
                        },
                    }

                    response = await client.post(
                        settings.ollama_url,
                        headers=headers,
                        json=payload,
                    )

                    response.raise_for_status()

                    value = (
                        response.json()
                        .get("message", {})
                        .get("content")
                    )

                    return (
                        value.strip()
                        if isinstance(value, str) and value.strip()
                        else None
                    )

        except httpx.HTTPStatusError as exc:
            logger.warning(
                "LLM HTTP request failed: provider=%s status=%s",
                self.provider,
                exc.response.status_code,
            )
            return None

        except httpx.TimeoutException:
            logger.warning(
                "LLM request timed out: provider=%s",
                self.provider,
            )
            return None

        except Exception as exc:
            # Do not log request headers, query strings,
            # request bodies or credentials.
            logger.warning(
                "LLM request failed: provider=%s error=%s",
                self.provider,
                type(exc).__name__,
            )
            return None

        return None
