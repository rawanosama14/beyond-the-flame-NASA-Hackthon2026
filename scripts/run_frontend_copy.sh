#!/usr/bin/env bash
# Never runs npm in the protected original frontend directory.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/frontend"
DEST="$ROOT/.runtime/frontend"
mkdir -p "$ROOT/.runtime"
if [ -e "$DEST" ]; then
  echo "Removing the previous isolated copy only: $DEST"
  rm -rf "$DEST"
fi
cp -a "$SRC" "$DEST"
chmod -R u+w "$DEST"
cd "$DEST"
npm ci
export NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000}"
npm run dev
