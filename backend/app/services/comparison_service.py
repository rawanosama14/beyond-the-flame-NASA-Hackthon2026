from __future__ import annotations

import re
from typing import Any, Dict, List

from app.services.ner_service import NERService

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+|(?<=[؛])\s*")
OBJECTIVE_CUES = re.compile(
    r"(?i)\b(objective|objectives|aim|aims|aimed|purpose|designed to|was designed|were designed|investigat(?:e|ed|es|ing)|examines?|examined|study|studied|characteri[sz](?:e|ed|ing))\b"
)
HARDWARE_TERMS = [
    "Combustion Integrated Rack", "CIR", "Microgravity Science Glovebox", "MSG",
    "Multi-user Droplet Combustion Apparatus", "MDCA", "P-Trak", "Pyrell",
    "flow duct", "fan-driven duct", "spherical burner", "burner", "glovebox",
    "combustion chamber", "test chamber",
]
SENSOR_TERMS = [
    "camera", "video camera", "high-speed camera", "CCD", "photodiode",
    "photomultiplier", "thermocouple", "pyrometer", "radiometer", "spectrometer",
    "particle counter", "P-Trak", "aerosol instrument", "smoke detector",
    "gas analyzer", "gas analyser", "pressure transducer", "flow meter",
    "infrared camera", "IR camera",
]
VARIABLE_TERMS = [
    "flame spread", "burning rate", "flame growth", "flame extinction", "extinction limit",
    "ignition", "flame temperature", "flame height", "heat release", "radiative heat flux",
    "droplet diameter", "droplet lifetime", "droplet burning rate", "smoke particle size",
    "particle size distribution", "aerosol concentration", "soot", "mass loss", "oxygen concentration",
    "oxygen mole fraction", "airflow velocity", "flow velocity", "velocity field", "fuel diameter",
    "sample thickness", "sample dimensions", "flame structure", "smoke point", "lift-off height",
]


def _sentences(text: str) -> List[str]:
    return [x.strip() for x in SENTENCE_SPLIT.split(re.sub(r"\s+", " ", text or "")) if x.strip()]


def _mentions(text: str, terms: List[str]) -> List[str]:
    lower = (text or "").casefold()
    found = []
    for term in terms:
        if re.search(r"(?<!\w)" + re.escape(term.casefold()) + r"(?!\w)", lower):
            found.append(term)
    return found


def _evidence(sentences: List[str], cue: re.Pattern, limit: int = 3) -> List[str]:
    values = []
    for sentence in sentences:
        if cue.search(sentence):
            snippet = sentence[:480]
            if snippet not in values:
                values.append(snippet)
        if len(values) >= limit:
            break
    return values


def compare_investigation(name: str, docs: List[Dict[str, Any]], ner: NERService) -> Dict[str, Any]:
    per_doc = []
    objective_evidence: List[Dict[str, str]] = []
    hardware_evidence: List[Dict[str, str]] = []
    sensor_evidence: List[Dict[str, str]] = []
    variable_evidence: List[Dict[str, str]] = []
    values: Dict[str, List[Dict[str, Any]]] = {k: [] for k in ["FUEL", "OXYGEN", "PRESSURE", "FLOW", "TEMPERATURE"]}

    for doc in docs:
        text = doc.get("text", "")
        sentences = _sentences(text)
        ner_result = ner.extract(text)
        for entity in ner_result.get("entities", []):
            label = entity.get("entity")
            if label in values:
                values[label].append({
                    "value": entity.get("text"),
                    "source_file": doc.get("source_file"),
                    "page": doc.get("page_number"),
                    "method": entity.get("method"),
                })

        for sentence in _evidence(sentences, OBJECTIVE_CUES, 2):
            objective_evidence.append({"excerpt": sentence, "source_file": doc.get("source_file"), "page": str(doc.get("page_number"))})
        for term in _mentions(text, HARDWARE_TERMS):
            match = next((s for s in sentences if term.casefold() in s.casefold()), text[:350])
            hardware_evidence.append({"term": term, "excerpt": match[:400], "source_file": doc.get("source_file"), "page": str(doc.get("page_number"))})
        for term in _mentions(text, SENSOR_TERMS):
            match = next((s for s in sentences if term.casefold() in s.casefold()), text[:350])
            sensor_evidence.append({"term": term, "excerpt": match[:400], "source_file": doc.get("source_file"), "page": str(doc.get("page_number"))})
        for term in _mentions(text, VARIABLE_TERMS):
            match = next((s for s in sentences if term.casefold() in s.casefold()), text[:350])
            variable_evidence.append({"term": term, "excerpt": match[:400], "source_file": doc.get("source_file"), "page": str(doc.get("page_number"))})
        per_doc.append({
            "title": doc.get("title"), "source_file": doc.get("source_file"),
            "page": doc.get("page_number"), "source_url": doc.get("source_url"),
            "score": doc.get("score"),
        })

    def unique_records(records: List[Dict[str, Any]], key_fields: tuple[str, ...], limit: int = 30):
        seen = set()
        result = []
        for record in records:
            key = tuple(str(record.get(k, "")).casefold() for k in key_fields)
            if key in seen:
                continue
            seen.add(key)
            result.append(record)
            if len(result) >= limit:
                break
        return result

    objective_evidence = unique_records(objective_evidence, ("excerpt", "source_file", "page"), 5)
    hardware_evidence = unique_records(hardware_evidence, ("term", "source_file"), 15)
    sensor_evidence = unique_records(sensor_evidence, ("term", "source_file"), 15)
    variable_evidence = unique_records(variable_evidence, ("term", "source_file"), 20)
    compact_values = {key.lower(): unique_records(items, ("value", "source_file", "page"), 30) for key, items in values.items()}

    return {
        "investigation": name,
        "objective": objective_evidence or "Not specified in retrieved source text",
        "fuels": compact_values["fuel"] or "Not specified in retrieved source text",
        "oxygen": compact_values["oxygen"] or "Not specified in retrieved source text",
        "pressure": compact_values["pressure"] or "Not specified in retrieved source text",
        "airflow": compact_values["flow"] or "Not specified in retrieved source text",
        "temperature": compact_values["temperature"] or "Not specified in retrieved source text",
        "measurements_and_variables": variable_evidence or "Not specified in retrieved source text",
        "sensors": sensor_evidence or "Not specified in retrieved source text",
        "hardware": hardware_evidence or "Not specified in retrieved source text",
        "evidence_type": sorted({str(d.get("evidence_type", "not specified")) for d in docs}) or ["not specified"],
        "sources": per_doc,
        "extraction_note": "Fields are extracted only from retrieved text and may mix related papers. Verify each value against its cited source before using it as an experimental condition.",
    }
