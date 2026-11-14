from __future__ import annotations

import tempfile
import re
from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np

from app.core.config import settings


class VisionService:
    def __init__(self):
        settings.vision_output_dir.mkdir(parents=True, exist_ok=True)
        self.cv_available = True

    def analyze_image(self, image_bytes: bytes, filename: str = "upload.png") -> Dict[str, Any]:
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("The uploaded file is not a readable image.")
        h, w = image.shape[:2]
        if h * w > 40_000_000:
            raise ValueError("Image dimensions exceed the configured 40-megapixel safety limit.")
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Broad, documented heuristic ranges only; inspect the returned overlay before use.
        warm = cv2.inRange(hsv, np.array([0, 45, 50]), np.array([38, 255, 255]))
        blue = cv2.inRange(hsv, np.array([85, 35, 35]), np.array([145, 255, 255]))
        kernel = np.ones((3, 3), np.uint8)
        warm = cv2.morphologyEx(warm, cv2.MORPH_OPEN, kernel)
        warm = cv2.morphologyEx(warm, cv2.MORPH_CLOSE, kernel)
        blue = cv2.morphologyEx(blue, cv2.MORPH_OPEN, kernel)
        warm_px, blue_px = int(cv2.countNonZero(warm)), int(cv2.countNonZero(blue))
        contours, _ = cv2.findContours(cv2.bitwise_or(warm, blue), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        contour = contours[0] if contours else None
        area = float(cv2.contourArea(contour)) if contour is not None else 0.0
        perimeter = float(cv2.arcLength(contour, True)) if contour is not None else 0.0
        if contour is not None:
            x, y, cw, ch = cv2.boundingRect(contour)
            aspect = float(cw / max(1, ch))
            circularity = float(4 * np.pi * area / max(1e-8, perimeter * perimeter))
            solidity = float(area / max(1e-8, cv2.contourArea(cv2.convexHull(contour))))
        else:
            x = y = cw = ch = 0
            aspect = circularity = solidity = 0.0
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        dominant = "blue_tone_candidate" if blue_px > warm_px else "yellow_or_orange_tone_candidate" if warm_px > 0 else "no_candidate_detected"
        shape = "sphere_like_candidate" if circularity >= 0.68 and 0.75 <= aspect <= 1.33 else "elongated_candidate" if aspect >= 1.4 else "irregular_or_not_detected"
        combined = "blue_sphere_like_candidate" if dominant == "blue_tone_candidate" and shape == "sphere_like_candidate" else "yellow_teardrop_like_candidate" if dominant.startswith("yellow") and shape == "elongated_candidate" else "unclassified_visual_candidate"
        overlay = image.copy()
        if contour is not None:
            cv2.drawContours(overlay, [contour], -1, (0, 255, 0), 2)
        ok, encoded = cv2.imencode(".jpg", overlay, [int(cv2.IMWRITE_JPEG_QUALITY), 78])
        return {
            "filename": filename, "width_px": w, "height_px": h,
            "segmentation": "HSV warm/blue heuristic", "flame_pixel_area": int(warm_px + blue_px),
            "flame_area_fraction": round((warm_px + blue_px) / max(1, w * h), 6),
            "warm_pixel_area": warm_px, "blue_pixel_area": blue_px,
            "largest_contour_area_px": round(area, 2), "bounding_box_px": {"x": int(x), "y": int(y), "width": int(cw), "height": int(ch)},
            "aspect_ratio": round(aspect, 4), "circularity": round(circularity, 4), "solidity": round(solidity, 4),
            "mean_luminance": round(float(gray.mean()), 3), "dominant_color_candidate": dominant,
            "shape_candidate": shape, "combined_candidate": combined,
            "overlay_jpeg_base64": __import__("base64").b64encode(encoded.tobytes()).decode("ascii") if ok else None,
            "model": None,
            "limitations": ["Heuristic segmentation only; no trained classifier or labeled evaluation set was supplied.", "Pixel dimensions are not physical lengths without camera calibration.", "Visual candidates do not prove ignition, extinction, material flammability, or fire risk.", "Blue-sphere/yellow-teardrop labels are appearance heuristics, not validated flame-state classes."],
        }

    def analyze_video(self, video_bytes: bytes, filename: str, experiment_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Reuse the supplied combustion_behavior_analysis pipeline, rather than replacing its logic.
        src_root = settings.project_root / "source_data" / "combustion_behavior_analysis" / "src"
        import sys
        if str(src_root) not in sys.path:
            sys.path.insert(0, str(src_root))
        from combustion_analysis.pipeline import run_analysis
        suffix = Path(filename).suffix or ".mp4"
        with tempfile.TemporaryDirectory(prefix="beyond_flame_") as temp_dir:
            input_path = Path(temp_dir) / (Path(filename).name or f"upload{suffix}")
            input_path.write_bytes(video_bytes)
            metadata_path = None
            if metadata:
                metadata_path = Path(temp_dir) / "metadata.json"
                import json
                metadata_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
            safe_experiment_id = re.sub(r"[^A-Za-z0-9_.-]", "_", experiment_id or input_path.stem)[:80]
            output_dir = settings.vision_output_dir / (safe_experiment_id or input_path.stem)
            result = run_analysis(
                input_path, output_dir,
                config_path=settings.project_root / "source_data" / "combustion_behavior_analysis" / "configs" / "default.yaml",
                experiment_id=experiment_id, metadata_path=metadata_path,
            )
            return {"analysis": result, "limitations": result.get("run_metadata", {}).get("warnings", [])}

    def health(self):
        return {"available": self.cv_available, "engine": "OpenCV", "trained_classifier": False, "pipeline_reused": True}
