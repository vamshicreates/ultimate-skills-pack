#!/usr/bin/env python3
"""
Multi-Cam Podcast EDL Director & NLE Interchange Compiler (`scripts/podcast_edl_director.py`).

Combines:
- `edit/sync_map.json` (Camera 1/2/3 + Master Audio sync offsets)
- `edit/diarized_segments.json` (Speaker turns S0/S1/BOTH & word boundaries)
- `edit/camera_roles.json` (WIDE, CU_S0, CU_S1 assignments)
- `scripts/laya_decision_gate.py` (NandhaKishorM/laya non-autoregressive decision engine)

Generates:
1. `edit/edl.json` — Master switched multicam Edit Decision List
2. `edit/timeline_spec.json` — Premiere Pro Live Foreground & XML Builder spec
3. `edit/podcast_master.xml` — FCP7 `xmeml v4` multi-track sequence (Premiere Pro & DaVinci Resolve)
4. `edit/podcast_master.fcpxml` — FCPXML v1.10 rational-frame timeline (DaVinci Resolve & Final Cut Pro)
5. `edit/master.srt` — Output-timeline synchronized captions (video-use Hard Rule 5)
"""

import argparse
import json
import math
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.dom import minidom

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from laya_decision_gate import decide_podcast_segment_angle, evaluate_decision  # noqa: E402


def path_to_file_url(file_path: str) -> str:
    p = Path(file_path).resolve()
    posix = p.as_posix()
    if not posix.startswith("/"):
        posix = "/" + posix
    return f"file://localhost{urllib.parse.quote(posix, safe='/:')}"


