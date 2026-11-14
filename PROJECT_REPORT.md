# PROJECT REPORT — Beyond the Flame

**Build date:** 14 November 2026  
**Project type:** NASA PSI microgravity-combustion evidence dashboard and research API  
**Status:** Backend implemented and locally testable; frontend source preserved; frontend production build and Docker image build remain unverified in this environment.

## 1. Executive summary

The supplied materials have been integrated into one project with the original Next.js frontend left unchanged and read-only. A new FastAPI backend implements the frontend's existing `/api/chat` contract and adds APIs for investigation search, ranking, comparison, parameter extraction, control-system insights, media metadata, and image/video analysis.

The backend runs by default without an external LLM key using local BM25 + TF-IDF evidence retrieval and extractive responses. Optional Gemini, Groq, OpenAI, OpenAI-compatible and Ollama adapters are available. Optional dense multilingual E5 embeddings and the supplied SciBERT NER inference path can be activated when their model weights are available. The provided upload did not contain those weight files, so neither is represented as active by default.

This is an evidence discovery prototype, **not** a certified spacecraft fire-risk predictor. No synthetic result is presented as a NASA experiment, and no risk/flammability probability is generated from retrieval scores.

## 2. Original materials and audit results

| Material | What was supplied | Integration decision |
|---|---|---|
| Next.js frontend ZIP | Next.js 16, React 19.2, TypeScript 5.7; 30 frontend files | Kept in `frontend/`, checksummed, read-only, and unchanged. |
| NASA RAG ZIP | 614 preprocessed retrieval chunks, metadata/catalogues, 27 PDF research files, existing Chroma vectors | Preserved under `source_data/nasa_rag/`; runtime corpus regenerated as portable JSONL. Original Chroma assets kept as provenance, not required by default runtime. |
| NLP ZIP | cleaned research text, data/features, labels and training assets | Preserved under `source_data/nlp/`; integrated an explainable rule/lexicon entity extractor and numeric-condition parser. |
| Outputs ZIP | NER training/evaluation summaries and predictions | Preserved; six-sentence test split is reported with sample-size limitations. |
| NASA challenge ZIP | additional NASA research/data and metadata | Preserved; stale absolute Windows paths are not used by runtime. |
| PSI-26 data ZIP | empty directory entries only | No data inferred or fabricated. |
| `ner_inference.py` | SciBERT token-classification loading and BIO decoding utility | Preserved and used by optional service only when a compatible local model directory exists. Weights were not supplied. |
| Combustion analysis ZIP | original OpenCV pipeline, tests, synthetic sample video | Pipeline reused for video requests; test assets retained and limitations exposed in API. |
| Setup notebook | project/setup notebook | Preserved as reference; not an application dependency. |

The original Chroma collection advertises 614 vectors of dimension 768. Its matching embedding checkpoint and a reproducible runtime setup were not present. The uploaded E5 model cache and SciBERT model weight files were also absent. The backend therefore uses its own BM25 + TF-IDF index immediately, rather than silently depending on missing weights.

The generated corpus has **615 chunks across 28 documents** (614 source chunks plus one PSI-60 metadata record). The source manifest contains a verified document-specific URL for all 28/28 documents: 26 DOI links, one NASA NTRS source, and one exact PSI record. For four PDFs whose extracted metadata omitted a DOI, the paper was matched using the full abstract and author/title details before assigning the DOI. No guessed URLs are inserted.

## 3. Frontend API contract and unchanged proof

The original `frontend/components/copilot.tsx` contains the only active frontend network call:

- `POST ${NEXT_PUBLIC_API_BASE_URL || ''}/api/chat`
- `Content-Type: application/json`
- body: `{ "message": string, "scenario": string }`
- response consumed as `answer` or `response`, with optional `citations: [{title, url}]`
- no Authorization header, WebSocket, SSE, or other API call was found in the supplied frontend source.

The backend returns `{answer, citations}` as the expected stable shape. The contract is documented in `docs/FRONTEND_API_CONTRACT.md`.

Frontend-preservation verification:

- Source snapshot: `../_original_backup/extracted/frontend/`
- Working frontend: `frontend/`
- File count: 30
- `diff -qr` result: no differences
- SHA-256 checksum verification: all entries match `docs/frontend_checksums.sha256`
- `find frontend -type f -newer ../frontend_checksums.txt`: zero files
- `frontend/` permissions: read-only (`a-w` removed)

