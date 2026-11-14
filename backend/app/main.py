from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.runtime import RateLimiter
from app.services.cache import TTLCache
from app.services.catalog_service import CatalogService
from app.services.llm_service import LLMService
from app.services.ner_service import NERService
from app.services.rag_service import RAGService
from app.services.retrieval import ResearchRetriever
from app.services.vision_service import VisionService
from app.api.routes import router

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("beyond_flame")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.retriever = None
    app.state.rag = None
    app.state.llm = LLMService()
    app.state.ner = NERService()
    app.state.vision = None
    app.state.catalog = None
    app.state.cache = TTLCache(settings.response_cache_size, settings.response_cache_ttl_seconds)
    app.state.rate_limiter = RateLimiter(settings.request_rate_limit, settings.request_rate_window_seconds)
    try:
        app.state.retriever = ResearchRetriever(
            settings.corpus_path,
            embedding_enabled=settings.embedding_enabled,
            embedding_model=settings.embedding_model,
            cache_dir=settings.embedding_cache_dir,
        )
        app.state.rag = RAGService(app.state.retriever, app.state.llm)
        app.state.catalog = CatalogService(settings.investigation_catalog_path, app.state.retriever)
        logger.info("Research corpus loaded: %s", app.state.retriever.stats())
    except Exception as exc:
        logger.exception("Research retrieval could not be initialized: %s", type(exc).__name__)
    try:
        app.state.vision = VisionService()
    except Exception as exc:
        logger.warning("Vision service unavailable: %s", type(exc).__name__)
    yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Evidence-grounded API for NASA microgravity combustion and spacecraft fire-safety research.",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

@app.middleware("http")
async def request_guard(request: Request, call_next):
    if request.url.path.startswith("/api/") or request.url.path == "/health":
        peer = request.client.host if request.client else "unknown"
        limiter = getattr(request.app.state, "rate_limiter", None)
        if limiter and not limiter.allow(peer):
            return JSONResponse(status_code=429, content={"error": {"code": "rate_limit_exceeded", "message": "Too many requests. Please retry shortly."}})
    return await call_next(request)

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled request error path=%s error=%s", request.url.path, type(exc).__name__)
    return JSONResponse(status_code=500, content={"error": {"code": "internal_error", "message": "The request could not be completed."}})

app.include_router(router)

@app.get("/", tags=["system"])
async def root():
    return {"name": settings.app_name, "version": settings.app_version, "docs": "/docs", "health": "/health"}

@app.get("/health", tags=["system"])
async def health():
    llm = app.state.llm.health() if getattr(app.state, "llm", None) else {"mode": "unavailable"}
    rag = app.state.retriever.stats() if getattr(app.state, "retriever", None) else {"loaded": False, "error": "Corpus could not be loaded"}
    nlp = app.state.ner.health() if getattr(app.state, "ner", None) else {"available": False}
    vision = app.state.vision.health() if getattr(app.state, "vision", None) else {"available": False}
    active = (
        "llm_configured_with_extract_fallback_on_error"
        if llm.get("configured") and rag.get("loaded")
        else "extractive_fallback" if rag.get("loaded") else "degraded"
    )
    return {"status": "ok" if rag.get("loaded") else "degraded", "active_mode": active, "services": {"rag": rag, "llm": llm, "nlp": nlp, "vision": vision}}
