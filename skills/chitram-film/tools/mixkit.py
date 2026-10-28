"""Mixkit (mixkit.co) free SFX + stock music: list a category page, download by exact title.
Licence: Mixkit Sound Effects Free License / Stock Music Free License — free in commercial and social
videos, no attribution required, but not re-distributable as standalone audio. Log every file.

    python tools/mixkit.py list free-sound-effects/whoosh/            # titles, durations, urls
    python tools/mixkit.py list free-stock-music/tag/hip-hop/
    python tools/mixkit.py get free-sound-effects/transition/ "Movie trailer whoosh hit" assets/sfx/whoosh_hit.mp3

Good pages: free-sound-effects/{whoosh,swoosh,transition,pop,click,impact,glitch,cinematic}/ ·
free-stock-music/tag/{hip-hop,cinematic,electronic,lo-fi,corporate,trap}/
Tested picks: "Cinematic whoosh fast transition", "Arrow whoosh", "Fast whoosh transition", "Magic sparkle
whoosh", "Explainer video pops whoosh light pop", "Metal hit woosh", "Epic movie trailer whoosh impact",
"Cool impact movie trailer", "Movie trailer whoosh hit", "Technology transition slide", "Pulsating bass
transition", "Hard pop click", "Bubble pop up alert notification", "Long pop"; music "Thunder" (dark trap,
83 bpm, quiet build then a hard drop at 20.15 s — perfect for "reveal" edits), "Need for speed" (136 bpm).
NOTE: the title of a card comes AFTER its audio url in the HTML — this parser pairs them correctly.
"""
import html, json, os, re, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}


def page(path):
    return urllib.request.urlopen(urllib.request.Request("https://mixkit.co/" + path.lstrip("/"), headers=UA), timeout=60).read().decode("utf-8", "ignore")


def items(path):
    s = page(path)
    ms = list(re.finditer(r'data-audio-player-preview-url-value="([^"]+)"', s))
    out = []
    for k, m in enumerate(ms):
        end = ms[k + 1].start() if k + 1 < len(ms) else m.end() + 4000
        seg = s[m.end():end]
        t = re.findall(r"<h2[^>]*>\s*([^<]+?)\s*</h2>", seg)
        d = re.findall(r"(\d+:\d\d)", seg)
        if t: out.append((html.unescape(t[0]).strip(), d[0] if d else "?", m.group(1)))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "list":
        for t, d, u in items(sys.argv[2]): print(f"{t:45s} {d:>6s}  {u}")
    elif sys.argv[1] == "get":
        path, title, dst = sys.argv[2], sys.argv[3], sys.argv[4]
        hit = [x for x in items(path) if x[0].lower() == title.lower()]
        if not hit: raise SystemExit(f"not found on {path}: {title}")
        data = urllib.request.urlopen(urllib.request.Request(hit[0][2], headers=UA), timeout=120).read()
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True); open(dst, "wb").write(data)
        log = os.path.join(os.path.dirname(dst) or ".", "MIXKIT_SOURCES.json")
        j = json.load(open(log)) if os.path.exists(log) else {}
        j[dst] = {"title": hit[0][0], "url": hit[0][2], "license": "Mixkit Free License"}
        json.dump(j, open(log, "w"), indent=1); print("ok", dst, len(data))
