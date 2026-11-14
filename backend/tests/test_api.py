from __future__ import annotations
import io
from pathlib import Path
import numpy as np
import cv2
from fastapi.testclient import TestClient
from app.main import app


def image_bytes():
    image = np.zeros((96, 128, 3), dtype=np.uint8)
    cv2.ellipse(image, (64, 48), (12, 25), 0, 0, 360, (0, 150, 255), -1)
    ok, data = cv2.imencode(".png", image)
    assert ok
    return data.tobytes()


def test_health_has_all_services():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["services"]["rag"]["loaded"] is True
        assert {"llm", "nlp", "vision"}.issubset(body["services"])


def test_frontend_chat_contract():
    with TestClient(app) as client:
        response = client.post("/api/chat", json={"message": "What does the Saffire study say about flame spread?", "scenario": "Space station"})
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body.get("answer"), str) and body["answer"].strip()
        assert isinstance(body.get("citations"), list)
        for citation in body["citations"]:
            assert isinstance(citation.get("title"), str)
            assert citation.get("url", "").startswith("https://")


def test_chat_handles_arabic_and_partial_gravity_guardrail():
    with TestClient(app) as client:
        response = client.post("/api/chat", json={"message": "هل توجد بيانات احتراق في الجاذبية الجزئية؟", "scenario": "Moon base"})
        assert response.status_code == 200
        assert "جاذبية" in response.json()["answer"]


def test_investigation_catalog_and_detail():
    with TestClient(app) as client:
        data = client.get("/api/investigations?q=FLEX").json()
        assert data["count"] >= 1
        assert any(x["name"] == "FLEX" for x in data["investigations"])
        detail = client.get("/api/investigations/FLEX")
        assert detail.status_code == 200


def test_compare_and_rank():
    with TestClient(app) as client:
        compare = client.post("/api/compare", json={"investigations": ["FLEX", "BASS"]})
        assert compare.status_code == 200
        assert len(compare.json()["comparisons"]) == 2
        first = compare.json()["comparisons"][0]
        assert "oxygen" in first and "hardware" in first and "sensors" in first
        assert first["sources"]
        ranked = client.post("/api/rank", json={"habitat_type": "Space station", "top_k": 5})
        assert ranked.status_code == 200
        assert ranked.json()["ranking_type"] == "retrieval_relevance_not_fire_risk"


def test_nlp_extraction():
    with TestClient(app) as client:
        resp = client.post("/api/modeling/extract", json={"text": "Oxygen was 21 percent at 14.7 psi. Airflow was 20 cm/s over PMMA."})
        assert resp.status_code == 200
        types = {x["entity"] for x in resp.json()["entities"]}
        assert "PRESSURE" in types and "FLOW" in types and "FUEL" in types
        assert any(x["parameter_class"] == "pressure" for x in resp.json()["numeric_parameters"])


def test_insights_and_media():
    with TestClient(app) as client:
        assert client.get("/api/insights").status_code == 200
        controls = client.post("/api/insights/controls", json={"topic": "smoke detection and suppression", "habitat_type": "Space station"})
        assert controls.status_code == 200
        assert "detection" in controls.json()["evidence_groups"]
        media = client.get("/api/media").json()
        assert media["count"] >= 1
        assert all(x.get("page_url", "").startswith("https://") for x in media["media"])


def test_vision_endpoint_image():
    with TestClient(app) as client:
        response = client.post("/api/vision/analyze", files={"file": ("test.png", image_bytes(), "image/png")})
        assert response.status_code == 200
        result = response.json()["result"]
        assert result["width_px"] == 128
        assert "limitations" in result


def test_video_analysis_reuses_supplied_pipeline():
    video_path = Path(__file__).resolve().parents[2] / "source_data" / "combustion_behavior_analysis" / "data" / "external" / "synthetic_flame_demo.mp4"
    video = video_path.read_bytes()
    with TestClient(app) as client:
        response = client.post(
            "/api/vision/analyze",
            files={"file": ("sample_synthetic.mp4", video, "video/mp4")},
            data={"experiment_id": "pytest_synthetic_video"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["media_type"] == "video"
        assert body["scientific_status"] == "prototype_visual_analysis_not_NASA_validated"
        assert body["result"]["analysis"]["frame_count"] > 0
