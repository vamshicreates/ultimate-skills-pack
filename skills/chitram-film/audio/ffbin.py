"""Find an ffmpeg binary: $FFMPEG → PATH → imageio-ffmpeg's bundled build (pip install imageio-ffmpeg)."""
import os, shutil


def ffmpeg():
    p = os.environ.get("FFMPEG")
    if p and os.path.isfile(p): return p
    if p and os.path.isdir(p):          # seen on Windows: FFMPEG set to a folder
        for n in ("ffmpeg.exe", "ffmpeg", os.path.join("bin", "ffmpeg.exe"), os.path.join("bin", "ffmpeg")):
            if os.path.isfile(os.path.join(p, n)): return os.path.join(p, n)
    p = shutil.which("ffmpeg")
    if p: return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("ffmpeg not found: set FFMPEG, add ffmpeg to PATH, or pip install imageio-ffmpeg")
