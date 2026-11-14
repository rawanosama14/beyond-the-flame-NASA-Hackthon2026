# Optional extras

No separate UI page was added because the supplied frontend is a strict read-only asset and has no image-analysis UI contract. Image and video analysis is available through `POST /api/vision/analyze`; see FastAPI `/docs` and the root README. A future standalone upload page can be built in this `extras/` folder without modifying `frontend/`.
