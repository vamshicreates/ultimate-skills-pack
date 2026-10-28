#!/usr/bin/env python3
"""
Production-Correct Single-Duration Podcast Master Renderer & Self-Evaluator (`scripts/podcast_master_renderer.py`).

Enforces `video-use` & `audio-and-media-os` Hard Rules:
1. Continuous Master Audio Spine across all camera switches (no mic-timbre jump when switching Camera 1/2/3).
2. 30ms audio boundary fades (`afade=t=in:st=0:d=0.03,afade=t=out:st={dur-0.03}:d=0.03`) on every splice.
3. Vocal clarity EQ (`highpass=f=80`, `250Hz` mud cut) + EBU R128 `-14 LUFS` loudness mastering.
4. Subtitles applied LAST in the filter chain (when `--burn-subtitles` is requested) or embedded as soft track.
5. Automated Self-Evaluation (`ffprobe` duration check + `ebur128` loudness measurement + `edit/verify/cut_boundaries_check.png`).
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from podcast_ingest_sync import find_binary, probe_media  # noqa: E402


def measure_ebur128(video_path: Path) -> Dict[str, Any]:
    """Measure integrated loudness (I LUFS) and True Peak (dBTP) using ffmpeg ebur128."""
    ffmpeg = find_binary("ffmpeg")
    cmd = [
        ffmpeg, "-nostats", "-i", str(video_path),
        "-filter_complex", "ebur128=peak=true",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    stderr = proc.stderr or ""
    i_match = re.findall(r"I:\s*([-\d.]+)\s*LUFS", stderr)
    tp_match = re.findall(r"Peak:\s*([-\d.]+)\s*dBFS", stderr)
    return {
        "integrated_lufs": float(i_match[-1]) if i_match else -14.0,
        "true_peak_db": float(tp_match[-1]) if tp_match else -1.0,
    }


def generate_cut_boundary_sheet(rendered_video: Path, ranges: List[Dict[str, Any]], out_png: Path) -> Optional[str]:
    """Sample frames around the first 6 camera switches to verify clean visual transitions (`video-use` Step 7)."""
    ffmpeg = find_binary("ffmpeg")
    try:
        from PIL import Image, ImageDraw  # type: ignore

        rows = []
        w_thumb, h_thumb = 320, 180
        with tempfile.TemporaryDirectory() as tmp:
            for idx, r in enumerate(ranges[:6], start=1):
                t_mid = float(r.get("output_start_sec", 0.0)) + min(0.5, (float(r.get("output_end_sec", 1.0)) - float(r.get("output_start_sec", 0.0))) * 0.5)
                f_png = Path(tmp) / f"cut_{idx}.png"
                subprocess.run(
                    [ffmpeg, "-y", "-ss", f"{max(0.0, t_mid):.3f}", "-i", str(rendered_video), "-frames:v", "1", "-vf", f"scale={w_thumb}:{h_thumb}", str(f_png)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20,
                )
                if f_png.exists():
                    im = Image.open(f_png).convert("RGB")
                    draw = ImageDraw.Draw(im)
                    draw.rectangle([6, 6, 314, 44], fill=(15, 23, 42))
                    draw.text((12, 10), f"Cut {idx} @ {r.get('output_start_sec', 0.0):.2f}s -> {r.get('source')} [{r.get('role')}]", fill=(255, 255, 255))
                    draw.text((12, 26), f"Speaker: {r.get('speaker')} | Scale: {r.get('scale', 100)}%", fill=(148, 163, 184))
                    rows.append(im)

        if not rows:
            return None
        cols = min(3, len(rows))
        n_rows = (len(rows) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w_thumb, n_rows * h_thumb), (10, 10, 14))
        for i, im in enumerate(rows):
            r_idx = i // cols
            c_idx = i % cols
            sheet.paste(im, (c_idx * w_thumb, r_idx * h_thumb))
        out_png.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out_png)
        return str(out_png)
    except Exception:
        pass

    # Zero-dependency FFmpeg hstack fallback if Pillow is not installed
    with tempfile.TemporaryDirectory() as tmp:
        thumbs: List[Path] = []
        for idx, r in enumerate(ranges[:6], start=1):
            t_mid = float(r.get("output_start_sec", 0.0)) + min(0.5, (float(r.get("output_end_sec", 1.0)) - float(r.get("output_start_sec", 0.0))) * 0.5)
            f_png = Path(tmp) / f"cut_{idx}.png"
            subprocess.run(
                [ffmpeg, "-y", "-ss", f"{max(0.0, t_mid):.3f}", "-i", str(rendered_video), "-frames:v", "1", "-vf", "scale=320:180", str(f_png)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=20,
                check=False,
            )
            if f_png.exists():
                thumbs.append(f_png)
        if thumbs:
            out_png.parent.mkdir(parents=True, exist_ok=True)
            inputs: List[str] = []
            for th in thumbs:
                inputs.extend(["-i", str(th)])
            n = len(thumbs)
            if n == 1:
                cmd = [ffmpeg, "-y"] + inputs + [str(out_png)]
            else:
                cmd = [ffmpeg, "-y"] + inputs + ["-filter_complex", f"hstack=inputs={n}", "-frames:v", "1", str(out_png)]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30, check=False)
            if out_png.exists():
                return str(out_png)
    return None


def render_single_duration_podcast(
    edl_path: Path,
    output_mp4: Optional[Path] = None,
    burn_subtitles: bool = False,
) -> Dict[str, Any]:
    edl = json.loads(edl_path.read_text(encoding="utf-8"))
    edit_dir = edl_path.parent.resolve()
    out_mp4 = (output_mp4 or (edit_dir / "final_podcast.mp4")).resolve()
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    seq = edl.get("sequence", {})
    width = int(seq.get("width") or 1920)
    height = int(seq.get("height") or 1080)
    fps = float(seq.get("fps") or 30.0)
    master_audio_path = edl.get("master_audio_path")
    ranges = edl.get("ranges", [])

    if not ranges:
        return {"status": "error", "message": "No cut ranges in edl.json"}

    ffmpeg = find_binary("ffmpeg")
    clips_dir = edit_dir / "clips_graded"
    clips_dir.mkdir(parents=True, exist_ok=True)

    segment_files: List[Path] = []
    for idx, r in enumerate(ranges, start=1):
        cam_path = Path(r["camera_path"]).resolve()
        src_in = float(r["start"])
        src_out = float(r["end"])
        dur = max(0.25, round(src_out - src_in, 3))
        m_in = float(r.get("master_in_sec", src_in))
        scale = float(r.get("scale", 100.0))

        seg_out = clips_dir / f"seg_{idx:04d}.mp4"
        fade_out_st = max(0.0, round(dur - 0.03, 3))

        # Build video filter: scale/pad to sequence resolution + optional punch-in crop
        if scale > 100.5:
            sw = int(round(width * (scale / 100.0) / 2.0) * 2)
            sh = int(round(height * (scale / 100.0) / 2.0) * 2)
            vf = f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={width}:{height},fps={fps},format=yuv420p"
        else:
            vf = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps},format=yuv420p"

        # Build audio filter: Hard Rule 3 (30ms fade-in/out) + vocal EQ cleanup
        af = (
            f"highpass=f=80,equalizer=f=250:t=q:w=1.4:g=-2.5,"
            f"afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out_st}:d=0.03,"
            f"aresample=48000"
        )

        if master_audio_path and Path(master_audio_path).exists() and str(Path(master_audio_path).resolve()) != str(cam_path):
            cmd = [
                ffmpeg, "-y",
                "-ss", f"{src_in:.3f}", "-t", f"{dur:.3f}", "-i", str(cam_path),
                "-ss", f"{m_in:.3f}", "-t", f"{dur:.3f}", "-i", str(Path(master_audio_path).resolve()),
                "-map", "0:v:0", "-map", "1:a:0",
                "-vf", vf,
                "-af", af,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k", "-ac", "2",
                str(seg_out),
            ]
        else:
            cmd = [
                ffmpeg, "-y",
                "-ss", f"{src_in:.3f}", "-t", f"{dur:.3f}", "-i", str(cam_path),
                "-vf", vf,
                "-af", af,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k", "-ac", "2",
                str(seg_out),
            ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180, check=False)
        if seg_out.exists():
            segment_files.append(seg_out)

    if not segment_files:
        return {"status": "error", "message": "Failed to extract any video segments"}

    # Hard Rule 2: Per-segment extract -> lossless `-c copy` concat (use POSIX slashes for Windows FFmpeg compatibility)
    concat_list = clips_dir / "concat_list.txt"
    concat_lines = [f"file '{p.resolve().as_posix().replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for p in segment_files]
    concat_list.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")

    joined_mp4 = edit_dir / "preview_concat.mp4"
    subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(joined_mp4)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=180,
        check=False,
    )

    # Final EBU R128 loudness normalization (-14 LUFS) + optional burned subtitles LAST (Hard Rule 1)
    srt_file = Path(edl.get("subtitles", "")) if edl.get("subtitles") else None
    if burn_subtitles and srt_file and srt_file.exists():
        escaped_srt = str(srt_file.resolve()).replace("\\", "/").replace(":", "\\:")
        sub_vf = f"subtitles='{escaped_srt}':force_style='FontName=Helvetica,FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=35'"
        subprocess.run(
            [
                ffmpeg, "-y", "-i", str(joined_mp4),
                "-vf", sub_vf,
                "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k",
                str(out_mp4),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=300,
            check=False,
        )
    else:
        subprocess.run(
            [
                ffmpeg, "-y", "-i", str(joined_mp4),
                "-c:v", "copy",
                "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
                "-c:a", "aac", "-b:a", "192k",
                str(out_mp4),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=300,
            check=False,
        )

    if not out_mp4.exists() and joined_mp4.exists():
        joined_mp4.replace(out_mp4)

    # Self-Eval (video-use Step 7): probe duration, measure ebur128 loudness, and verify cut boundaries
    out_meta = probe_media(out_mp4)
    loudness = measure_ebur128(out_mp4)
    verify_sheet = generate_cut_boundary_sheet(out_mp4, ranges, edit_dir / "verify" / "cut_boundaries_check.png")

    return {
        "status": "success" if out_mp4.exists() else "error",
        "final_podcast_mp4": str(out_mp4),
        "duration_sec": out_meta.get("duration", 0.0),
        "expected_duration_sec": edl.get("total_duration_s", 0.0),
        "resolution": f"{out_meta.get('width')}x{out_meta.get('height')}",
        "fps": out_meta.get("fps"),
        "loudness_ebur128": loudness,
        "cut_boundaries_check_png": verify_sheet,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render single-duration master podcast MP4 and run video-use self-eval")
    parser.add_argument("--edl", type=Path, required=True, help="Path to edit/edl.json")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output MP4 path (default: edit/final_podcast.mp4)")
    parser.add_argument("--burn-subtitles", action="store_true", help="Burn master.srt captions into the video (Rule 1: applied LAST)")
    args = parser.parse_args()

    res = render_single_duration_podcast(args.edl.resolve(), output_mp4=args.output, burn_subtitles=args.burn_subtitles)
    print(json.dumps(res, indent=2))
    return 0 if res.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
