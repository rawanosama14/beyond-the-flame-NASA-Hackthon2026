#!/usr/bin/env python3
"""Collect NASA Image and Video Library metadata without a NASA API key.

Default behavior is metadata-only. Binary downloads are intentionally not automatic.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlencode

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "backend" / "data" / "media" / "metadata.json"
API = "https://images-api.nasa.gov/search"


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", value)[:100]


def collect(query: str, limit: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    params = {"q": query, "media_type": "image,video", "page": 1}
    with httpx.Client(timeout=30, follow_redirects=True, headers={"User-Agent": "BeyondTheFlameResearch/1.0"}) as client:
        response = client.get(API, params=params)
        response.raise_for_status()
        items = response.json().get("collection", {}).get("items", [])
        for item in items[:limit]:
            data = (item.get("data") or [{}])[0]
            nasa_id = str(data.get("nasa_id") or "")
            title = str(data.get("title") or "Untitled NASA media")
            media_type = str(data.get("media_type") or "unknown")
            preview_url = (item.get("links") or [{}])[0].get("href")
            asset_manifest = item.get("href")
            rows.append({
                "id": "nasa_images_" + safe_id(nasa_id or title),
                "title": title,
                "media_type": media_type,
                # NASA search responses expose a preview and an asset manifest,
                # not necessarily a stable human-facing detail page.
                "page_url": None,
                "preview_url": preview_url,
                "asset_manifest_url": asset_manifest,
                "credit": data.get("center") or "NASA",
                "date_created": data.get("date_created"),
                "description": (data.get("description") or "")[:1200],
                "keywords": data.get("keywords", []),
                "investigation": "Not linked to an investigation unless confirmed by source metadata",
                "downloaded": False,
                "source_api": API + "?" + urlencode(params),
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="microgravity combustion")
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    if args.limit < 1 or args.limit > 100:
        raise SystemExit("--limit must be between 1 and 100")
    rows = collect(args.query, args.limit)
    current = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else []
    known = {x.get("id") for x in current}
    added = [x for x in rows if x.get("id") not in known]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(current + added, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"NASA media metadata fetched: {len(rows)}; new records added: {len(added)}")
    print(f"Metadata path: {OUTPUT}")
    print("No media binaries were downloaded. Verify source-page credits and usage conditions before redistribution.")


if __name__ == "__main__":
    main()
