from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings

PATTERNS = {
    "OXYGEN": re.compile(
        r"(?i)(?:oxygen(?:\s+concentration)?|o\s*2|أكسجين|اكسجين)\s*(?:concentration\s*)?(?:was|is|of|at|=|:)?\s*(\d+(?:\.\d+)?)\s*(%|percent|per cent)?|(?<!\w)(\d+(?:\.\d+)?)\s*(%|percent)\s*(?:oxygen|o\s*2)"
    ),
    "PRESSURE": re.compile(r"(?i)(\d+(?:\.\d+)?)\s*(psi(?:a)?|kpa|bar|atm)\b"),
    "FLOW": re.compile(r"(?i)(\d+(?:\.\d+)?)\s*(cm/s|mm/s|m/s|cm s-1|m s-1)\b"),
    "TEMPERATURE": re.compile(r"(?i)(\d+(?:\.\d+)?)\s*(k|°c|celsius|°f|fahrenheit)\b"),
}
FUEL_TERMS = [
    "PMMA", "cotton-fiberglass", "cotton", "fiberglass", "methanol", "heptane",
    "n-heptane", "nonane", "ethylene", "iso-octane", "Pyrell", "wax",
    "solid fuel", "liquid droplet", "polyethylene", "acrylic",
]
INVESTIGATIONS = [
    "BASS-II", "BASS", "Saffire-III", "Saffire-II", "Saffire-I", "SAME-R", "SAME",
    "DAFT-2", "DAFT", "FLEX-2", "FLEX", "CFI-G", "CFI", "ACME", "SPICE", "SLICE",
    "E-FIELD Flames", "BRE",
]
WORD_PATTERN = re.compile(r"\w+(?:[-’'][\w]+)*|[^\w\s]", re.UNICODE)


