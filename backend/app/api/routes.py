from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel, Field, field_validator

from app.core.config import settings
from app.services.comparison_service import compare_investigation
from app.services.ner_service import extract_numeric_parameters

router = APIRouter()
SCENARIOS = {"Moon base", "Space station", "Mars habitat", "Pressurized rover"}

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    scenario: str = Field(default="Space station", max_length=100)
    @field_validator("message")
    @classmethod
    def strip_message(cls, v):
        v = v.strip()
        if not v: raise ValueError("message must not be blank")
        return v
    @field_validator("scenario")
    @classmethod
    def validate_scenario(cls, v):
        return v if v in SCENARIOS else "Space station"

class CompareRequest(BaseModel):
    investigations: List[str] = Field(min_length=2, max_length=6)
    @field_validator("investigations")
    @classmethod
    def unique_studies(cls, v):
        result = list(dict.fromkeys(x.strip() for x in v if x.strip()))
        if len(result) < 2: raise ValueError("At least two distinct investigations are required")
        return result

class RankRequest(BaseModel):
    habitat_type: str = Field(min_length=2, max_length=120)
    top_k: int = Field(default=8, ge=1, le=20)


class ControlsInsightsRequest(BaseModel):
    topic: str = Field(default="fire safety controls and equipment", min_length=3, max_length=300)
    habitat_type: str = Field(default="Space station", max_length=100)
    top_k: int = Field(default=8, ge=1, le=15)
    include_earth_applications: bool = False

class ModelingRequest(BaseModel):
    text: Optional[str] = Field(default=None, max_length=20000)
    query: Optional[str] = Field(default=None, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=10)
    @field_validator("text", "query")
    @classmethod
    def strip_optional(cls, v):
        return v.strip() if isinstance(v, str) else v


def _state(request: Request, name: str):
    value = getattr(request.app.state, name, None)
    if value is None: raise HTTPException(status_code=503, detail=f"{name} service is not ready")
    return value

@router.post("/api/chat", tags=["frontend contract"])
async def chat(body: ChatRequest, request: Request):
    rag = _state(request, "rag")
    key = f"chat:{body.scenario.casefold()}:{body.message.casefold()}"
    cache = _state(request, "cache")
    cached = cache.get(key)
    if cached is not None: return cached
    result = await rag.answer(body.message, body.scenario, top_k=5)
    # Frontend contract: it reads answer (or response) and citations[{title,url}].
    payload = {"answer": result["answer"], "citations": result.get("citations", [])}
    cache.set(key, payload)
    return payload

@router.get("/api/investigations", tags=["research"])
async def list_investigations(request: Request, q: str = "", domain: str = ""):
    catalog = _state(request, "catalog")
    return {"count": len(catalog.list(q, domain)), "investigations": catalog.list(q, domain)}

@router.get("/api/investigations/{investigation_name}", tags=["research"])
async def get_investigation(investigation_name: str, request: Request):
    try: return _state(request, "catalog").detail(investigation_name)
    except KeyError: raise HTTPException(status_code=404, detail="Investigation is not in the supported challenge catalog")

@router.post("/api/compare", tags=["research"])
async def compare(body: CompareRequest, request: Request):
    retriever = _state(request, "retriever")
    ner = _state(request, "ner")
    studies = []
    for name in body.investigations:
        docs = retriever.retrieve(name, top_k=8, filters={"investigation": name})
        studies.append(compare_investigation(name, docs, ner))
    return {"comparisons": studies, "limitations": ["Missing values are left unspecified rather than inferred.", "The current corpus is partial and is not a validated predictive fire-risk dataset."]}

@router.post("/api/rank", tags=["research"])
async def rank(body: RankRequest, request: Request):
    catalog = _state(request, "catalog")
    return {"habitat_type": body.habitat_type, "ranking_type": "retrieval_relevance_not_fire_risk", "results": catalog.rank(body.habitat_type, body.top_k), "limitations": ["Scores indicate textual evidence relevance only, not hazard probability, flammability, or safety certification."]}

@router.post("/api/modeling/extract", tags=["nlp"])
async def extract_modeling_features(body: ModelingRequest, request: Request):
    ner = _state(request, "ner")
    retriever = _state(request, "retriever")
    text = body.text or ""
    sources = []
    entity_records = []
    numeric_records = []
    if not text and body.query:
        docs = retriever.retrieve(body.query, top_k=body.top_k)
        sources = [{"title": d["title"], "source_file": d["source_file"], "page": d["page_number"], "url": d.get("source_url")} for d in docs]
        for doc in docs:
            result = ner.extract(doc["text"])
            for entity in result["entities"]:
                entity_records.append({**entity, "source_file": doc["source_file"], "page": doc["page_number"]})
            for value in extract_numeric_parameters(doc["text"]):
                numeric_records.append({**value, "source_file": doc["source_file"], "page": doc["page_number"], "source_url": doc.get("source_url")})
        method = ner.mode
        warning = "Values are extracted from retrieved papers; verify source metadata before treating them as test conditions."
    elif text.strip():
        result = ner.extract(text)
        entity_records = result["entities"]
        numeric_records = extract_numeric_parameters(text)
        method = result["method"]
        warning = result.get("warning")
    else:
        raise HTTPException(status_code=422, detail="Provide either text or query")
    parameters = {}
    for entity in entity_records:
        parameters.setdefault(entity["entity"], []).append({
            "text": entity["text"], "start": entity["start"], "end": entity["end"],
            "extraction_method": entity["method"],
            **({"source_file": entity["source_file"], "page": entity["page"]} if entity.get("source_file") else {}),
        })
    return {
        "parameters": parameters, "entities": entity_records,
        "numeric_parameters": numeric_records, "method": method, "sources": sources,
        "warning": warning,
        "note": "Values retain their source units and nearby context. They are extracted mentions, not automatically verified test metadata or a validated predictive dataset.",
    }

