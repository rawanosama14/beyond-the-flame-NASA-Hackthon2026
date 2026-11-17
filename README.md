# 🌌 Beyond the Flame — Integrated NASA Microgravity Fire-Safety Research API

> **AI-Powered Fire Safety Insights from Microgravity**  
> A scientific intelligence (SI) platform that turns decades of microgravity combustion research into structured, searchable, and actionable fire-safety knowledge for crewed spaceflight.

---

## 🔍 Overview
This repository combines the supplied Next.js dashboard, the partial PSI/NASA research corpus, NLP assets, and the teammate's OpenCV combustion-video pipeline. The backend is newly integrated around the frontend's existing API contract, bridging the gap between archival science and spacecraft design decisions.

> ⚠️ **Scope Note:** This is an evidence-discovery prototype, not a certified spacecraft fire-risk model or operational safety system. It never invents experimental values, partial-gravity results, or source links.

---

## 📂 Repository Structure

- `frontend/` — Supplied Next.js 16 / React 19.2 UI (Read-only, byte-identical to original snapshot).
- `backend/` — FastAPI application with typed request validation, lifecycle-loaded NLP/RAG/LLM/CV services, and source corpus/metadata.
- `source_data/` — Teammate source assets preserved for provenance (RAG chunks, vector files, NLP scripts, notebook, and combustion-analysis pipeline).
- `eval/` — 40 retrieval questions and measured BM25 vs. hybrid evaluation report (`metrics.json`, `golden_qa.jsonl`).
- `scripts/` — Reproducible corpus build, evaluation, model download, NASA media harvesting, and run scripts.
- `docs/` — Frontend contract, source audit, and scientific limitations.

---

## 📊 Corpus & Data Statistics
* **Runtime Corpus:** 615 chunks across 28 source files (27 PDF research sources + 1 metadata text file).
* **Provenance:** Verified document-specific source URLs for all 28 documents (26 DOI links, 1 NASA NTRS source, and 1 exact NASA PSI record).

---

## 🚀 Getting Started Locally (Windows PowerShell)

Ensure you are using **Python 3.11–3.13** and **Node.js 20.9+** (Node 22 recommended).

### 1. Setup Backend
```powershell
# From the project root
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env

```

*(Optional: Edit `.env` to configure an LLM provider if desired).*

### 2. Run Services

* **Terminal 1 (Backend):**
```powershell
.\scripts\run_backend.sh
# Or on Windows PowerShell:
.\scripts\run_backend.ps1

```


* **Terminal 2 (Frontend):**
```powershell
.\scripts\run_frontend_copy.ps1

```


* **Access Points:**
* **Frontend UI:** `http://localhost:3000`
* **Backend API & Swagger Docs:** `http://127.0.0.1:8000/docs`



---

## 🔌 Main API Endpoints

* `POST /api/chat` — Exact UI contract (`message`, `scenario`) returning answers with verified source citations.
* `GET /health` — Service state check (RAG, NLP, LLM, and vision services).
* `GET /api/investigations` — Investigation catalogue and retrieved evidence.
* `POST /api/compare` — Side-by-side comparison of 2–6 investigations by controlled variables.
* `POST /api/modeling/extract` & `POST /api/ner/extract` — Entity and numeric value extraction with source/page provenance.
* `POST /api/vision/analyze` — Multipart image/video analysis using OpenCV pipeline.

---

## 🧠 LLM & Neural Retrieval Setup (Optional)

* **Default:** `LLM_PROVIDER=disabled` (operates fully via extractive fallback RAG).
* **Supported LLM Providers:** Gemini, Groq, OpenAI, OpenAI-compatible APIs, and Ollama.
* **Dense Retrieval (E5 / SciBERT):** Optional neural embeddings can be enabled by installing `backend/requirements-optional.txt` and setting `EMBEDDING_ENABLED=true`.

---

## 📌 Important Scientific Limits

* No direct partial-gravity combustion results are claimed (microgravity and 1g bound behavior, but do not establish intermediate gravity).
* Retrieval relevance scores are **not** hazard or risk scores.
* CV analysis relies on heuristic OpenCV processing without certified NASA image benchmarks.
* Missing values and unknown document URLs remain explicitly missing.

---

## 👥 Contributors & Acknowledgments

Developed as part of the **NASA Space Apps Challenge** initiative, bridging data engineering, computer vision, and aerospace safety research.
