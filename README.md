# Beyond the Flame — Integrated NASA Microgravity Fire-Safety Research API

This repository combines the supplied Next.js dashboard, the partial PSI/NASA research corpus, NLP assets and the teammate OpenCV combustion-video pipeline. The backend is newly integrated around the frontend's existing API contract. The dashboard source is preserved as read-only; no frontend edits are required.

> **Scope:** this is an evidence-discovery prototype, not a certified spacecraft fire-risk model or operational safety system. It never invents experimental values, partial-gravity results, or source links.

## 1. What is included

- `frontend/` — supplied Next.js 16 / React 19.2 UI. It is read-only and byte-identical to the extracted original snapshot.
- `backend/` — FastAPI app, typed request validation, lifecycle-loaded NLP/RAG/LLM/CV services, source corpus and media/investigation metadata.
- `source_data/` — teammate source assets preserved for provenance, including the RAG chunks/vector files, NLP data, original `ner_inference.py`, outputs, setup notebook and the combustion-analysis pipeline.
- `eval/` — 40 retrieval questions and measured BM25 vs hybrid evaluation report.
- `scripts/` — reproducible corpus build, evaluation, model download, NASA media metadata harvesting, and safe local run scripts.
- `docs/` — frontend contract, source audit and scientific limitations.

The rebuilt runtime corpus has **615 chunks across 28 source files** (27 PDF research sources plus one metadata text file). The original RAG archive supplied 614 retrieval chunks. A verified document-specific source URL is present for all 28 documents (26 DOI links, one NASA NTRS source, and one exact NASA PSI record). DOI-only mappings were confirmed against the exact PDF titles/abstracts/authors; unknown links are never guessed. These files are a partial curated corpus, not a complete NASA PSI data mirror.

## 2. Run locally (Windows PowerShell)

Use Python 3.11–3.13 and Node.js 20.9+ (Node 22 recommended).

```powershell
# From the project root
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` only if you want an external LLM provider (see **LLM setup** below). Start the backend in terminal 1:

```powershell
.\scripts\run_backend.ps1
```

Start the frontend in terminal 2:

```powershell
.\scripts\run_frontend_copy.ps1
```

The frontend script copies `frontend/` into `.runtime/frontend/` and runs `npm ci` only in that copy. The original `frontend/` directory is never modified. Open `http://localhost:3000`. The API listens at `http://127.0.0.1:8000`; Swagger UI is at `http://127.0.0.1:8000/docs`.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
./scripts/run_backend.sh
```

In a second terminal, run `./scripts/run_frontend_copy.sh`. It creates `.runtime/frontend/`, installs there, and points the copied UI to `http://localhost:8000`.

## 3. LLM setup (optional)

The default is `LLM_PROVIDER=disabled`. All RAG/research features still work through extractive fallback; `/health` reports the active mode. To enable an LLM, put your provider details in the **root** `.env` file (never in `frontend/`, Python source, or source control). Do not include `.env` in a handoff ZIP.