@router.post("/api/ner/extract", tags=["nlp"])
async def ner_extract(body: ModelingRequest, request: Request):
    return await extract_modeling_features(body, request)

@router.get("/api/insights", tags=["research"])
async def insights(request: Request, topic: str = Query(default="", max_length=120)):
    retriever = _state(request, "retriever")
    query = topic or "spacecraft fire safety flame spread smoke aerosol detection suppression materials"
    docs = retriever.retrieve(query, top_k=10)
    by_type: Dict[str, List[Dict[str, Any]]] = {}
    for d in docs:
        by_type.setdefault(d.get("evidence_type", "not specified"), []).append({"title": d["title"], "source_file": d["source_file"], "page": d["page_number"], "excerpt": d["text"][:420], "source_url": d.get("source_url")})
    return {"topic": query, "evidence_groups": by_type, "interpretation": "Evidence map only; no causal conclusions or fire-risk predictions are generated."}

@router.post("/api/insights/controls", tags=["research"])
async def control_insights(body: ControlsInsightsRequest, request: Request):
    retriever = _state(request, "retriever")
    rag = _state(request, "rag")
    query = body.topic + " detection suppression smoke aerosol material flammability fire control equipment " + body.habitat_type
    if body.include_earth_applications:
        query += " Earth firefighter protective equipment fine water mist"
    docs = retriever.retrieve(query, top_k=body.top_k)
    groups: Dict[str, List[Dict[str, Any]]] = {"detection": [], "suppression": [], "materials_and_prevention": [], "earth_applications": []}
    for doc in docs:
        text = doc["text"].casefold()
        item = {"title": doc["title"], "source_file": doc["source_file"], "page": doc["page_number"], "excerpt": doc["text"][:520], "source_url": doc.get("source_url")}
        if any(term in text for term in ["smoke", "aerosol", "particle counter", "particle size", "sensor", "detector"]):
            groups["detection"].append(item)
        if any(term in text for term in ["extinguish", "extinction", "suppress", "suppression", "water mist", "helium", "carbon dioxide"]):
            groups["suppression"].append(item)
        if any(term in text for term in ["flammability", "flame spread", "solid fuel", "material", "ignition"]):
            groups["materials_and_prevention"].append(item)
        if body.include_earth_applications and any(term in text for term in ["earth application", "firefighter", "wildland fire", "building fire", "industrial fire"]):
            groups["earth_applications"].append(item)
    answer = await rag.answer(body.topic + " for " + body.habitat_type, body.habitat_type, top_k=body.top_k)
    return {
        "habitat_type": body.habitat_type,
        "topic": body.topic,
        "answer": answer["answer"],
        "citations": answer.get("citations", []),
        "evidence_groups": {key: unique for key, unique in ((k, v[:5]) for k, v in groups.items()) if unique},
        "earth_applications_requested": body.include_earth_applications,
        "earth_applications_status": "evidence_found" if groups["earth_applications"] else "not_found_in_retrieved_corpus" if body.include_earth_applications else "not_requested",
        "limitations": ["Keyword-grouped evidence is a discovery aid, not a validated equipment recommendation.", "Do not infer a detector or suppressant specification without run-level test data and engineering qualification."],
    }

@router.get("/api/media", tags=["media"])
async def list_media(request: Request, investigation: str = ""):
    try: data = json.loads(settings.media_path.read_text(encoding="utf-8"))
    except Exception: data = []
    if investigation:
        data = [x for x in data if investigation.casefold() in str(x.get("investigation", "")).casefold() or investigation.casefold() in str(x.get("title", "")).casefold()]
    return {"count": len(data), "media": data}

@router.post("/api/vision/analyze", tags=["vision"])
async def vision_analyze(
    request: Request,
    file: UploadFile = File(...),
    experiment_id: Optional[str] = Form(default=None),
    metadata_json: Optional[str] = Form(default=None),
):
    vision = _state(request, "vision")
    raw = await file.read(settings.max_upload_bytes + 1)
    if len(raw) > settings.max_upload_bytes: raise HTTPException(status_code=413, detail="Uploaded media exceeds MAX_UPLOAD_BYTES")
    filename = file.filename or "upload.bin"
    content_type = file.content_type or ""
    metadata = None
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
            if not isinstance(metadata, dict): raise ValueError("metadata_json must be an object")
        except Exception: raise HTTPException(status_code=422, detail="metadata_json must be a valid JSON object")
    suffix = re.sub(r"[^a-z0-9.]", "", filename.lower())
    is_video = content_type.startswith("video/") or suffix.endswith((".mp4", ".mov", ".avi", ".mkv"))
    try:
        if is_video:
            result = vision.analyze_video(raw, filename, experiment_id, metadata)
            return {"media_type": "video", "result": result, "scientific_status": "prototype_visual_analysis_not_NASA_validated"}
        if not (content_type.startswith("image/") or suffix.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"))):
            raise HTTPException(status_code=415, detail="Upload an image or video file")
        result = vision.analyze_image(raw, filename)
        return {"media_type": "image", "result": result, "scientific_status": "heuristic_visual_analysis_not_NASA_validated"}
    except HTTPException: raise
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Media analysis failed: {type(exc).__name__}")
