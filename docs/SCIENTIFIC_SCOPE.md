# Scientific scope and guardrails

## Intended use

This is a research discovery and evidence organization prototype for microgravity combustion investigations relevant to crew-habitat fire safety. It is not a spacecraft safety certification tool, operational alarm, validated flammability model, or substitute for engineering review.

## Explicit restrictions

- The supplied challenge brief states that direct partial-gravity combustion data are not available in NASA PSI at this time. The system therefore states that such results are **not found in the supplied data**. It never describes E-FIELD as an actual lunar/Martian gravity experiment: electric-field effects are an analogue only.
- Microgravity and normal-gravity observations can be used as comparison bounds when clearly labeled, but they do not establish measured intermediate-gravity behavior.
- Rocket and propellant fire safety is outside the project scope. Chat requests about rockets/propellants receive a scope refusal rather than a RAG answer.
- The challenge-provided Moon habitat values (at least 30% oxygen at at most 10.2 psi), spacesuit values (100% oxygen at 4.3 psi), and Earth reference (14.7 psi / about 21% oxygen) are **scenario context**, not experimental PSI measurements and not final design specifications. Do not attribute them to an investigation.
- CFI-G oxygen concentrations refer to a burner oxidizer stream when supported by the cited source, not a crew cabin atmosphere. The backend does not insert the 85% figure unless it is in retrieved source material.
- Relevance rankings are text/evidence relevance, not a probability of ignition, fire severity, flammability rating, safety certification, or NASA ranking.
- A named investigation's catalogue summary can be broader than the local PDF corpus. Every numeric condition should be verified against the linked PSI record or publication.

## Dataset boundaries

The rebuilt runtime corpus contains 615 chunks across 28 source files (27 PDF research sources plus one investigation metadata text source). It was derived from teammate-provided processed JSONL. This is a partial curated corpus, not a complete mirror of NASA PSI or a complete run-level experiment database. All 28 source documents currently have a verified document-level URL in `source_manifest.json`; exact DOI matches were checked against title/abstract/author evidence, and NASA record URLs are used only where the relationship is explicit.

The original Chroma index is preserved in `source_data/`, but the exact `intfloat/multilingual-e5-base` model weights and a compatible Chroma runtime were not supplied as a complete runnable environment. Default retrieval therefore uses BM25 + TF-IDF + title boost + source diversity. Dense embeddings are optional after downloading the configured model.

## NLP and CV limitations

- SciBERT inference code was supplied, but the matching fine-tuned checkpoint directory and weights were not. The default entity extractor is a deterministic regex/lexicon fallback. It preserves raw values and units; it does not establish that a value is an experimental run condition.
- Supplied NER evaluation: 44 training sentences, 5 validation sentences, 6 test sentences; 19 labels; test precision 0.5263, recall 0.5882, F1 0.5556. The 6-sentence test set is too small for a production accuracy claim.
- Image processing uses OpenCV HSV segmentation and shape/color heuristics. No labeled NASA image dataset was supplied; no classifier was trained and no CV accuracy is reported.
- Video processing reuses the supplied `combustion_behavior_analysis` pipeline. Pixel geometry is not physical geometry without camera calibration. Optical flow is apparent image motion, not gas-flow velocity. Visual disappearance is not proof of flame extinction.
- Three official NASA SVS image references are included as metadata links. Their binary files were not included/downloaded in this build; the metadata marks `downloaded: false`. The page identifies these assets as SoFIE imagery, not Saffire imagery.

## Data provenance policy

A DOI is used when found in the source's own document metadata/text. An official NASA PSI record or NASA overview is used only when a document-specific DOI is absent and the relationship is sufficiently clear. Unknown links stay unset. All source URLs are in `backend/data/source_manifest.json` and the media URL/title/credit metadata is in `backend/data/media/metadata.json`.
