#!/usr/bin/env bash
# Optional downloads only. Nothing is downloaded into the distributable source tree.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python - <<'PY'
try:
    from huggingface_hub import snapshot_download
except ImportError as exc:
    raise SystemExit("Install optional dependencies first: pip install -r backend/requirements-optional.txt") from exc
from pathlib import Path

cache = Path(".model_cache")
cache.mkdir(exist_ok=True)
path = snapshot_download(
    repo_id="intfloat/multilingual-e5-base",
    cache_dir=str(cache),
)
print("Downloaded embedding model cache:", path)
PY
if [ -n "${NER_MODEL_REPO_ID:-}" ]; then
  python - <<'PY'
import os
from pathlib import Path
from huggingface_hub import snapshot_download
repo = os.environ["NER_MODEL_REPO_ID"]
path = snapshot_download(repo_id=repo, local_dir=str(Path(".model_cache") / "scibert_nasa_ner"))
print("Downloaded configured NER checkpoint:", path)
PY
else
  echo "NER_MODEL_REPO_ID is unset. No fine-tuned SciBERT checkpoint was supplied, so it was not guessed or downloaded."
fi