def _unique(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for item in sorted(items, key=lambda x: (x.get("start", 0), x.get("end", 0))):
        key = (item.get("entity"), item.get("text", "").casefold(), item.get("start"))
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out



NUMERIC_WITH_UNIT = re.compile(
    r"(?i)(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>%|percent|per cent|psia?|kpa|bar|atm|cm/s|mm/s|m/s|cm\s*s-1|m\s*s-1|°c|celsius|°f|fahrenheit|kelvin|k|mm|cm|meters?|metres?|seconds?|secs?|minutes?|mins?|hours?|hrs?)(?=\s|[.,;:)]|$)"
)


def extract_numeric_parameters(text: str) -> List[Dict[str, Any]]:
    """Return raw quantitative mentions with nearby context; no unit conversion is guessed."""
    out = []
    for match in NUMERIC_WITH_UNIT.finditer(text or ""):
        unit = match.group("unit")
        norm = unit.casefold().replace(" ", "")
        if norm in {"psi", "psia", "kpa", "bar", "atm"}:
            category = "pressure"
        elif norm in {"cm/s", "mm/s", "m/s", "cms-1", "ms-1"}:
            category = "velocity_or_airflow"
        elif norm in {"k", "kelvin", "°c", "celsius", "°f", "fahrenheit"}:
            category = "temperature"
        elif norm in {"mm", "cm", "m", "meter", "meters", "metre", "metres"}:
            category = "length_or_dimension"
        elif norm in {"s", "sec", "secs", "second", "seconds", "min", "mins", "minute", "minutes", "h", "hr", "hrs", "hour", "hours"}:
            category = "time"
        elif norm in {"%", "percent", "percent"}:
            context_before = (text or "")[max(0, match.start() - 90):match.start()].casefold()
            category = "oxygen_concentration" if any(x in context_before for x in ["oxygen", "o2", "oxidizer", "أكسجين", "اكسجين"]) else "percentage_unspecified"
        else:
            category = "not_resolved"
        out.append({
            "value": float(match.group("value")), "unit": unit,
            "parameter_class": category,
            "raw": match.group(0), "context": (text or "")[max(0, match.start() - 90):min(len(text or ""), match.end() + 90)].strip(),
            "start": match.start(), "end": match.end(),
        })
    return out

class NERService:
    """Neural SciBERT when a fine-tuned checkpoint is supplied; otherwise explicit rules.

    The uploaded inference utility is reused for token-level BIO decoding. It is never
    represented as trained/available unless a compatible local checkpoint loads.
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.torch = None
        self.mode = "regex_lexicon_fallback"
        self.error: Optional[str] = None
        self.model_path: Optional[str] = None
        if settings.ner_model_dir:
            self._try_load_neural(Path(settings.ner_model_dir))

    def _try_load_neural(self, path: Path) -> None:
        try:
            if not path.exists():
                raise FileNotFoundError("configured NER model path does not exist")
            import torch
            from transformers import AutoModelForTokenClassification, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(str(path), use_fast=True)
            if not tokenizer.is_fast:
                raise RuntimeError("SciBERT NER requires a fast tokenizer with word_ids()")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = AutoModelForTokenClassification.from_pretrained(str(path))
            model.to(device).eval()
            self.tokenizer, self.model, self.torch = tokenizer, model, torch
            self.model_path = str(path)
            self.mode = "scibert_ner_plus_domain_rules"
        except Exception as exc:
            self.error = type(exc).__name__
            self.mode = "regex_lexicon_fallback"

    def _neural_entities(self, text: str) -> List[Dict[str, Any]]:
        if self.model is None or self.tokenizer is None or self.torch is None:
            return []
        try:
            matches = list(WORD_PATTERN.finditer(text))
            words = [m.group(0) for m in matches]
            if not words:
                return []
            encoded = self.tokenizer(
                words, is_split_into_words=True, truncation=True,
                max_length=256, return_tensors="pt"
            )
            word_ids = encoded.word_ids(batch_index=0)
            device = next(self.model.parameters()).device
            model_inputs = {k: v.to(device) for k, v in encoded.items()}
            with self.torch.no_grad():
                logits = self.model(**model_inputs).logits
                probs = self.torch.softmax(logits, dim=-1)
                ids = probs.argmax(dim=-1)[0]
                confidence = probs.max(dim=-1).values[0]
            id2label = self.model.config.id2label
            tags, scores = [], []
            previous = None
            for token_i, word_i in enumerate(word_ids):
                if word_i is None or word_i == previous:
                    previous = word_i
                    continue
                tags.append(str(id2label[int(ids[token_i].item())]))
                scores.append(float(confidence[token_i].item()))
                previous = word_i
            used_matches = matches[:len(tags)]
            out = []
            current_type = None
            start_word = None
            current_scores: List[float] = []

            def flush(end_word: int):
                nonlocal current_type, start_word, current_scores
                if current_type is not None and start_word is not None and end_word > start_word:
                    start_char = used_matches[start_word].start()
                    end_char = used_matches[end_word - 1].end()
                    out.append({
                        "text": text[start_char:end_char], "entity": current_type,
                        "start": start_char, "end": end_char,
                        "confidence": round(sum(current_scores) / max(1, len(current_scores)), 4),
                        "method": "scibert",
                    })
                current_type, start_word, current_scores = None, None, []

            for i, (word, tag, score) in enumerate(zip(words[:len(tags)], tags, scores)):
                if tag == "O" or "-" not in tag:
                    flush(i)
                    continue
                prefix, entity_type = tag.split("-", 1)
                if prefix == "B" or current_type != entity_type:
                    flush(i)
                    current_type, start_word, current_scores = entity_type, i, [score]
                else:
                    current_scores.append(score)
            flush(len(tags))
            return out
        except Exception as exc:
            self.error = f"inference:{type(exc).__name__}"
            return []

    def _rule_entities(self, text: str) -> List[Dict[str, Any]]:
        entities: List[Dict[str, Any]] = []
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                entities.append({
                    "text": match.group(0).strip(), "entity": label,
                    "start": match.start(), "end": match.end(),
                    "confidence": None, "method": "regex",
                })
        for term in FUEL_TERMS:
            for match in re.finditer(re.escape(term), text, flags=re.IGNORECASE):
                entities.append({
                    "text": match.group(0), "entity": "FUEL", "start": match.start(),
                    "end": match.end(), "confidence": None, "method": "lexicon",
                })
        for term in INVESTIGATIONS:
            for match in re.finditer(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, flags=re.IGNORECASE):
                entities.append({
                    "text": match.group(0), "entity": "INVESTIGATION", "start": match.start(),
                    "end": match.end(), "confidence": None, "method": "lexicon",
                })
        return entities

    def extract(self, text: str) -> Dict[str, Any]:
        if not isinstance(text, str) or not text.strip():
            return {"entities": [], "method": self.mode, "warning": "Input text is empty."}
        neural = self._neural_entities(text)
        entities = _unique(neural + self._rule_entities(text))
        warning = None
        if self.model is None:
            warning = "Rule-based fallback; fine-tuned SciBERT weights were not supplied."
        elif self.error and self.error.startswith("inference:"):
            warning = "SciBERT inference failed; domain-rule extraction was used for this request."
        return {
            "entities": entities, "method": self.mode, "warning": warning,
            "model_path": self.model_path,
        }

    def health(self) -> Dict[str, Any]:
        return {
            "available": True, "mode": self.mode,
            "neural_weights_present": self.model is not None,
            "model_error": self.error,
            "note": "Rule/lexicon entities are deterministic mentions, not validated measurements or a trained classifier."
            if self.model is None else "Fine-tuned SciBERT loaded; neural output is combined with domain extraction rules.",
        }