The frontend was never used as an npm working directory. A separate copied build was attempted under `.runtime/frontend`, but `npm ci` could not fetch registry packages because of DNS/network failure (`EAI_AGAIN`) and was stopped. The temporary copy was removed. Thus the frontend's npm build is **not verified**, but the original frontend remains byte-identical.

## 4. Backend implementation

### Services

- `retrieval.py`: token BM25 + TF-IDF hybrid retrieval, query expansion/aliases, metadata filtering, title boosts and source diversity. Embedding support can load `intfloat/multilingual-e5-base` when enabled and downloaded; it is disabled by default.
- `rag_service.py`: extracts evidence and sources, supports English/Arabic answers, guards against unsupported partial-gravity and rocket/propellant claims, and rejects LLM output whose source markers are invalid or unresolved. Falls back to extractive evidence if LLM credentials/network are absent or output fails validation.
- `llm_service.py`: Gemini, Groq, OpenAI, OpenAI-compatible and Ollama adapters with timeout and bounded concurrency. Keys are read only from the root `.env` and are not embedded in the repository.
- `ner_service.py`: explainable entity lexicon/rules and numeric extraction that retains source units/context. SciBERT can be enabled through `NER_MODEL_DIR` when compatible fine-tuned weights are available.
- `comparison_service.py`: extracts research excerpts and parameter mentions for each investigation, leaving unsupported fields as not specified.
- `catalog_service.py`: investigation catalogue/details and habitat-relevance ranking. Scores are explicitly labelled `retrieval_relevance_not_fire_risk`.
- `vision_service.py`: image-level OpenCV morphology/color/shape measurements plus the original teammate video-analysis pipeline.
- `cache.py`, `runtime.py`: response cache and request rate limiting.

### API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Service status and selected LLM/fallback mode |
| `POST /api/chat` | Exact original frontend contract |
| `GET /api/investigations` | Search/list investigation metadata |
| `GET /api/investigations/{name}` | One investigation details |
| `POST /api/compare` | Compare investigation evidence and source-specific values |
| `POST /api/rank` | Rank evidence relevance for a habitat type (not physical risk) |
| `POST /api/modeling/extract` | Extract numeric parameters, entities, units and context for downstream modelling |
| `POST /api/ner/extract` | Entity extraction |
| `GET /api/insights` | Grouped research insights |
| `POST /api/insights/controls` | Detection, suppression, material/prevention evidence; optional Earth-applications query |
| `GET /api/media` | Curated NASA media records and source references |
| `POST /api/vision/analyze` | Image or video upload and visual feature analysis |

Interactive OpenAPI documentation is generated by FastAPI at `/docs`; raw schema is `/openapi.json`.

## 5. Retrieval evaluation (measured)

The included `eval/golden_qa.jsonl` contains 40 manually curated retrieval questions, built from the supplied research corpus. Baseline is BM25-only. The hybrid configuration adds TF-IDF, title boosts and source-diversity reranking.

| Metric | BM25 baseline | Hybrid | Change |
|---|---:|---:|---:|
| Retrieval recall@5 | 100.00% | 100.00% | No change |
| Top-1 expected-source accuracy | 72.50% | 75.00% | +2.50 percentage points |
| Mean reciprocal rank | 0.8183 | 0.8308 | +0.0125 |
| Strict expected-source citation precision@3 | 49.17% | 51.67% | +2.50 percentage points |
| Expected-term evidence coverage@5 | 95.42% | 94.17% | -1.25 percentage points |

These figures are **retrieval metrics on a small curated set**, not prediction accuracy. Citation precision is strict against the question's expected-source labels and may penalize other relevant sources. Expected-term coverage is a lexical support proxy. Semantic answer faithfulness was not human-reviewed or measured because no expert-annotated answer set was supplied. There is no measured before/after improvement claim for semantic correctness.

The supplied NER artifact reports 44 training, 5 validation and 6 test sentences; 17 true entities, 19 predicted entities and 10 correct; precision 0.5263, recall 0.5882 and F1 0.5556. That test sample is too small to claim production-grade NER accuracy.

## 6. Computer vision and media

`POST /api/vision/analyze` accepts image/video uploads. Image features are heuristic OpenCV measurements (segmented area, bounding box/aspect ratio, brightness/color distributions and flame-shape descriptors). Video analysis reuses the uploaded team's existing pipeline. A smoke test processed 36 frames from the supplied **synthetic demonstration clip**. This validates code execution only, not science accuracy or NASA footage classification.

