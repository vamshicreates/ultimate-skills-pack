"""Music analysis: tempo, beat grid, downbeats, energy curve and the 'drop'."""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from .media import extract_wav


def analyze_music(path: str | Path, target_duration: float = 30.0, drop_at: float = 0.31) -> dict:
    import librosa  # heavy import, keep local

    with tempfile.TemporaryDirectory() as td:
        wav = extract_wav(path, Path(td) / "a.wav")
        y, sr = librosa.load(str(wav), sr=22050, mono=True)
    dur = len(y) / sr
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time", tightness=120)
    tempo = float(np.atleast_1d(tempo)[0])
    beats = np.asarray(beats, dtype=float)
    if len(beats) < 8:  # very ambient track: fall back to a fixed grid
        period = 60.0 / (tempo if tempo > 40 else 120.0)
        beats = np.arange(0.0, dur, period)
    env = librosa.onset.onset_strength(y=y, sr=sr)
    env_t = librosa.times_like(env, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    rms_t = librosa.times_like(rms, sr=sr)

    # Downbeat phase: the beat phase (0..3) whose beats carry the most onset energy.
    strength = np.interp(beats, env_t, env)
    phase = int(np.argmax([strength[k::4].mean() if len(strength[k::4]) else 0 for k in range(4)]))
    downbeats = beats[phase::4]

    # Energy curve (smoothed RMS, 2 Hz) and the biggest sustained rise = the drop.
    hop = rms_t[1] - rms_t[0] if len(rms_t) > 1 else 0.023
    win = max(1, int(1.0 / hop))
    smooth = np.convolve(rms, np.ones(win) / win, mode="same")
    # drop = biggest jump between the 3 s before and the 3 s after, ignoring the very start/end
    look = max(1, int(3.0 / hop))
    rise = np.full_like(smooth, -np.inf)
    cs = np.concatenate([[0.0], np.cumsum(smooth)])
    lo_i = max(look, int(0.12 * len(smooth)))
    hi_i = min(len(smooth) - look, int(0.88 * len(smooth)))
    for i in range(lo_i, hi_i):
        before = (cs[i] - cs[i - look]) / look
        after = (cs[i + look] - cs[i]) / look
        rise[i] = (after - before) / (before + 1e-4) * after
    drop_t = float(rms_t[int(np.argmax(rise))]) if np.isfinite(rise).any() else dur * 0.3
    # snap the drop to the nearest downbeat
    if len(downbeats):
        drop_t = float(downbeats[np.argmin(np.abs(downbeats - drop_t))])

    # Suggested music window: put the drop ~31% into a `target_duration` reel, starting on a downbeat.
    start = max(0.0, drop_t - drop_at * target_duration)
    if len(downbeats):
        cands = downbeats[downbeats <= start + 1e-6]
        start = float(cands[-1]) if len(cands) else float(downbeats[0])
    if start + target_duration > dur:
        start = max(0.0, dur - target_duration)

    return {
        "path": str(path),
        "duration": round(dur, 3),
        "tempo": round(tempo, 2),
        "beat_period": round(60.0 / tempo, 4) if tempo > 0 else None,
        "beats": [round(float(b), 3) for b in beats],
        "downbeats": [round(float(b), 3) for b in downbeats],
        "drop": round(drop_t, 3),
        "suggested_start": round(start, 3),
        "energy": {"t": [round(float(t), 2) for t in rms_t[::10]],
                   "rms": [round(float(v), 4) for v in smooth[::10]]},
    }


def beats_in_window(music: dict, start: float, duration: float) -> list[float]:
    return [round(b - start, 4) for b in music["beats"] if start - 1e-6 <= b <= start + duration + 1e-6]
