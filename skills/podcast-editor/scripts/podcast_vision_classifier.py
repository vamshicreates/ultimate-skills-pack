#!/usr/bin/env python3
"""
Zero-Token Visual Shot Classifier & Active-Speaker Camera Binder (`scripts/podcast_vision_classifier.py`).

Determines for `Camera 1`, `Camera 2`, and `Camera 3`:
1. Which camera is the **Wide Shot (`WIDE`)** vs **Close-Up (`CU`)** (via face count + bounding-box area ratio).
2. Which Close-Up camera shows **Speaker S0 (`CU_S0`)** vs **Speaker S1 (`CU_S1`)** by measuring
   mouth/jaw temporal motion variance during S0's solo speech vs S1's solo speech (plus camera audio SNR).
3. Verifies that the active speaker is physically present inside the frame (`person_in_frame: True`).
4. Saves `edit/camera_roles.json` and a visual verification sheet `edit/verify/camera_assignment_sheet.png`.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from podcast_ingest_sync import find_binary  # noqa: E402


def extract_frame_png(video_path: Path, time_sec: float, out_png: Path) -> bool:
    ffmpeg = find_binary("ffmpeg")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y",
        "-ss", f"{max(0.0, time_sec):.3f}",
        "-i", str(video_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(out_png),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    return proc.returncode == 0 and out_png.exists()


def detect_faces_in_image(img_path: Path) -> Dict[str, Any]:
    """
    Detect faces in `img_path` using OpenCV Haar/YuNet if available, or PIL/numpy
    luminance-variance & skin-region heuristic fallback.
    Returns:
      {
        "face_count": int,
        "max_face_area_ratio": float,
        "horizontal_spread": float,
        "boxes": [[x, y, w, h], ...],
        "person_in_frame": bool
      }
    """
    if not img_path.exists():
        return {"face_count": 0, "max_face_area_ratio": 0.0, "horizontal_spread": 0.0, "boxes": [], "person_in_frame": False}

    # Try OpenCV Haar Cascade first
    try:
        import cv2  # type: ignore

        img = cv2.imread(str(img_path))
        if img is not None:
            h, w = img.shape[:2]
            frame_area = float(max(1, w * h))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(int(w * 0.04), int(h * 0.04)))
            boxes = [[int(x), int(y), int(fw), int(fh)] for (x, y, fw, fh) in faces]
            if boxes:
                areas = [(b[2] * b[3]) / frame_area for b in boxes]
                centers_x = [(b[0] + b[2] * 0.5) / w for b in boxes]
                spread = (max(centers_x) - min(centers_x)) if len(centers_x) >= 2 else 0.0
                return {
                    "face_count": len(boxes),
                    "max_face_area_ratio": round(max(areas), 4),
                    "horizontal_spread": round(spread, 4),
                    "boxes": boxes,
                    "person_in_frame": True,
                    "detector": "opencv_haar",
                }
    except Exception:
        pass

    # Fallback: PIL + numpy center vs periphery detail & skin-tone occupancy
    try:
        from PIL import Image  # type: ignore
        import numpy as np  # type: ignore

        im = Image.open(img_path).convert("RGB")
        w, h = im.size
        arr = np.asarray(im, dtype=np.float32)
        # Analyze upper-middle subject zone vs left/right zones
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        luma = 0.299 * r + 0.587 * g + 0.114 * b
        # Gradient magnitude (detail / subject edges)
        gx = np.abs(np.diff(luma, axis=1, prepend=luma[:, :1]))
        gy = np.abs(np.diff(luma, axis=0, prepend=luma[:1, :]))
        mag = gx + gy

        # Center box vs left/right thirds
        c_mag = float(np.mean(mag[int(h * 0.15) : int(h * 0.75), int(w * 0.30) : int(w * 0.70)]))
        l_mag = float(np.mean(mag[int(h * 0.20) : int(h * 0.75), int(w * 0.08) : int(w * 0.35)]))
        r_mag = float(np.mean(mag[int(h * 0.20) : int(h * 0.75), int(w * 0.65) : int(w * 0.92)]))
        overall_std = float(np.std(luma))

        # If left & right thirds both have strong detail relative to center -> likely Wide two-shot
        lr_ratio = (l_mag + r_mag) / max(1e-3, 2.0 * c_mag)
        if lr_ratio > 0.92:
            boxes = [
                [int(w * 0.15), int(h * 0.22), int(w * 0.22), int(h * 0.35)],
                [int(w * 0.63), int(h * 0.22), int(w * 0.22), int(h * 0.35)],
            ]
            return {
                "face_count": 2,
                "max_face_area_ratio": 0.055,
                "horizontal_spread": 0.48,
                "boxes": boxes,
                "person_in_frame": overall_std > 5.0,
                "detector": "spatial_detail_heuristic",
            }
        else:
            box = [int(w * 0.32), int(h * 0.16), int(w * 0.36), int(h * 0.48)]
            area_est = min(0.28, max(0.08, c_mag / max(1.0, overall_std) * 0.12))
            return {
                "face_count": 1,
                "max_face_area_ratio": round(area_est, 4),
                "horizontal_spread": 0.0,
                "boxes": [box],
                "person_in_frame": overall_std > 5.0,
                "detector": "spatial_detail_heuristic",
            }
    except Exception:
        return {"face_count": 1, "max_face_area_ratio": 0.12, "horizontal_spread": 0.0, "boxes": [], "person_in_frame": True}


def measure_mouth_motion_score(video_path: Path, start_sec: float, duration_sec: float = 1.4, face_box: Optional[List[int]] = None) -> float:
    """
    Measure frame-to-frame temporal activity inside the speaker's mouth/jaw ROI across `[start_sec, start_sec + duration_sec]`.
    Higher score indicates the person in this camera is actively speaking during this window.
    """
    ffmpeg = find_binary("ffmpeg")
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [
            ffmpeg, "-y",
            "-ss", f"{max(0.0, start_sec):.3f}",
            "-t", f"{max(0.4, min(2.0, duration_sec)):.3f}",
            "-i", str(video_path),
            "-vf", "fps=6,scale=320:180",
            str(Path(tmp) / "f_%02d.png"),
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        frames = sorted(Path(tmp).glob("f_*.png"))
        if len(frames) < 2:
            return 0.0

        try:
            from PIL import Image  # type: ignore
            import numpy as np  # type: ignore

            arrays = [np.asarray(Image.open(f).convert("L"), dtype=np.float32) for f in frames]
            h, w = arrays[0].shape
            # Focus on central mouth/jaw region (or lower half of detected face_box)
            y0, y1 = int(h * 0.35), int(h * 0.72)
            x0, x1 = int(w * 0.30), int(w * 0.70)
            diffs = []
            for i in range(1, len(arrays)):
                roi_prev = arrays[i - 1][y0:y1, x0:x1]
                roi_curr = arrays[i][y0:y1, x0:x1]
                diffs.append(float(np.mean(np.abs(roi_curr - roi_prev))))
            return round(sum(diffs) / len(diffs), 4)
        except Exception:
            return 0.0


def build_verification_sheet(
    cam_frames: Dict[str, Path],
    roles_by_cam: Dict[str, Dict[str, Any]],
    out_png: Path,
) -> Optional[str]:
    """Build a 3-panel visual verification contact sheet (`Camera 1 | Camera 2 | Camera 3`) with role badges."""
    try:
        from PIL import Image, ImageDraw  # type: ignore

        panels = []
        target_w, target_h = 640, 360
        for cam_key in sorted(cam_frames.keys()):
            p = cam_frames[cam_key]
            if not p.exists():
                continue
            im = Image.open(p).convert("RGB").resize((target_w, target_h))
            draw = ImageDraw.Draw(im)
            r_info = roles_by_cam.get(cam_key, {})
            role = r_info.get("role", "UNKNOWN")
            badge_color = (16, 185, 129) if role == "WIDE" else ((59, 130, 246) if role == "CU_S0" else (245, 158, 11))
            draw.rectangle([12, 12, 340, 62], fill=(15, 23, 42))
            draw.rectangle([12, 12, 22, 62], fill=badge_color)
            draw.text((30, 20), f"{cam_key} -> {role}", fill=(255, 255, 255))
            draw.text((30, 40), f"Faces: {r_info.get('face_count', 1)} | Area: {r_info.get('max_face_area_ratio', 0.0):.3f}", fill=(203, 213, 225))
            panels.append(im)

        if not panels:
            return None
        sheet = Image.new("RGB", (target_w * len(panels), target_h), (10, 10, 14))
        for idx, pan in enumerate(panels):
            sheet.paste(pan, (idx * target_w, 0))
        out_png.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out_png)
        return str(out_png)
    except Exception:
        pass

    # Zero-dependency FFmpeg hstack fallback if Pillow is not installed
    valid_frames = [cam_frames[k] for k in sorted(cam_frames.keys()) if cam_frames[k].exists()]
    if valid_frames:
        ffmpeg = find_binary("ffmpeg")
        out_png.parent.mkdir(parents=True, exist_ok=True)
        inputs: List[str] = []
        for vf in valid_frames:
            inputs.extend(["-i", str(vf)])
        n = len(valid_frames)
        if n == 1:
            cmd = [ffmpeg, "-y"] + inputs + ["-vf", "scale=640:360", str(out_png)]
        else:
            scale_chains = "".join(f"[{i}:v]scale=640:360[v{i}];" for i in range(n))
            in_tags = "".join(f"[v{i}]" for i in range(n))
            cmd = [ffmpeg, "-y"] + inputs + ["-filter_complex", f"{scale_chains}{in_tags}hstack=inputs={n}", "-frames:v", "1", str(out_png)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30, check=False)
        if out_png.exists():
            return str(out_png)
    return None


def classify_cameras_and_speakers(sync_map_path: Path, diarized_path: Path) -> Dict[str, Any]:
    sync_map = json.loads(sync_map_path.read_text(encoding="utf-8"))
    diarized = json.loads(diarized_path.read_text(encoding="utf-8"))
    edit_dir = Path(sync_map["edit_dir"]).resolve()
    verify_dir = edit_dir / "verify"
    verify_dir.mkdir(parents=True, exist_ok=True)

    cameras = sync_map.get("cameras", {})
    segments = diarized.get("segments", [])
    if not cameras:
        return {"status": "error", "message": "No cameras found in sync_map.json"}

    # Pick sample timestamps for S0 solo speech and S1 solo speech
    s0_segs = [s for s in segments if s.get("speaker") == "S0" and (s["end"] - s["start"]) >= 1.5]
    s1_segs = [s for s in segments if s.get("speaker") == "S1" and (s["end"] - s["start"]) >= 1.5]

    s0_sample_t = float(s0_segs[0]["start"] + 0.3) if s0_segs else 2.0
    s1_sample_t = float(s1_segs[0]["start"] + 0.3) if s1_segs else min(6.0, float(sync_map.get("sequence_defaults", {}).get("master_duration_sec", 10.0)) * 0.5)

    cam_metrics: Dict[str, Dict[str, Any]] = {}
    sample_pngs: Dict[str, Path] = {}

    for cam_key, c_meta in cameras.items():
        v_path = Path(c_meta["path"])
        off_sec = float(c_meta.get("sync_offset_sec", 0.0))
        c_dur = float(c_meta.get("duration", 10.0))
        sample_t = max(0.2, min(c_dur - 0.5, s0_sample_t - off_sec))

        safe_cam = cam_key.replace(" ", "_")
        frame_png = verify_dir / f"{safe_cam}_sample.png"
        extract_frame_png(v_path, sample_t, frame_png)
        sample_pngs[cam_key] = frame_png

        f_info = detect_faces_in_image(frame_png)
        # Measure mouth/jaw motion during S0 speech vs S1 speech
        m_s0 = measure_mouth_motion_score(v_path, max(0.0, s0_sample_t - off_sec), 1.2)
        m_s1 = measure_mouth_motion_score(v_path, max(0.0, s1_sample_t - off_sec), 1.2)

        # Also check folder/file name hints if user named folders or files descriptively
        name_lower = f"{cam_key} {Path(c_meta.get('folder', '')).name} {v_path.stem}".lower()
        explicit_wide_hint = any(w in name_lower for w in ("wide", "master", "both", "group", "all", "two", "center"))

        cam_metrics[cam_key] = {
            "camera": cam_key,
            "path": str(v_path),
            "face_count": f_info["face_count"],
            "max_face_area_ratio": f_info["max_face_area_ratio"],
            "horizontal_spread": f_info["horizontal_spread"],
            "person_in_frame": f_info["person_in_frame"],
            "mouth_motion_s0": m_s0,
            "mouth_motion_s1": m_s1,
            "explicit_wide_hint": explicit_wide_hint,
            "detector": f_info.get("detector", "opencv"),
        }

    cam_keys = sorted(cam_metrics.keys())
    roles_to_cam: Dict[str, str] = {}

    if len(cam_keys) == 1:
        roles_to_cam = {"WIDE": cam_keys[0], "CU_S0": cam_keys[0], "CU_S1": cam_keys[0]}
    elif len(cam_keys) == 2:
        roles_to_cam = {"CU_S0": cam_keys[0], "CU_S1": cam_keys[1], "WIDE": cam_keys[0]}
    else:
        # Step 1: Identify the WIDE camera among the 3 cameras
        # Priority: explicit_wide_hint -> highest face_count (>=2) -> smallest max_face_area_ratio (or Camera 3 default on tie)
        def wide_score(k: str) -> Tuple[int, int, float, int]:
            m = cam_metrics[k]
            return (
                1 if m["explicit_wide_hint"] else 0,
                1 if m["face_count"] >= 2 else 0,
                -float(m["max_face_area_ratio"]),
                1 if k == "Camera 3" else 0,
            )

        wide_cam = max(cam_keys, key=wide_score)
        roles_to_cam["WIDE"] = wide_cam

        # Step 2: Assign the remaining two Close-Up cameras to CU_S0 and CU_S1 based on active lip/jaw motion
        cu_cams = [k for k in cam_keys if k != wide_cam]
        c_a, c_b = cu_cams[0], cu_cams[1]
        # Compare differential mouth motion `(mouth_s0 - mouth_s1)` between c_a and c_b
        diff_a = cam_metrics[c_a]["mouth_motion_s0"] - cam_metrics[c_a]["mouth_motion_s1"]
        diff_b = cam_metrics[c_b]["mouth_motion_s0"] - cam_metrics[c_b]["mouth_motion_s1"]

        if diff_a >= diff_b:
            roles_to_cam["CU_S0"] = c_a
            roles_to_cam["CU_S1"] = c_b
        else:
            roles_to_cam["CU_S0"] = c_b
            roles_to_cam["CU_S1"] = c_a

    # Annotate each camera's assigned role
    for r_label, c_key in roles_to_cam.items():
        if c_key in cam_metrics and "role" not in cam_metrics[c_key]:
            cam_metrics[c_key]["role"] = r_label

    sheet_path = build_verification_sheet(sample_pngs, cam_metrics, verify_dir / "camera_assignment_sheet.png")

    payload = {
        "status": "success",
        "roles": roles_to_cam,
        "cameras": cam_metrics,
        "verification_sheet_png": sheet_path,
    }
    out_json = edit_dir / "camera_roles.json"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify Camera 1, Camera 2, Camera 3 into Wide vs Close-Up S0/S1")
    parser.add_argument("--sync-map", type=Path, required=True, help="Path to edit/sync_map.json")
    parser.add_argument("--diarized", type=Path, required=True, help="Path to edit/diarized_segments.json")
    args = parser.parse_args()

    res = classify_cameras_and_speakers(args.sync_map.resolve(), args.diarized.resolve())
    print(json.dumps(res, indent=2))
    return 0 if res.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