def format_srt_timestamp(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    ms = int(round((seconds - int(seconds)) * 1000))
    total_s = int(seconds)
    if ms >= 1000:
        ms -= 1000
        total_s += 1
    s = total_s % 60
    m = (total_s // 60) % 60
    h = total_s // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_output_srt(cuts: List[Dict[str, Any]], srt_path: Path) -> str:
    """Write output-timeline synchronized SRT captions (video-use Hard Rule 5)."""
    lines: List[str] = []
    for idx, c in enumerate(cuts, start=1):
        st = format_srt_timestamp(c["output_start_sec"])
        en = format_srt_timestamp(c["output_end_sec"])
        spk = c.get("speaker", "S0")
        txt = str(c.get("quote", "")).strip() or f"[{spk}]"
        lines.append(f"{idx}\n{st} --> {en}\n{txt}\n")
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    srt_path.write_text("\n".join(lines), encoding="utf-8")
    return str(srt_path)


def compile_xmeml_v4(
    seq_name: str,
    width: int,
    height: int,
    fps: float,
    cuts: List[Dict[str, Any]],
    master_audio_path: Optional[str],
    out_xml_path: Path,
) -> str:
    """Compile FCP7 `xmeml version="4"` multi-track sequence for Premiere Pro & DaVinci Resolve."""
    timebase = int(round(fps))
    ntsc = abs(fps - round(fps)) > 0.001

    def sec_to_frames(sec: float) -> int:
        return int(round(float(sec) * timebase))

    def add_rate(parent: ET.Element):
        r = ET.SubElement(parent, "rate")
        ET.SubElement(r, "timebase").text = str(timebase)
        ET.SubElement(r, "ntsc").text = "TRUE" if ntsc else "FALSE"

    xmeml = ET.Element("xmeml", version="4")
    seq = ET.SubElement(xmeml, "sequence", id="podcast-sequence-1")
    ET.SubElement(seq, "name").text = seq_name
    add_rate(seq)

    media = ET.SubElement(seq, "media")
    video = ET.SubElement(media, "video")
    v_fmt = ET.SubElement(video, "format")
    v_sc = ET.SubElement(v_fmt, "samplecharacteristics")
    add_rate(v_sc)
    ET.SubElement(v_sc, "width").text = str(width)
    ET.SubElement(v_sc, "height").text = str(height)
    ET.SubElement(v_sc, "anamorphic").text = "FALSE"
    ET.SubElement(v_sc, "pixelaspectratio").text = "square"
    ET.SubElement(v_sc, "fielddominance").text = "none"

    audio = ET.SubElement(media, "audio")
    ET.SubElement(audio, "numOutputChannels").text = "2"
    a_fmt = ET.SubElement(audio, "format")
    a_sc = ET.SubElement(a_fmt, "samplecharacteristics")
    ET.SubElement(a_sc, "depth").text = "16"
    ET.SubElement(a_sc, "samplerate").text = "48000"

    file_reg: Dict[str, str] = {}

    def attach_file(clip_el: ET.Element, media_path: str, min_frames: int, has_video: bool = True, has_audio: bool = True):
        abs_p = str(Path(media_path).resolve())
        if abs_p not in file_reg:
            fid = f"file-{len(file_reg) + 1}"
            file_reg[abs_p] = fid
            fnode = ET.SubElement(clip_el, "file", id=fid)
            ET.SubElement(fnode, "name").text = Path(abs_p).name
            ET.SubElement(fnode, "pathurl").text = path_to_file_url(abs_p)
            add_rate(fnode)
            ET.SubElement(fnode, "duration").text = str(max(min_frames, 3600))
            fmed = ET.SubElement(fnode, "media")
            if has_video:
                ET.SubElement(fmed, "video")
            if has_audio:
                faud = ET.SubElement(fmed, "audio")
                ET.SubElement(faud, "channelcount").text = "2"
        else:
            ET.SubElement(clip_el, "file", id=file_reg[abs_p])

    v1_track = ET.SubElement(video, "track")
    a1_track = ET.SubElement(audio, "track")
    total_frames = 0

    for idx, c in enumerate(cuts, start=1):
        in_f = sec_to_frames(c["source_in_sec"])
        out_f = sec_to_frames(c["source_out_sec"])
        dur_f = max(1, out_f - in_f)
        start_f = sec_to_frames(c["output_start_sec"])
        end_f = start_f + dur_f
        total_frames = max(total_frames, end_f)

        cname = f"{c['camera']}_{c['role']}_{idx:02d}"
        v_ci = ET.SubElement(v1_track, "clipitem", id=f"clipitem-v1-{idx}")
        ET.SubElement(v_ci, "name").text = cname
        ET.SubElement(v_ci, "enabled").text = "TRUE"
        ET.SubElement(v_ci, "duration").text = str(out_f + 300)
        add_rate(v_ci)
        ET.SubElement(v_ci, "start").text = str(start_f)
        ET.SubElement(v_ci, "end").text = str(end_f)
        ET.SubElement(v_ci, "in").text = str(in_f)
        ET.SubElement(v_ci, "out").text = str(out_f)
        attach_file(v_ci, c["camera_path"], out_f + 300, has_video=True, has_audio=True)

        scale_pct = float(c.get("scale", 100.0))
        if abs(scale_pct - 100.0) >= 0.1:
            filt = ET.SubElement(v_ci, "filter")
            eff = ET.SubElement(filt, "effect")
            ET.SubElement(eff, "name").text = "Basic Motion"
            ET.SubElement(eff, "effectid").text = "basic"
            ET.SubElement(eff, "effectcategory").text = "motion"
            ET.SubElement(eff, "effecttype").text = "motion"
            ET.SubElement(eff, "mediatype").text = "video"
            param = ET.SubElement(eff, "parameter")
            ET.SubElement(param, "parameterid").text = "scale"
            ET.SubElement(param, "name").text = "Scale"
            ET.SubElement(param, "valuemin").text = "0"
            ET.SubElement(param, "valuemax").text = "1000"
            ET.SubElement(param, "value").text = str(scale_pct)

        # Audio track A1 uses the Master Audio Spine (aligned via master_in_sec / master_out_sec)
        aud_path = master_audio_path or c["camera_path"]
        a_in_f = sec_to_frames(c["master_in_sec"])
        a_out_f = a_in_f + dur_f
        a_ci = ET.SubElement(a1_track, "clipitem", id=f"clipitem-a1-{idx}")
        ET.SubElement(a_ci, "name").text = f"MasterAudio_{idx:02d}"
        ET.SubElement(a_ci, "enabled").text = "TRUE"
        ET.SubElement(a_ci, "duration").text = str(a_out_f + 300)
        add_rate(a_ci)
        ET.SubElement(a_ci, "start").text = str(start_f)
        ET.SubElement(a_ci, "end").text = str(end_f)
        ET.SubElement(a_ci, "in").text = str(a_in_f)
        ET.SubElement(a_ci, "out").text = str(a_out_f)
        attach_file(a_ci, aud_path, a_out_f + 300, has_video=(aud_path == c["camera_path"]), has_audio=True)

        # Add sequence marker for each camera angle switch
        m_el = ET.SubElement(seq, "marker")
        ET.SubElement(m_el, "name").text = f"{c['role']} ({c['camera']} - {c['speaker']})"
        ET.SubElement(m_el, "comment").text = str(c.get("reason", ""))
        ET.SubElement(m_el, "in").text = str(start_f)
        ET.SubElement(m_el, "out").text = "-1"

    ET.SubElement(seq, "duration").text = str(max(total_frames, timebase))
    xml_bytes = ET.tostring(xmeml, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
    lines = pretty_xml.splitlines()
    if lines and lines[0].startswith("<?xml"):
        lines.insert(1, "<!DOCTYPE xmeml>")
    out_xml_path.parent.mkdir(parents=True, exist_ok=True)
    out_xml_path.write_text("\n".join(lines), encoding="utf-8")
    return str(out_xml_path)


def compile_fcpxml_v110(
    seq_name: str,
    width: int,
    height: int,
    fps: float,
    cuts: List[Dict[str, Any]],
    out_fcpxml_path: Path,
) -> str:
    """
    Compile Final Cut Pro `.fcpxml` v1.10 with strict rational frame fractions
    (per `timeline-and-storyboards` multi-track NLE mapping rules) for DaVinci Resolve & Final Cut Pro.
    """
    fps_int = max(1, int(round(fps)))
    den = fps_int * 100

    def sec_to_rational(sec: float) -> str:
        frames = int(round(float(sec) * fps_int))
        return f"{frames * 100}/{den}s"

    fcpxml = ET.Element("fcpxml", version="1.10")
    resources = ET.SubElement(fcpxml, "resources")
    ET.SubElement(
        resources,
        "format",
        id="r1",
        name=f"FFVideoFormat{height}p{fps_int}",
        frameDuration=f"100/{den}s",
        width=str(width),
        height=str(height),
    )

    asset_map: Dict[str, str] = {}
    for c in cuts:
        p = str(Path(c["camera_path"]).resolve())
        if p not in asset_map:
            aid = f"r{len(asset_map) + 2}"
            asset_map[p] = aid
            asset = ET.SubElement(
                resources,
                "asset",
                id=aid,
                name=Path(p).name,
                start="0s",
                duration=sec_to_rational(max(3600.0, c["source_out_sec"] + 60.0)),
                hasVideo="1",
                hasAudio="1",
                format="r1",
            )
            ET.SubElement(asset, "media-rep", kind="original-media", src=path_to_file_url(p))

    library = ET.SubElement(fcpxml, "library")
    event = ET.SubElement(library, "event", name="Podcast_Multicam_Edit")
    project = ET.SubElement(event, "project", name=seq_name)
    total_dur = cuts[-1]["output_end_sec"] if cuts else 0.0
    sequence = ET.SubElement(
        project,
        "sequence",
        format="r1",
        duration=sec_to_rational(total_dur),
        tcStart="0s",
        tcFormat="NDF",
    )
    spine = ET.SubElement(sequence, "spine")

    for idx, c in enumerate(cuts, start=1):
        p = str(Path(c["camera_path"]).resolve())
        aid = asset_map[p]
        dur_s = max(1.0 / fps_int, c["output_end_sec"] - c["output_start_sec"])
        ac = ET.SubElement(
            spine,
            "asset-clip",
            name=f"{c['camera']} [{c['role']} - {c['speaker']}]",
            ref=aid,
            offset=sec_to_rational(c["output_start_sec"]),
            start=sec_to_rational(c["source_in_sec"]),
            duration=sec_to_rational(dur_s),
            format="r1",
        )
        ET.SubElement(
            ac,
            "marker",
            start=sec_to_rational(c["source_in_sec"]),
            duration=f"100/{den}s",
            value=f"{c['role']}: {c.get('reason', '')[:80]}",
        )

    xml_bytes = ET.tostring(fcpxml, encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
    lines = pretty.splitlines()
    if lines and lines[0].startswith("<?xml"):
        lines.insert(1, "<!DOCTYPE fcpxml>")
    out_fcpxml_path.parent.mkdir(parents=True, exist_ok=True)
    out_fcpxml_path.write_text("\n".join(lines), encoding="utf-8")
    return str(out_fcpxml_path)


def build_podcast_multicam_edl(
    sync_map_path: Path,
    diarized_path: Path,
    camera_roles_path: Path,
    brief_text: str = "",
    pad_pre_sec: float = 0.06,
    pad_post_sec: float = 0.10,
    merge_gap_sec: float = 0.60,
) -> Dict[str, Any]:
    sync_map = json.loads(sync_map_path.read_text(encoding="utf-8"))
    diarized = json.loads(diarized_path.read_text(encoding="utf-8"))
    camera_roles = json.loads(camera_roles_path.read_text(encoding="utf-8"))

    edit_dir = Path(sync_map["edit_dir"]).resolve()
    seq_def = sync_map.get("sequence_defaults", {})
    width = int(seq_def.get("width") or 1920)
    height = int(seq_def.get("height") or 1080)
    fps = float(seq_def.get("fps") or 30.0)
    master_dur = float(seq_def.get("master_duration_sec") or 60.0)
    master_audio_path = sync_map.get("master_audio", {}).get("path")

    cameras = sync_map.get("cameras", {})
    roles_map = camera_roles.get("roles", {})
    raw_segments = diarized.get("segments", [])

    # Step 1: Consult Laya Decision Gate on overall podcast brief if complex/provided
    overall_laya = evaluate_decision(
        brief_text or "Multi-camera 3-angle podcast edit with active speaker close-ups, wide shots on banter/laughter, and dead-air tightening",
        force_laya=False,
    )

    # Step 2: Merge consecutive same-speaker phrases separated by tiny gaps (< merge_gap_sec)
    # while keeping individual camera shots under ~12s so visual pacing stays engaging
    merged_segments: List[Dict[str, Any]] = []
    for seg in raw_segments:
        st = max(0.0, float(seg["start"]) - pad_pre_sec)
        en = min(master_dur, float(seg["end"]) + pad_post_sec)
        if en - st < 0.35:
            continue
        spk = str(seg.get("speaker", "S0"))
        txt = str(seg.get("text", "")).strip()
        is_ct = bool(seg.get("is_crosstalk", False))

        if (
            merged_segments
            and merged_segments[-1]["speaker"] == spk
            and merged_segments[-1]["is_crosstalk"] == is_ct
            and (st - merged_segments[-1]["end"]) <= merge_gap_sec
            and (en - merged_segments[-1]["start"]) <= 11.0
        ):
            merged_segments[-1]["end"] = round(en, 3)
            merged_segments[-1]["text"] = f"{merged_segments[-1]['text']} {txt}".strip()
        else:
            merged_segments.append({
                "start": round(st, 3),
                "end": round(en, 3),
                "speaker": spk,
                "text": txt,
                "is_crosstalk": is_ct,
            })

    if not merged_segments and cameras:
        merged_segments = [{"start": 0.0, "end": min(master_dur, 15.0), "speaker": "S0", "text": "[Podcast Dialogue]", "is_crosstalk": False}]

    # Step 3: Assign Camera Angles (WIDE, CU_S0, CU_S1) per segment via Laya + Multicam Rules
    cuts: List[Dict[str, Any]] = []
    prev_role = ""
    consecutive_same_role_sec = 0.0
    output_cursor_sec = 0.0

    for idx, seg in enumerate(merged_segments):
        decision = decide_podcast_segment_angle(
            segment=seg,
            seg_index=idx,
            total_segments=len(merged_segments),
            prev_angle=prev_role,
            consecutive_same_angle_sec=consecutive_same_role_sec,
            available_roles=roles_map,
            use_laya_for_ambiguous=True,
        )

        chosen_role = decision["role"]
        chosen_cam = decision["camera"]
        if chosen_cam not in cameras:
            chosen_cam = next(iter(cameras.keys()))

        cam_meta = cameras[chosen_cam]
        cam_off = float(cam_meta.get("sync_offset_sec", 0.0))
        cam_dur = float(cam_meta.get("duration", master_dur))
        cam_person_ok = camera_roles.get("cameras", {}).get(chosen_cam, {}).get("person_in_frame", True)

        # Convert master audio timestamps `[seg.start, seg.end]` to camera source timestamps
        seg_dur = round(seg["end"] - seg["start"], 3)
        # Only apply sync offset if sync_confidence >= 0.35 and offset stays within camera bounds
        sync_conf = float(cam_meta.get("sync_confidence", 0.0))
        effective_off = cam_off if (sync_conf >= 0.35 and 0.0 <= (seg["start"] - cam_off) and (seg["end"] - cam_off) <= cam_dur) else 0.0
        src_in = round(seg["start"] - effective_off, 3)
        src_out = round(seg["end"] - effective_off, 3)

        # Safety check: only fall back to WIDE if person_in_frame is False or camera stopped recording before seg.start
        if not cam_person_ok or seg["start"] >= cam_dur:
            wide_cam = roles_map.get("WIDE", chosen_cam)
            if wide_cam in cameras:
                w_meta = cameras[wide_cam]
                if seg["start"] < float(w_meta.get("duration", master_dur)):
                    chosen_cam = wide_cam
                    chosen_role = "WIDE"
                    cam_meta = w_meta
                    cam_dur = float(w_meta.get("duration", master_dur))
                    src_in = round(seg["start"], 3)
                    src_out = round(seg["end"], 3)

        # Clamp safely within source camera bounds
        src_in = max(0.0, min(max(0.0, cam_dur - seg_dur), src_in))
        src_out = round(min(cam_dur, src_in + seg_dur), 3)
        actual_dur = round(max(0.35, src_out - src_in), 3)

        if chosen_role == prev_role:
            consecutive_same_role_sec += actual_dur
        else:
            consecutive_same_role_sec = actual_dur
        prev_role = chosen_role

        out_start = round(output_cursor_sec, 3)
        out_end = round(out_start + actual_dur, 3)
        output_cursor_sec = out_end

        cuts.append({
            "cut_index": idx + 1,
            "camera": chosen_cam,
            "camera_path": cam_meta["path"],
            "role": chosen_role,
            "speaker": seg["speaker"],
            "master_in_sec": round(seg["start"], 3),
            "master_out_sec": round(seg["start"] + actual_dur, 3),
            "source_in_sec": src_in,
            "source_out_sec": src_out,
            "output_start_sec": out_start,
            "output_end_sec": out_end,
            "duration_sec": actual_dur,
            "scale": float(decision.get("scale", 100.0)),
            "beat": decision["beat"],
            "quote": seg["text"],
            "reason": decision["reason"],
            "laya_invoked": decision.get("laya_invoked", False),
        })

    # Write 1: `edit/master.srt`
    srt_path = write_output_srt(cuts, edit_dir / "master.srt")

    # Write 2: `edit/edl.json` (compatible with video-use & timeline-and-storyboards)
    sources_dict = {k: v["path"] for k, v in cameras.items()}
    edl_payload = {
        "version": 1,
        "type": "podcast_multicam",
        "sequence": {
            "name": "Podcast_Master_Edit",
            "width": width,
            "height": height,
            "fps": fps,
        },
        "master_audio_path": master_audio_path,
        "camera_roles": roles_map,
        "laya_decision_summary": overall_laya,
        "sources": sources_dict,
        "ranges": [
            {
                "source": c["camera"],
                "camera_path": c["camera_path"],
                "role": c["role"],
                "speaker": c["speaker"],
                "start": c["source_in_sec"],
                "end": c["source_out_sec"],
                "master_in_sec": c["master_in_sec"],
                "master_out_sec": c["master_out_sec"],
                "output_start_sec": c["output_start_sec"],
                "output_end_sec": c["output_end_sec"],
                "scale": c["scale"],
                "beat": c["beat"],
                "quote": c["quote"],
                "reason": c["reason"],
            }
            for c in cuts
        ],
        "subtitles": srt_path,
        "total_duration_s": round(output_cursor_sec, 3),
    }
    edl_path = edit_dir / "edl.json"
    edl_path.write_text(json.dumps(edl_payload, indent=2), encoding="utf-8")

    # Write 3: `edit/podcast_master.xml` (FCP7 xmeml v4) & `edit/podcast_master.fcpxml` (FCPXML v1.10)
    xml_path = compile_xmeml_v4("Podcast_Master_Edit", width, height, fps, cuts, master_audio_path, edit_dir / "podcast_master.xml")
    fcpxml_path = compile_fcpxml_v110("Podcast_Master_Edit", width, height, fps, cuts, edit_dir / "podcast_master.fcpxml")

    # Write 4: `edit/timeline_spec.json` (for Premiere Pro Live Foreground Builder)
    timeline_spec = {
        "sequence": {
            "name": "Podcast_Master_Edit",
            "width": width,
            "height": height,
            "fps": fps,
        },
        "outputXml": xml_path,
        "outputFcpxml": fcpxml_path,
        "outputSrt": srt_path,
        "masterAudioPath": master_audio_path,
        "v1_aroll": [
            {
                "name": f"{c['camera']}_{c['role']}_Cut{c['cut_index']:02d}",
                "camera": c["camera"],
                "role": c["role"],
                "speaker": c["speaker"],
                "path": c["camera_path"],
                "inSec": c["source_in_sec"],
                "outSec": c["source_out_sec"],
                "startSec": c["output_start_sec"],
                "masterInSec": c["master_in_sec"],
                "masterOutSec": c["master_out_sec"],
                "scale": c["scale"],
                "gainDb": 0.0,
            }
            for c in cuts
        ],
        "markers": [
            {
                "name": f"{c['role']} ({c['camera']} - {c['speaker']})",
                "timeSec": c["output_start_sec"],
                "comment": f"{c['beat']}: {c['reason']}",
                "role": c["role"],
            }
            for c in cuts
        ],
        "captions": [
            {
                "startSec": c["output_start_sec"],
                "endSec": c["output_end_sec"],
                "text": c["quote"],
            }
            for c in cuts
        ],
    }
    spec_path = edit_dir / "timeline_spec.json"
    spec_path.write_text(json.dumps(timeline_spec, indent=2), encoding="utf-8")

    # Compute angle distribution statistics
    role_counts: Dict[str, int] = {}
    role_durations: Dict[str, float] = {}
    for c in cuts:
        r = c["role"]
        role_counts[r] = role_counts.get(r, 0) + 1
        role_durations[r] = round(role_durations.get(r, 0.0) + c["duration_sec"], 2)

    return {
        "status": "success",
        "total_cuts": len(cuts),
        "total_duration_sec": round(output_cursor_sec, 3),
        "angle_distribution": {
            "counts": role_counts,
            "durations_sec": role_durations,
        },
        "edl_json": str(edl_path),
        "timeline_spec_json": str(spec_path),
        "xmeml_v4_xml": xml_path,
        "fcpxml_v110": fcpxml_path,
        "master_srt": srt_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build switched multi-cam podcast EDL, XML, FCPXML, and SRT")
    parser.add_argument("--sync-map", type=Path, required=True, help="Path to edit/sync_map.json")
    parser.add_argument("--diarized", type=Path, required=True, help="Path to edit/diarized_segments.json")
    parser.add_argument("--camera-roles", type=Path, required=True, help="Path to edit/camera_roles.json")
    parser.add_argument("--brief", type=str, default="", help="Optional user editorial brief for Laya Router")
    args = parser.parse_args()

    res = build_podcast_multicam_edl(
        sync_map_path=args.sync_map.resolve(),
        diarized_path=args.diarized.resolve(),
        camera_roles_path=args.camera_roles.resolve(),
        brief_text=args.brief,
    )
    print(json.dumps(res, indent=2))
    return 0 if res.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
