from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.retrieval import ResearchRetriever


class CatalogService:
    def __init__(self, catalog_path: Path, retriever: ResearchRetriever):
        self.catalog_path = catalog_path
        self.retriever = retriever
        self.records = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else []

    def list(self, query: str = "", domain: str = "") -> List[Dict[str, Any]]:
        out = []
        q = query.casefold().strip()
        for item in self.records:
            hay = (item.get("name", "") + " " + item.get("category", "") + " " + " ".join(item.get("aliases", []))).casefold()
            if q and q not in hay and not any(q in x.casefold() for x in item.get("aliases", [])):
                continue
            if domain and domain.casefold() != item.get("category", "").casefold():
                continue
            docs = self.retriever.retrieve(item["name"], top_k=3)
            local_sources = sorted({d["source_file"] for d in docs})
            out.append({**item, "corpus_match": bool(local_sources), "local_source_files": local_sources})
        return out

    def detail(self, name: str) -> Dict[str, Any]:
        items = self.list(query=name)
        exact = next((x for x in items if x["name"].casefold() == name.casefold()), None)
        if not exact:
            raise KeyError(name)
        docs = self.retriever.retrieve(name + " " + " ".join(exact.get("aliases", [])), top_k=10)
        return {**exact, "evidence": [{"title": d["title"], "source_file": d["source_file"], "page": d["page_number"], "excerpt": d["text"][:500], "source_url": d.get("source_url")} for d in docs]}

    def rank(self, habitat: str, top_k: int = 8) -> List[Dict[str, Any]]:
        terms = {
            "moon base": "solid material flammability oxygen enriched atmosphere airflow spacecraft habitat",
            "space station": "fire smoke aerosol detection suppression flame spread microgravity",
            "mars habitat": "solid material flammability oxygen enriched atmosphere airflow habitat",
            "pressurized rover": "smoke aerosol detection airflow fire suppression confined vehicle materials",
        }
        query = terms.get(habitat.casefold(), habitat) + " " + habitat
        ranked = []
        for item in self.records:
            docs = self.retriever.retrieve(item["name"] + " " + query, top_k=2)
            score = max([d["score"] for d in docs], default=0.0)
            if score > 0:
                ranked.append({"name": item["name"], "category": item["category"], "relevance_score": round(score, 4), "rationale": item.get("rationale", "Evidence overlap with the supplied corpus; not a validated risk score."), "evidence_count": len(docs), "source_files": sorted({d["source_file"] for d in docs})})
        ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
        return ranked[:max(1, min(top_k, 20))]
