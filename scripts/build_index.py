#!/usr/bin/env python3
"""Build the local retriever corpus from the supplied, curated PSI research chunks."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAG = ROOT / "source_data" / "nasa_rag"
OUT = ROOT / "backend" / "data"
PSI_URLS = {
    "SAFFIRE-I": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-98",
    "SAFFIRE-II": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-99",
    "SAFFIRE-III": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-100",
    "FLEX": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69",
    "SAME-R": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-101",
    "SPICE": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-107",
}
OVERVIEW = "https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/"
# Verified document-level identifiers for files whose PDF text extraction did not
# retain a DOI. These mappings were checked against the exact document title/file.
KNOWN_DOIS = {
    "1-s2.0-S0010218021000821-am.pdf": "10.1016/j.combustflame.2021.02.019",
    "1-s2.0-S0360128518301539-am.pdf": "10.1016/j.pecs.2019.100787",
    "1-s2.0-S1540748918301573-am.pdf": "10.1016/j.proci.2018.05.151",
    "1-s2.0-S1540748922000670-am.pdf": "10.1016/j.proci.2022.07.043",
    "1-s2.0-S1540748922001134-am.pdf": "10.1016/j.proci.2022.07.094",
    "1-s2.0-S1540748924002086-am.pdf": "10.1016/j.proci.2024.105400",
    "20140006750.pdf": "10.1016/j.combustflame.2015.01.012",
    "thermal_regime_flame_spread_clean.pdf": "10.1016/j.firesaf.2015.11.011",
    "thermal_regime_flame_spread_pmma_clean.pdf": "10.1016/j.firesaf.2015.11.011",
    "fire_detection_air_quality_sensors_spacecraft_clean.pdf": "10.1016/j.firesaf.2020.102977",
    "flame_spread_paper_clean.pdf": "10.1016/j.combustflame.2015.10.023",
    "opposed_flow_flame_spread_pmma_clean.pdf": "10.1016/j.proci.2014.07.017",
    "sibal_concurrent_flame_spread_clean.pdf": "10.1016/j.proci.2016.06.028",
}
KNOWN_SOURCE_URLS = {
    "20070017909.pdf": "https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20070017909.pdf",
}

def clean_doi(text: str):
    m = re.search(r"10\.\d{4,9}/[^\s,;<>]+", text or "", re.I)
    if not m: return None
    doi = m.group(0).rstrip(".,;:)]}")
    return doi.replace("ﬂ", "fl").replace("ﬁ", "fi")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    metadata = {}
    meta_path = RAG / "data/processed/document_metadata.jsonl"
    if meta_path.exists():
        for line in meta_path.open(encoding="utf-8"):
            if line.strip():
                m = json.loads(line); metadata[m.get("source_file", "")] = m
    catalog = {}
    cat_path = RAG / "data/processed/document_catalog.jsonl"
    if cat_path.exists():
        for line in cat_path.open(encoding="utf-8"):
            if line.strip():
                c = json.loads(line); catalog[c.get("source_file", "")] = c
    chunks_path = RAG / "data/processed/retrieval_chunks.jsonl"
    out_path = OUT / "corpus.jsonl"
    docs = {}
    count = 0
    with chunks_path.open(encoding="utf-8") as src, out_path.open("w", encoding="utf-8") as dst:
        for line in src:
            r = json.loads(line)
            source = r.get("source_file", "unknown")
            md = metadata.get(source, r.get("document_metadata", {}))
            first = catalog.get(source, {}).get("first_pages_text", "")
            doi = clean_doi(first) or KNOWN_DOIS.get(source)
            # Prefer a DOI or a verified document-specific NASA NTRS URL. Only fall
            # back to a PSI record when the source identifies one experiment.
            if doi:
                url, status = f"https://doi.org/{doi}", "doi"
            elif source in KNOWN_SOURCE_URLS:
                url, status = KNOWN_SOURCE_URLS[source], "nasa_ntrs_document"
            else:
                url, status = None, "no_document_specific_url_in_upload"
            program_items = [str(x).upper().replace(" ", "-") for x in md.get("program", [])]
            title_text = str(md.get("title", "")).upper().replace(" ", "-")
            identity_text = " ".join(program_items + [title_text])
            if not doi:
                specific_saffire = [name for name in ["SAFFIRE-I", "SAFFIRE-II", "SAFFIRE-III"] if name in identity_text]
                if len(specific_saffire) == 1:
                    url, status = PSI_URLS[specific_saffire[0]], "nasa_psi_record"
                elif "SAME-R" in identity_text:
                    url, status = PSI_URLS["SAME-R"], "nasa_psi_record"
                elif "SPICE" in identity_text:
                    url, status = PSI_URLS["SPICE"], "nasa_psi_record"
                elif "FLEX" in identity_text:
                    url, status = PSI_URLS["FLEX"], "nasa_psi_record"
                elif "SAFFIRE" in identity_text:
                    url, status = "https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/", "nasa_investigation_catalog"
            rec = {
                "chunk_id": r.get("chunk_id"), "source_file": source,
                "page_number": r.get("page_number"), "title": md.get("title") or source,
                "text": r.get("chunk_text", ""), "source_url": url,
                "source_url_status": status,
                "metadata": {k: md.get(k) for k in ["document_type", "evidence_type", "platform", "program", "gravity_conditions", "materials_or_fuels", "topics", "methods", "metadata_status"] if k in md},
            }
            dst.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
            if source not in docs:
                docs[source] = {k: rec[k] for k in ["source_file", "title", "source_url", "source_url_status", "metadata"]}
                docs[source]["doi"] = doi
    # Include PSI-60 investigation metadata, which exists in the upload but was not part of the 614-page chunks.
    p = RAG / "data/processed/metadata_documents.jsonl"
    if p.exists():
        for line in p.open(encoding="utf-8"):
            if not line.strip(): continue
            m = json.loads(line)
            text = "\n".join([str(m.get("study_title", "")), str(m.get("objective", "")), str(m.get("approach", "")), str(m.get("hypothesis", "")), str(m.get("text", ""))])
            source = m.get("source_file", "i_Investigation.txt")
            url = "https://psi.nasa.gov/physci/repo/data/investigations/PSI-60"
            rec = {"chunk_id": "PSI-60-metadata-1", "source_file": source, "page_number": "metadata", "title": m.get("study_title", "PSI-60 metadata"), "text": text, "source_url": url, "source_url_status": "nasa_psi_record", "metadata": {"document_type": "PSI investigation metadata", "evidence_type": "metadata_description", "platform": "Ground Investigation", "program": [m.get("experiment", "SPICE")], "topics": m.get("study_design", []), "metadata_status": "curated_source_record"}}
            with out_path.open("a", encoding="utf-8") as dst: dst.write(json.dumps(rec, ensure_ascii=False) + "\n")
            docs[source] = {k: rec[k] for k in ["source_file", "title", "source_url", "source_url_status", "metadata"]}
            docs[source]["doi"] = m.get("dataset_doi")
            count += 1
    (OUT / "documents.json").write_text(json.dumps(list(docs.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {"chunk_count": count, "document_count": len(docs), "sources": list(docs.values()), "source_policy": "DOI or exact NASA PSI record URLs are used where verified; missing URLs are explicitly marked rather than fabricated."}
    (OUT / "source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {count} chunks across {len(docs)} documents: {out_path}")

if __name__ == "__main__": main()
