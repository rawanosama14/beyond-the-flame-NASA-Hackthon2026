# Frontend API contract (read-only audit)

## Contract source

The contract was derived from the supplied `frontend/components/copilot.tsx`. The shipped frontend contains one active network call: its Research Copilot uses `fetch`. No Axios, WebSocket, EventSource/SSE, polling, or other application API calls were found in the supplied frontend source.

## Required endpoint

`POST /api/chat`

Headers:

```http
Content-Type: application/json
```

Request body:

```json
{
  "message": "How does BASS compare with FLEX?",
  "scenario": "Moon base"
}
```

- `message`: non-empty string, maximum 2,000 characters in the backend.
- `scenario`: one of `Moon base`, `Space station`, `Mars habitat`, `Pressurized rover`. The backend defaults or normalizes an unknown scenario to `Space station`.
- There is no frontend-supplied Authorization header.
- The frontend uses `NEXT_PUBLIC_API_BASE_URL` after trimming a trailing slash. When empty, requests are relative to the frontend origin.

Success response (the frontend accepts `answer` or `response`; this backend uses `answer`):

```json
{
  "answer": "Evidence-grounded answer with source and page references...",
  "citations": [
    {"title": "NASA PSI source", "url": "https://psi.nasa.gov/..."}
  ]
}
```

`citations` may be an empty array when retrieved source material has no verifiable public URL in the supplied files. The answer still identifies source title and page where available. The frontend filters citations to HTTP(S) links.

## Error behavior

The frontend checks `response.ok`. On non-2xx responses or JSON without a string `answer`/`response`, it displays an explicit network/schema error and does not create a fallback AI answer. Backend error responses use HTTP status codes and FastAPI validation; rate-limit failures return HTTP 429 with an `error` object. An unavailable retrieval service returns HTTP 503.

## Hosting modes

1. **Local split process:** set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` in the copied frontend environment before starting/building it; backend listens on port 8000, frontend on 3000.
2. **Docker Compose:** frontend uses an empty API base (relative `/api/chat`); Nginx proxies `/api/*` to FastAPI and all other paths to Next.js. This avoids a frontend source/config edit.

No file in `frontend/` was edited to add these behaviors.

## Additional backend endpoints (not called by the supplied frontend)

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Component status and active LLM/fallback mode |
| GET | `/api/investigations` | Search the supported investigation catalogue |
| GET | `/api/investigations/{name}` | Investigation details and retrieved evidence |
| POST | `/api/compare` | Extractive comparison of 2–6 investigations |
| POST | `/api/rank` | Habitat-specific evidence relevance ranking (not risk score) |
| POST | `/api/modeling/extract` | Entity and numeric-unit extraction from text or retrieved sources |
| POST | `/api/ner/extract` | Alias of modeling extraction |
| GET | `/api/insights` | Evidence map by evidence type |
| POST | `/api/insights/controls` | Evidence grouped around detection, suppression and materials; optional Earth applications |
| GET | `/api/media` | NASA media metadata, optionally filtered by investigation |
| POST | `/api/vision/analyze` | Image or video analysis (multipart form upload) |

The generated OpenAPI document is available at `/openapi.json`; Swagger UI is at `/docs` when running FastAPI directly on port 8000.