| Provider | `.env` settings | Key/setup page |
|---|---|---|
| Gemini | `LLM_PROVIDER=gemini`, `LLM_MODEL=gemini-2.5-flash`, `LLM_API_KEY=...` | [Google AI Studio API keys](https://aistudio.google.com/app/apikey) |
| Groq | `LLM_PROVIDER=groq`, `LLM_MODEL=<supported Groq model>`, `LLM_API_KEY=...` | [Groq API keys](https://console.groq.com/keys) |
| OpenAI | `LLM_PROVIDER=openai`, `LLM_MODEL=<supported model>`, `LLM_API_KEY=...` | [OpenAI API keys](https://platform.openai.com/api-keys) |
| OpenAI-compatible | `LLM_PROVIDER=openai-compatible`, `LLM_BASE_URL=https://.../v1`, `LLM_MODEL=...`, `LLM_API_KEY=...` | Use the endpoint and key provided by that service |
| Ollama | `LLM_PROVIDER=ollama`, `OLLAMA_URL=http://localhost:11434/api/chat`, `OLLAMA_MODEL=qwen2.5:1.5b` | [Ollama](https://ollama.com/) — install/pull a model locally; no API key required |

The provider adapter has a timeout and bounded concurrency. On provider/API errors or missing credentials, requests fall back to extractive RAG rather than pretending an LLM succeeded. LLM output is accepted only when it cites valid retrieved source markers that resolve to source URLs. A local `.env` key is not written to logs or the ZIP.

**Security:** any API credential pasted into chat or another public/shared surface should be revoked/rotated with its provider before use. The key-like text supplied alongside this task was not added to any project file because its provider and validity are not established.

## 4. Optional neural retrieval and NER

The base install uses BM25 + TF-IDF, title matching, and source-diversity reranking. The original Chroma store is preserved but is not activated by default because the matching E5 checkpoint/runtime was not provided.

To enable dense E5 retrieval:

```bash
pip install -r backend/requirements-optional.txt
./scripts/download_models.sh
```

Then set in `.env`:

```env
EMBEDDING_ENABLED=true
EMBEDDING_MODEL=intfloat/multilingual-e5-base
HF_HOME=./.model_cache
```

Restart the backend. Corpus passage embeddings are computed once at startup and cached in memory for requests. Model files are not bundled in the ZIP.

For SciBERT, set `NER_MODEL_DIR` to a local fine-tuned token-classification checkpoint directory containing a matching model config/weights/tokenizer. No compatible fine-tuned SciBERT weight folder was present in the uploads, and no unknown checkpoint was guessed. A repository can be downloaded through `scripts/download_models.sh` only after setting the actual `NER_MODEL_REPO_ID`.

## 5. Main API

- `POST /api/chat` — exact supplied UI contract: `{ "message": "...", "scenario": "Space station" }`; returns `{ "answer": "...", "citations": [{"title":"...","url":"https://..."}] }`.
- `GET /health` — checks RAG, NLP, LLM and vision service state, including active fallback/LLM mode.
- `GET /api/investigations` and `GET /api/investigations/{name}` — investigation catalogue and retrieved evidence.
- `POST /api/compare` — 2–6 investigations; returns objectives/conditions/variables/hardware/sensor mentions only when present in retrieved sources.
- `POST /api/rank` — rank by text relevance to a habitat (not validated risk or flammability).
- `POST /api/modeling/extract` and `POST /api/ner/extract` — use `text` or `query`; return entity mentions and numeric values with original units/context and source/page provenance.
- `GET /api/insights` — grouped research evidence.
- `POST /api/insights/controls` — detection, suppression and material/prevention evidence; optional Earth-application evidence search.
- `GET /api/media` — NASA image/video metadata (three NASA SVS media references; binary downloads are not included).
- `POST /api/vision/analyze` — multipart `file` upload for image/video, optional `experiment_id` and JSON `metadata_json` form fields.

Full input/output schemas are generated at `/openapi.json` and `/docs`. The contract audit and endpoints are documented in `docs/FRONTEND_API_CONTRACT.md`.

## 6. Run tests and evaluation

```bash
PYTHONPATH=backend pytest -q backend/tests
PYTHONPATH=source_data/combustion_behavior_analysis/src pytest -q source_data/combustion_behavior_analysis/tests
PYTHONPATH=backend python scripts/evaluate.py
```

`eval/metrics.json` records the actual before/after retrieval results. On 40 curated questions, hybrid retrieval raised top-1 expected-source accuracy from 72.50% to 75.00%, MRR from 0.8183 to 0.8308, and strict expected-source citation precision@3 from 49.17% to 51.67%; recall@5 remained 100% in both runs. Expected-term evidence coverage@5 changed from 95.42% to 94.17%. This last value is only a lexical retrieval-support proxy. Human-reviewed semantic answer faithfulness was not measured; do not interpret these retrieval metrics as scientific prediction accuracy. `eval/golden_qa.jsonl` is a manually curated test set, not an independent scientific validation set.

Rebuild the corpus from the preserved teammate RAG files with:

```bash
python scripts/build_index.py
```

## 7. Docker deployment

```bash
cp .env.example .env       # optional; configure LLM settings if needed
 docker compose up --build
```

Open `http://localhost:8080`. Nginx forwards `/api/*` to FastAPI and all other paths to Next.js. The supplied frontend uses a relative API path in this mode; no source changes are made. For a backend-only run, use the local script or `docker compose up backend`.

## 8. NASA media collection

The repository currently includes three NASA SVS SoFIE media references in `backend/data/media/metadata.json`, with NASA source page, direct URL and credit. `downloaded: false` is explicit. To query the public NASA Image and Video Library API and extend the metadata file, run:

```bash
python scripts/harvest_nasa_media.py --query "microgravity combustion" --limit 30
```

The harvester makes metadata-only requests by default and never claims that SoFIE images are Saffire footage. Review usage/licensing guidance on each source page before redistribution.

## 9. Important scientific limits

- No direct partial-gravity combustion results are claimed. E-FIELD is an electric-field analogue, not lunar/Martian gravity. Microgravity and 1g evidence may bound but cannot establish intermediate-gravity behavior.
- Rocket and propellant fire safety is out of scope.
- Challenge-provided Moon-base and spacesuit atmospheres are scenario assumptions, not experiment outputs or final specifications.
- Retrieval relevance scores are not hazard or risk scores.
- NER neural weights are absent; rule/lexicon extraction is the default. The supplied NER report covers only 6 test sentences (P=0.5263, R=0.5882, F1=0.5556).
- CV is heuristic OpenCV analysis with no labeled NASA image evaluation. Pixel measures are not physical units without calibration; optical flow is not gas velocity; image appearance/disappearance is not proof of ignition/extinction.
- The corpus is partial. Missing values and unknown document URLs remain explicitly missing.

Read `PROJECT_REPORT.md`, `docs/AUDIT_REPORT.md`, `docs/SCIENTIFIC_SCOPE.md`, and `SUGGESTIONS.md` before interpreting results.
