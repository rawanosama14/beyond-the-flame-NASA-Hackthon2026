from __future__ import annotations

import os
from pathlib import Path
from typing import List

try:
    from dotenv import load_dotenv
except Exception:  # python-dotenv is optional for simple local runs
    load_dotenv = None

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if load_dotenv:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def _csv(name: str, default: str) -> List[str]:
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


class Settings:
    project_root: Path = PROJECT_ROOT
    backend_root: Path = PROJECT_ROOT / "backend"
    data_dir: Path = PROJECT_ROOT / "backend" / "data"
    corpus_path: Path = PROJECT_ROOT / "backend" / "data" / "corpus.jsonl"
    documents_path: Path = PROJECT_ROOT / "backend" / "data" / "documents.json"
    media_path: Path = PROJECT_ROOT / "backend" / "data" / "media" / "metadata.json"
    investigation_catalog_path: Path = PROJECT_ROOT / "backend" / "data" / "investigations.json"
    vision_output_dir: Path = PROJECT_ROOT / "backend" / "runtime" / "vision"

    app_name: str = os.getenv("APP_NAME", "Beyond the Flame Research API")
    app_version: str = "1.0.0"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    cors_origins: List[str] = _csv("FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    llm_provider: str = os.getenv("LLM_PROVIDER", "disabled").strip().lower()
    llm_api_key: str = os.getenv("LLM_API_KEY", "").strip()
    llm_model: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "").rstrip("/")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    llm_max_concurrency: int = int(os.getenv("LLM_MAX_CONCURRENCY", "3"))
    llm_enabled: bool = llm_provider in {"gemini", "groq", "openai", "openai-compatible", "ollama"}

    embedding_enabled: bool = os.getenv("EMBEDDING_ENABLED", "false").lower() == "true"
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
    embedding_cache_dir: Path = Path(os.getenv("HF_HOME", str(PROJECT_ROOT / ".model_cache")))
    ner_model_dir: str = os.getenv("NER_MODEL_DIR", "").strip()

    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(40 * 1024 * 1024)))
    request_rate_limit: int = int(os.getenv("REQUEST_RATE_LIMIT", "60"))
    request_rate_window_seconds: int = int(os.getenv("REQUEST_RATE_WINDOW_SECONDS", "60"))
    response_cache_ttl_seconds: int = int(os.getenv("RESPONSE_CACHE_TTL_SECONDS", "120"))
    response_cache_size: int = int(os.getenv("RESPONSE_CACHE_SIZE", "128"))


settings = Settings()
