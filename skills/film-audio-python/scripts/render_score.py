#!/usr/bin/env python3
"""Render an event-based original music cue to 24-bit stereo WAV stems.

Usage: python3 render_score.py --spec cue.json --out output/cue-name
Requires NumPy. Events use seconds, semitone pitches (for example C#4),
gain in [0, 1], and pan in [-1, 1]. See the adjacent SKILL.md.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import wave
from pathlib import Path

import numpy as np


INSTRUMENTS = {"pad", "lead", "bass", "pluck", "kick", "snare", "hat", "noise"}
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,79}$")
PITCH_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d+)$")
SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def pitch_hz(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        midi = float(value)
    else:
        match = PITCH_RE.fullmatch(value.strip())
        if not match:
            raise ValueError(f"Invalid pitch {value!r}; use a note such as C#4 or a MIDI number")
        letter, accidental, octave = match.groups()
        midi = 12 * (int(octave) + 1) + SEMITONES[letter.upper()]
        midi += 1 if accidental == "#" else -1 if accidental == "b" else 0
    if not 0 <= midi <= 127:
        raise ValueError(f"MIDI pitch out of range: {midi}")
    return 440.0 * 2.0 ** ((midi - 69.0) / 12.0)


def envelope(t: np.ndarray, duration: float, attack: float, release: float) -> np.ndarray:
    attack = max(0.001, min(attack, duration / 2))
    release = max(0.001, min(release, duration / 2))
    return np.minimum(1.0, t / attack) * np.minimum(1.0, (duration - t) / release)


def synth(instrument: str, duration: float, sample_rate: int, pitch: object, rng: np.random.Generator) -> np.ndarray:
    count = max(1, round(duration * sample_rate))
    t = np.arange(count, dtype=np.float64) / sample_rate
    if instrument == "kick":
        phase = 2 * np.pi * (48 * t + 115 * (1 - np.exp(-28 * t)) / 28)
        sound = np.sin(phase) * np.exp(-13 * t)
        sound += 0.12 * rng.standard_normal(count) * np.exp(-85 * t)
    elif instrument == "snare":
        noise = rng.standard_normal(count)
        bright = np.diff(noise, prepend=noise[0]) * 0.35
        sound = (bright + 0.24 * np.sin(2 * np.pi * 185 * t)) * np.exp(-20 * t)
    elif instrument == "hat":
        noise = rng.standard_normal(count)
        sound = np.diff(noise, prepend=noise[0]) * 0.28 * np.exp(-55 * t)
    elif instrument == "noise":
        noise = rng.standard_normal(count)
        sound = noise * 0.22 * envelope(t, duration, 0.08, 0.15)
    else:
        if pitch is None:
            raise ValueError(f"{instrument} requires pitch")
        freq = pitch_hz(pitch)
        if instrument == "pad":
            sound = sum(
                np.sin(2 * np.pi * freq * ratio * t + phase)
                for ratio, phase in ((0.997, 0.0), (1.0, 0.4), (1.003, 1.1))
            ) / 3
            sound += 0.16 * np.sin(2 * np.pi * 2 * freq * t)
            sound *= envelope(t, duration, 0.35, 0.45)
        elif instrument == "lead":
            sound = np.sin(2 * np.pi * freq * t) + 0.28 * np.sin(2 * np.pi * 2 * freq * t)
            sound *= envelope(t, duration, 0.025, 0.12)
        elif instrument == "bass":
            sound = np.sin(2 * np.pi * freq * t) + 0.22 * np.sin(2 * np.pi * 2 * freq * t)
            sound *= envelope(t, duration, 0.015, 0.15) * (0.75 + 0.25 * np.exp(-8 * t))
        elif instrument == "pluck":
            sound = (
                np.sin(2 * np.pi * freq * t)
                + 0.38 * np.sin(2 * np.pi * 2 * freq * t)
                + 0.15 * np.sin(2 * np.pi * 3 * freq * t)
            )
            sound *= envelope(t, duration, 0.005, 0.04) * np.exp(-2.8 * t)
        else:
            raise ValueError(f"Unsupported instrument: {instrument}")
    return np.asarray(sound, dtype=np.float32)


def write_pcm24(path: Path, stereo: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = np.clip(stereo, -1.0, 1.0 - 1 / 8388608)
    integers = np.rint(safe * 8388607).astype("<i4")
    packed = integers.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(3)
        output.setframerate(sample_rate)
        output.writeframes(packed)


def render(spec: dict, out: Path) -> None:
    name = str(spec["name"])
    if not NAME_RE.fullmatch(name):
        raise ValueError("Cue name must use 2–80 letters, digits, underscores, or hyphens")
    if out.name != name:
        raise ValueError(f"Output folder must be named {name!r}")
    duration = float(spec["duration"])
    sample_rate = int(spec.get("sample_rate", 48000))
    if not 0 < duration <= 300 or not 8000 <= sample_rate <= 192000:
        raise ValueError("Duration must be 0–300 seconds and sample rate 8000–192000 Hz")
    events = spec.get("events", [])
    if not isinstance(events, list) or not events:
        raise ValueError("Provide a nonempty events list")

    rng = np.random.default_rng(int(spec.get("seed", 0)))
    total = round(duration * sample_rate)
    stems: dict[str, np.ndarray] = {}
    for index, event in enumerate(events, start=1):
        try:
            instrument = str(event["instrument"])
            start = float(event["start"])
            length = float(event["duration"])
            gain = float(event.get("gain", 0.2))
            pan = float(event.get("pan", 0))
            if instrument not in INSTRUMENTS:
                raise ValueError(f"Unknown instrument {instrument!r}")
            if not (math.isfinite(start) and math.isfinite(length) and math.isfinite(gain) and math.isfinite(pan)):
                raise ValueError("Event numbers must be finite")
            if start < 0 or length <= 0 or start + length > duration + 1 / sample_rate:
                raise ValueError("Event must fit within cue duration")
            if not 0 <= gain <= 1 or not -1 <= pan <= 1:
                raise ValueError("Gain must be 0–1 and pan -1–1")
            sound = synth(instrument, length, sample_rate, event.get("pitch"), rng)
            begin = round(start * sample_rate)
            end = min(total, begin + len(sound))
            sound = sound[: end - begin] * gain
            left = math.cos((pan + 1) * math.pi / 4)
            right = math.sin((pan + 1) * math.pi / 4)
            stem = stems.setdefault(instrument, np.zeros((total, 2), dtype=np.float32))
            stem[begin:end, 0] += sound * left
            stem[begin:end, 1] += sound * right
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Event {index}: {exc}") from exc

    mix = np.sum(np.stack(list(stems.values()), axis=0), axis=0)
    peak = float(np.max(np.abs(mix)))
    scale = min(1.0, 0.98 / peak) if peak else 1.0
    out.mkdir(parents=True, exist_ok=True)
    for instrument, stem in sorted(stems.items()):
        stem_name = f"{name}_{instrument}"
        write_pcm24(out / stem_name / f"{stem_name}.wav", stem * scale, sample_rate)
    write_pcm24(out / f"{name}_mix.wav", mix * scale, sample_rate)
    (out / "render.json").write_text(json.dumps({
        "name": name,
        "duration": duration,
        "sample_rate": sample_rate,
        "seed": int(spec.get("seed", 0)),
        "events": len(events),
        "peak_before_scaling": peak,
        "common_scale": scale,
        "stems": sorted(stems),
    }, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path, help="JSON event score")
    parser.add_argument("--out", required=True, type=Path, help="output directory")
    arguments = parser.parse_args()
    render(json.loads(arguments.spec.read_text()), arguments.out)


if __name__ == "__main__":
    main()
