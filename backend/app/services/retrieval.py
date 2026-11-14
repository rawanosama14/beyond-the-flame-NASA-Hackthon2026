from __future__ import annotations

import json
import math
import re
import threading
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

TOKEN_RE = re.compile(r"[\w]+(?:[-’'][\w]+)*", re.UNICODE)

ALIASES = {
    "saffire": ["saffire", "spacecraft fire experiment", "flame spread", "solid fabric"],
    "bass": ["bass", "burning suppression solids", "solid fuel", "pmma"],
    "bass-ii": ["bass ii", "bass-ii", "burning suppression solids ii"],
    "same": ["same", "smoke aerosol measurement", "smoke particle", "aerosol"],
    "same-r": ["same-r", "smoke aerosol measurement reflight", "smoke particulate"],
    "daft": ["daft", "dust aerosol measurement", "p-trak", "dust detection"],
    "flex": ["flex", "flame extinguishment", "droplet combustion", "limiting oxygen index"],
    "flex-2": ["flex-2", "flex 2", "droplet combustion"],
    "cfi": ["cfi", "cool flame investigation", "cool flames"],
    "cfi-g": ["cfi-g", "cool flames investigation with gases", "spherical diffusion flames"],
    "acme": ["acme", "advanced combustion via microgravity experiments", "gaseous flames"],
    "spice": ["spice", "smoke point in co-flow experiment", "coflow diffusion flames"],
    "slice": ["slice", "structure and liftoff in combustion experiment"],
}

ARABIC_EXPANSIONS = {
    "احتراق": "combustion flame burning",
    "لهب": "flame fire",
    "حريق": "fire flame",
    "دخان": "smoke aerosol particle detector",
    "استشعار": "sensor detection aerosol",
    "اكسجين": "oxygen O2 oxidizer",
    "أكسجين": "oxygen O2 oxidizer",
    "ضغط": "pressure psi bar",
    "تدفق": "airflow flow velocity",
    "هواء": "air airflow oxygen",
    "قطرات": "droplet droplets fuel",
    "وقود": "fuel material solid liquid gaseous",
    "مواد صلبة": "solid fuel material flame spread",
    "إطفاء": "extinction extinguishment suppressant",
    "جاذبية جزئية": "partial gravity reduced gravity",
    "جاذبية صغرى": "microgravity",
}