Limitations returned by the service include: pixel measures are not physical units without calibration; optical flow is not gas velocity; visual disappearance is not proof of extinction; hue heuristics can miss blue/dim flame regions; no labelled NASA media set or validated classifier was supplied.

Three NASA SVS media references are included with credits and original source/direct URLs. Their media binaries were not downloaded. They are SoFIE media, not relabelled as Saffire footage. The NASA Images and Video Library harvester is metadata-only by default and explicitly separates previews from asset manifests.

## 7. Scientific guardrails and scope

- Do not claim PSI partial-gravity combustion measurements exist. E-FIELD Flames use electric fields as an analogue, not a true partial-gravity environment. Microgravity and 1g observations can inform bounds but do not establish intermediate-gravity behavior.
- Rocket/propellant fire safety remains out of scope.
- Challenge atmospheric values for Moon bases, spacesuits and Earth are context scenarios, not experimental PSI measurements.
- CFI-G's high oxygen fraction is the burner oxidizer test stream; do not present it as a cabin atmosphere value.
- The system does not output a physical fire risk probability or claim predictive-model training from incomplete metadata.
- Unknown fuel sizes, sensor details, conditions, or URLs remain unknown until the underlying source supports them.

See `docs/SCIENTIFIC_SCOPE.md` for details and source policy.

## 8. How to run

### Backend local run

```bash
python -m venv .venv
# activate the environment, then:
pip install -r requirements.txt
cp .env.example .env
./scripts/run_backend.sh
```

Windows PowerShell: `py -3.13 -m venv .venv`, activate `.venv`, `pip install -r requirements.txt`, then `.\scripts\run_backend.ps1`.

### Frontend (isolated copy only)

```bash
./scripts/run_frontend_copy.sh
```

The script copies `frontend/` to `.runtime/frontend/`, installs there, and starts the copied UI. It never runs npm in the original frontend directory. Network access to npm registry is required for this first install.

### Docker

```bash
cp .env.example .env
docker compose up --build
```

The compose design routes requests via Nginx at `http://localhost:8080`, keeping the frontend's same-origin `/api/chat` URL intact. Docker and Docker Compose were not installed in the build workspace, so container build/start has not been verified here.

## 9. Secrets and API key handling

No API key is embedded in source files, logs, `.env.example`, Git commits or the ZIP. The key-like string sent in the conversation was not stored. Because it has been disclosed in a conversation, revoke/rotate it before use. After creating a fresh key with the correct provider, place it in the root `.env` alongside the matching `LLM_PROVIDER` value. Do not place it inside `frontend/`.

## 10. Files preserved, excluded and moved

- Source research, original NLP/RAG assets, existing Chroma data and CV pipeline remain under `source_data/`.
- Junk/cache files such as `.DS_Store`, `__pycache__` and `.pyc` were moved to `_trash/` with relative paths preserved. `_trash/` is excluded from the final ZIP by request, but is present in the working folder.
- ZIP excludes `.git/`, `_trash/`, `.env`, runtime caches/results, `.pytest_cache`, `__pycache__`, `.pyc`, local model caches and `node_modules`. It includes `.env.example` and all source data required for reproducibility.

## 11. Verification results and unresolved items

| Check | Result |
|---|---|
| FastAPI endpoint tests | 9/9 passed |
| Original OpenCV pipeline tests | 14/14 passed |
| Retrieval evaluation | 40 questions; metrics recorded in `eval/metrics.json` |
| API smoke run | Verified separately against local Uvicorn before packaging |
| Frontend byte diff and SHA-256 | All 30 files match; no diff |
| Frontend npm build | Not verified; registry DNS/network error `EAI_AGAIN` in isolated copy |
| Docker image/compose | Not verified; Docker CLI absent in build environment |
| E5 dense embedding model | Not supplied; optional download required |
| SciBERT NER weights | Not supplied; optional local checkpoint required |
| Expert answer-faithfulness benchmark | Not supplied; semantic evaluation remains unmeasured |
| Complete PSI run-level archive | Not supplied; the PSI-26 ZIP is empty |
| Media binaries | Not included; source metadata and links only |
| Document-level source URLs | Verified for all 28/28 documents |

No remaining blocker prevents running the default extractive FastAPI backend. The unresolved items affect optional neural modes, complete source coverage, expert validation and deployment build verification.
