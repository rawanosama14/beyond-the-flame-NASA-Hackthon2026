#!/usr/bin/env python3
"""Evaluate retrieval against 40 source-grounded questions.

No semantic answer-faithfulness score is fabricated. The automated term-support score
only measures whether gold evidence terms are present in retrieved source passages.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.core.config import settings  # noqa: E402
from app.services.retrieval import ResearchRetriever  # noqa: E402

TOKEN = re.compile(r"[\w]+", re.UNICODE)


def tokens(value: str) -> set[str]:
    return {x.casefold() for x in TOKEN.findall(value or "") if len(x) > 1}


def _term_is_present(term: str, haystack: str) -> bool:
    normalized_term = re.sub(r"\s+", " ", term).casefold().strip()
    normalized_haystack = re.sub(r"\s+", " ", haystack).casefold()
    return bool(normalized_term and normalized_term in normalized_haystack)


def evaluate(strategy: str) -> dict:
    retriever = ResearchRetriever(settings.corpus_path, embedding_enabled=False)
    qa_path = ROOT / "eval" / "golden_qa.jsonl"
    qa = [json.loads(line) for line in qa_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    recall_at_5, top1, reciprocal_rank = [], [], []
    citation_precision_at_3, term_support_at_5 = [], []
    missed_sources, missing_terms = [], []

    for item in qa:
        results = retriever.retrieve(item["question"], top_k=5, strategy=strategy)
        sources = [row["source_file"] for row in results]
        expected_sources = set(item["expected_sources"])
        positions = [index + 1 for index, source in enumerate(sources) if source in expected_sources]

        recall_at_5.append(1.0 if positions else 0.0)
        top1.append(1.0 if sources and sources[0] in expected_sources else 0.0)
        reciprocal_rank.append(1.0 / min(positions) if positions else 0.0)
        cited = sources[:3]
        correct_citations = sum(1 for source in cited if source in expected_sources)
        citation_precision_at_3.append(correct_citations / max(1, len(cited)))

        evidence_text = "\n".join(row["text"] for row in results[:5])
        expected_terms = item.get("expected_terms", [])
        present = [term for term in expected_terms if _term_is_present(term, evidence_text)]
        term_support_at_5.append(len(present) / max(1, len(expected_terms)))
        if not positions:
            missed_sources.append(item["id"])
        if len(present) != len(expected_terms):
            missing_terms.append({"id": item["id"], "missing": [t for t in expected_terms if t not in present]})

    mean = lambda values: round(sum(values) / max(1, len(values)), 4)
    return {
        "strategy": strategy,
        "questions": len(qa),
        "retrieval_recall_at_5": mean(recall_at_5),
        "top1_expected_source_accuracy": mean(top1),
        "mean_reciprocal_rank": mean(reciprocal_rank),
        "expected_source_citation_precision_at_3": mean(citation_precision_at_3),
        "expected_term_evidence_coverage_at_5": mean(term_support_at_5),
        "missed_question_ids": missed_sources,
        "questions_with_missing_expected_terms": missing_terms,
    }


if __name__ == "__main__":
    before = evaluate("bm25")
    after = evaluate("hybrid")
    report = {
        "before": before,
        "after": after,
        "interpretation": (
            "Before = BM25-only baseline. After = BM25 + TF-IDF + title boost + source-diversity reranking. "
            "Dense E5 embeddings were unavailable because the checkpoint was not supplied/downloaded. "
            "Citation precision is strict precision against the question's expected-source labels; other relevant sources can be penalized. "
            "Expected-term evidence coverage is a retrieval support proxy, not semantic answer faithfulness. "
            "Human-reviewed answer faithfulness was not measured because no expert-annotated answer set was supplied."
        ),
    }
    out = ROOT / "eval" / "metrics.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