class BM25Index:
    def __init__(self, docs: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1, self.b = k1, b
        self.tokens = [self.tokenize(d.get("text", "")) for d in docs]
        self.lengths = [len(x) for x in self.tokens]
        self.avgdl = sum(self.lengths) / max(1, len(self.lengths))
        self.term_freqs = [Counter(x) for x in self.tokens]
        df: Counter[str] = Counter()
        for terms in self.tokens:
            df.update(set(terms))
        self.idf = {term: math.log(1 + (len(docs) - freq + 0.5) / (freq + 0.5)) for term, freq in df.items()}

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return [x.casefold() for x in TOKEN_RE.findall(text or "") if len(x) > 1]

    def scores(self, query: str) -> List[float]:
        qterms = set(self.tokenize(query))
        result: List[float] = []
        for tf, dl in zip(self.term_freqs, self.lengths):
            score = 0.0
            for term in qterms:
                f = tf.get(term, 0)
                if not f:
                    continue
                idf = self.idf.get(term, 0.0)
                denom = f + self.k1 * (1 - self.b + self.b * dl / max(1.0, self.avgdl))
                score += idf * (f * (self.k1 + 1)) / denom
            result.append(score)
        return result


class ResearchRetriever:
    """Hybrid local retriever: BM25 + TF-IDF + a transparent metadata/title reranker.

    Optional sentence-transformers dense embeddings can be enabled after a model is downloaded.
    The supplied Chroma store is retained as source material, but it is not queried without the
    matching embedding weights and Chroma runtime, which were not part of the upload.
    """
    def __init__(self, corpus_path: Path, embedding_enabled: bool = False, embedding_model: str = "intfloat/multilingual-e5-base", cache_dir: Optional[Path] = None):
        self.corpus_path = Path(corpus_path)
        self.docs = self._load_docs()
        if not self.docs:
            raise RuntimeError(f"Research corpus is empty: {self.corpus_path}")
        self.bm25 = BM25Index(self.docs)
        self.vectorizer = None
        self.tfidf_matrix = None
        self.embedding_model = None
        self.doc_embeddings = None
        self.embedding_state = "disabled"
        self.embedding_error: Optional[str] = None
        self._lock = threading.Lock()
        self._build_tfidf()
        if embedding_enabled:
            self._load_embeddings(embedding_model, cache_dir)

    def _load_docs(self) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        with self.corpus_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                item = json.loads(line)
                metadata = item.get("metadata") or {}
                text = item.get("text") or item.get("chunk_text") or ""
                if not text.strip():
                    continue
                docs.append({
                    "chunk_id": item.get("chunk_id") or f"{item.get('source_file','unknown')}:{item.get('page_number','?')}:{len(docs)}",
                    "source_file": item.get("source_file", "unknown"),
                    "page_number": item.get("page_number", "Not specified"),
                    "title": item.get("title") or metadata.get("title") or item.get("source_file", "Research source"),
                    "text": text,
                    "source_url": item.get("source_url") or metadata.get("source_url"),
                    "source_url_status": item.get("source_url_status") or metadata.get("source_url_status", "not_provided"),
                    "metadata": metadata,
                })
        return docs

    def _build_tfidf(self) -> None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            self._cosine_similarity = cosine_similarity
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=60000, sublinear_tf=True, strip_accents="unicode", token_pattern=r"(?u)\b\w\w+\b")
            self.tfidf_matrix = self.vectorizer.fit_transform([d["text"] for d in self.docs])
            self.tfidf_state = "available"
        except Exception as exc:
            self.tfidf_state = "unavailable"
            self.tfidf_error = type(exc).__name__

    def _load_embeddings(self, model_name: str, cache_dir: Optional[Path]) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            kwargs = {"cache_folder": str(cache_dir)} if cache_dir else {}
            self.embedding_model = SentenceTransformer(model_name, **kwargs)
            # Pre-compute passage embeddings exactly once at startup. Never re-encode
            # the full corpus on each API request.
            passages = ["passage: " + d["text"] for d in self.docs]
            self.doc_embeddings = self.embedding_model.encode(
                passages, normalize_embeddings=True, show_progress_bar=False,
                batch_size=32
            )
            self.embedding_state = "available"
        except Exception as exc:
            self.embedding_state = "unavailable"
            self.embedding_error = f"{type(exc).__name__}: model may need download"

    @staticmethod
    def rewrite_query(query: str) -> str:
        expanded = query.strip()
        lower = expanded.casefold()
        additions: List[str] = []
        for key, variants in ALIASES.items():
            if key in lower or any(alias in lower for alias in variants[:2]):
                additions.extend(variants)
        for ar, en in ARABIC_EXPANSIONS.items():
            if ar in expanded:
                additions.append(en)
        if re.search(r"\b(partial|lunar gravity|martian gravity)\b", lower) or "جاذبية جزئية" in expanded:
            additions.extend(["partial gravity data", "microgravity normal gravity limits", "E-FIELD electric field analogue"])
        return expanded + " " + " ".join(dict.fromkeys(additions))

    @staticmethod
    def _norm(values: List[float]) -> List[float]:
        if not values:
            return values
        mx = max(values)
        if mx <= 0:
            return [0.0] * len(values)
        return [x / mx for x in values]

    def _metadata_matches(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        md = doc.get("metadata", {})
        hay = " ".join([
            doc.get("title", ""), doc.get("source_file", ""), doc.get("text", ""),
            " ".join(str(x) for x in md.get("program", [])),
            " ".join(str(x) for x in md.get("topics", [])),
            " ".join(str(x) for x in md.get("materials_or_fuels", [])),
            " ".join(str(x) for x in md.get("hardware", [])),
        ]).casefold()
        investigation = filters.get("investigation")
        if investigation and str(investigation).casefold() not in hay:
            aliases = ALIASES.get(str(investigation).casefold(), [])
            if not any(a.casefold() in hay for a in aliases):
                return False
        fuel_type = filters.get("fuel_type")
        if fuel_type and str(fuel_type).casefold() not in hay:
            return False
        hardware = filters.get("hardware")
        if hardware and str(hardware).casefold() not in hay:
            return False
        oxygen_min = filters.get("oxygen_min")
        oxygen_max = filters.get("oxygen_max")
        if oxygen_min is not None or oxygen_max is not None:
            oxygen_terms = re.findall(r"(?i)(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:o2|oxygen)?", doc.get("text", ""))
            oxygen_values = [float(x) for x in oxygen_terms]
            if not oxygen_values:
                return False
            if oxygen_min is not None and max(oxygen_values) < float(oxygen_min):
                return False
            if oxygen_max is not None and min(oxygen_values) > float(oxygen_max):
                return False
        return True

    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None, strategy: str = "hybrid") -> List[Dict[str, Any]]:
        filters = filters or {}
        rewritten = self.rewrite_query(query)
        bm25_scores = self.bm25.scores(rewritten)
        bm25_norm = self._norm(bm25_scores)
        tfidf_scores = [0.0] * len(self.docs)
        if self.vectorizer is not None and self.tfidf_matrix is not None:
            qvec = self.vectorizer.transform([rewritten])
            tfidf_scores = self._norm(self._cosine_similarity(qvec, self.tfidf_matrix)[0].tolist())
        dense_scores = [0.0] * len(self.docs)
        if self.embedding_model is not None:
            try:
                qemb = self.embedding_model.encode("query: " + rewritten, normalize_embeddings=True)
                dense_scores = self._norm((self.doc_embeddings @ qemb).tolist())
            except Exception:
                dense_scores = [0.0] * len(self.docs)
        qtokens = set(BM25Index.tokenize(rewritten))
        ranked = []
        for idx, doc in enumerate(self.docs):
            if not self._metadata_matches(doc, filters):
                continue
            title_tokens = set(BM25Index.tokenize(doc["title"]))
            title_bonus = min(1.0, len(qtokens & title_tokens) / max(1, len(qtokens)))
            # Baseline vs hybrid are intentionally exposed for reproducible evaluation.
            if strategy == "bm25":
                score = bm25_norm[idx]
            else:
                weights = (0.5, 0.35, 0.15) if self.embedding_state == "available" else (0.55, 0.45, 0.0)
                score = weights[0] * bm25_norm[idx] + weights[1] * tfidf_scores[idx] + weights[2] * dense_scores[idx]
                score = score * 0.85 + title_bonus * 0.15
            if score > 0:
                ranked.append((score, idx, title_bonus))
        ranked.sort(key=lambda x: x[0], reverse=True)
        # Diversity reranker: cap repeated pages/sources, preserving the best evidence per paper.
        selected: List[Dict[str, Any]] = []
        per_source = defaultdict(int)
        for score, idx, title_bonus in ranked:
            doc = self.docs[idx]
            src = doc["source_file"]
            if per_source[src] >= 2:
                continue
            md = doc.get("metadata", {})
            selected.append({
                "chunk_id": doc["chunk_id"], "source_file": src, "page_number": doc["page_number"],
                "title": doc["title"], "text": doc["text"], "source_url": doc.get("source_url"),
                "source_url_status": doc.get("source_url_status"), "score": round(float(score), 5),
                "evidence_type": md.get("evidence_type", "not specified"),
                "program": md.get("program", []), "materials_or_fuels": md.get("materials_or_fuels", []),
                "platform": md.get("platform", "not specified"),
            })
            per_source[src] += 1
            if len(selected) >= max(1, min(int(top_k), 20)):
                break
        return selected

    def stats(self) -> Dict[str, Any]:
        return {
            "loaded": True, "chunks": len(self.docs), "documents": len({d['source_file'] for d in self.docs}),
            "bm25": "available", "tfidf": getattr(self, "tfidf_state", "unknown"),
            "dense_embeddings": self.embedding_state,
            "embedding_model": "configured" if self.embedding_state == "available" else None,
            "embedding_error": self.embedding_error,
        }
