# Phase 1 — audit and gap analysis

## Inputs mapped

| Input | Audit result | Treatment |
|---|---|---|
| `Beyond-The-Flame-NextJS.zip` | Next.js 16 / React 19.2 / TypeScript 5.7; Node >=20.9; 30 source files including package lockfile. One active frontend request: `POST /api/chat` from `components/copilot.tsx`. | Extracted to `frontend/` without edits; original copy and initial file state preserved in the workspace backup. |
| `NASA.zip` | Teammate RAG source code, processed document catalogue/metadata/chunks, source PDFs, and a Chroma vector store. Processed `retrieval_chunks.jsonl` has 614 records; the saved Chroma collection has 614 vectors with 768-dimensional embeddings. | Retained under `source_data/nasa_rag/`. Rebuilt a portable JSONL corpus for the runtime. |
| `nlp.zip` | Extracted/cleaned text, feature tables, NER label/training/evaluation material, and measurement CSVs. | Retained under `source_data/nlp/`; regex fallback and optional neural inference are separated in backend service. |
| `outputs.zip` | NER reports, predictions and evaluation summaries. Test split is six sentences. | Retained under `source_data/outputs/`; metrics quoted with sample-size warning. |
| `NASA_Challenge (4).zip` | Additional challenge source documents and metadata. Some legacy metadata points to absolute Windows paths on a teammate's machine. | Retained under `source_data/nasa_challenge_data/`; backend does not depend on the stale paths. |
| `PSI-26data.zip` | Contains only empty directory entries; no usable PSI-26 dataset files. | Preserved in the original backup; flagged as missing data. |
| `01_Project_Setup.ipynb` | Setup notebook; not a production runtime dependency. | Preserved under `source_data/`. |
| `ner_inference.py` | SciBERT token-classification inference utility expects a local fine-tuned model folder. | Preserved under `source_data/ner_inference.py`; its compatible weights were not supplied. Equivalent inference decoding is loaded only when a valid local checkpoint is configured. |
| `combustion_behavior_analysis_complete.zip` | A separate, modular OpenCV video-analysis pipeline, tests, and a clearly labeled synthetic demonstration clip. | Preserved; backend video endpoint reuses its original `run_analysis` implementation. |

## Environment detected in the build workspace

- Python 3.13.5
- Node.js 22.16.0 / npm 10.9.2
- FastAPI 0.128.2 / Uvicorn 0.48.0 / Pydantic 2.13.5
- NumPy 2.3.5 / scikit-learn 1.8.0 / OpenCV 4.13.0.92 / Pandas 2.2.3 / PyYAML 6.0.3 / Matplotlib 3.10.8

## Frontend contract findings

Only one `fetch` call exists in the supplied UI: `POST ${NEXT_PUBLIC_API_BASE_URL || ''}/api/chat`, JSON body `{message, scenario}`. The component reads a string from `answer` or `response` and optional `citations` array of `{title,url}`; it sends no Authorization header and uses no streaming protocol. The backend implements this exact contract and keeps additional capabilities on separate endpoints. Full details: `docs/FRONTEND_API_CONTRACT.md`.

## Missing pieces / likely breakpoints

1. **Model weights absent:** no SciBERT fine-tuned `config.json`/`model.safetensors` bundle was supplied. No E5 SentenceTransformer cache was supplied. Neural modes are therefore not active by default.
2. **Vector store runtime incomplete:** Chroma files exist, but the exact embedding model cache and required runtime package were not supplied as one runnable setup. The vector store was preserved, but the shipped backend uses its own deterministic BM25 + TF-IDF index over source text.
3. **Dataset coverage partial:** source corpus is 614 chunks, plus one PSI-60 metadata record in the generated 615-chunk corpus. `PSI-26data.zip` is empty. Run-level data and exact condition matrices are not complete. The generated source manifest has verified document-level URLs for all 28/28 sources (26 DOIs, one NASA NTRS source and one exact PSI record). Mapped DOI matches were checked against document titles/abstracts/authors.
4. **Metadata path portability:** imported CSV metadata includes old absolute Windows file paths; backend runtime uses paths relative to this project and a newly built source manifest.
5. **NER evaluation size:** 6 test sentences (P=0.5263, R=0.5882, F1=0.5556), unsuitable for a broad accuracy claim.
6. **Media binary collection:** NASA media records are included with titles, source pages, direct URLs and credits; binary files were not downloaded in this build. They are explicitly marked `downloaded: false`.
7. **LLM credentials:** no provider can be safely inferred from a key string alone. The backend supports Gemini, Groq, OpenAI, OpenAI-compatible services and Ollama through root `.env`. No key is embedded.
8. **Scientific limitations:** no verified run-level model to predict flammability/risk; no direct PSI partial-gravity data per challenge brief; CV has no labeled NASA training set; no rocket/propellant scope.

## Fix plan implemented

- Create an immutable working frontend copy and backend-owned reverse-proxy option; never run npm inside the original frontend directory.
- Build FastAPI services for retrieval, RAG, provider-agnostic LLM, NER, comparison/ranking, media, and OpenCV video/image analysis.
- Use local BM25 + TF-IDF as an immediately runnable fallback; support optional E5 embeddings and optional SciBERT weights when available.
- Keep all numeric values in raw source units with a nearby excerpt and source/page provenance. Never fabricate missing fields.
- Add 40 curated retrieval QA questions and evaluate baseline vs hybrid ranking. Metrics are retrieval-only; no expert-reviewed answer faithfulness score is claimed.
- Add tests, Docker setup, run scripts, OpenAPI docs and explicit scientific-scope warnings.
