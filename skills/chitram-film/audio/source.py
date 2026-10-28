"""source.py: the self-sourcing sound system. The skill ships NO audio: every SFX, bed and music track is
found on the internet for the job, licence-checked, downloaded into the film's folder, measured and indexed,
then used by role/stack (SOUND.md) or fitted to the cut (MUSIC.md).

  python audio/source.py kit cinematic --to films/<n>/assets/sfx --lib <n>   a full SFX kit for a style
        profiles: cinematic · viral · tech · musicvideo · trailer · ui · nature   (python audio/source.py kits)
  python audio/source.py sfx "metal impact" --to films/<n>/assets/sfx --lib <n> [--n 4] [--max 8]
  python audio/source.py music "dark cinematic trailer" --to films/<n>/assets/music [--bpm 128] [--mood dark|bright]
                              [--min 30] [--n 6] [--vocals no]     -> downloads, analyses, ranks -> candidates.md
  python audio/source.py trends [--region India] [--niche "AI creator"]   the live trend-research protocol

Sources (all keyless): Openverse API (Freesound SFX, Jamendo + Wikimedia music), Mixkit (SFX + music).
Optional keys widen the net: FREESOUND_API_KEY (full Freesound), PIXABAY_KEY (Pixabay music/SFX).
Licence rule: only licences that allow COMMERCIAL use AND MODIFICATION (cutting music to picture is a
modification): CC0, PDM, CC BY, CC BY-SA, Mixkit Free License, Pixabay Content License. NC and ND are
rejected automatically. Every file is logged with title, author, licence and URL in <to>/CREDITS.txt;
CC BY / BY-SA need the credit line in the caption or description.
Trending Instagram/TikTok songs are NOT downloadable or bakeable: research them (trends), then the creator
adds them in-app (MUSIC.md §4).
"""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
UA = {"User-Agent": "Mozilla/5.0 (chitram-film sound sourcing)"}
OK_LIC = {"cc0", "pdm", "by", "by-sa", "mixkit", "pixabay"}


def opt(a, name, default=None, cast=str):
    return cast(a[a.index(name) + 1]) if name in a and a.index(name) + 1 < len(a) else default


def get_json(url, headers=None, tries=3):
    for k in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}),
                                                     timeout=40).read().decode("utf-8"))
        except Exception as e:
            if k == tries - 1: print("  ! request failed:", url[:90], e); return {}
            time.sleep(2 + 3 * k)


# ------------------------------------------------------------------ providers
def openverse(q, n=8, source="freesound", max_dur=None, min_dur=None):
    url = ("https://api.openverse.org/v1/audio/?" + urllib.parse.urlencode(
        {"q": q, "page_size": min(20, max(n * 3, 10)), "license_type": "commercial,modification", "source": source}))
    out = []
    for r in get_json(url).get("results", []):
        d = (r.get("duration") or 0) / 1000
        if r.get("license") not in OK_LIC: continue
        if max_dur and d and d > max_dur: continue
        if min_dur and d and d < min_dur: continue
        out.append({"title": r["title"], "url": r["url"], "license": "CC " + r["license"].upper() if r["license"] != "cc0" else "CC0",
                    "lic": r["license"], "author": r.get("creator") or "", "page": r.get("foreign_landing_url") or "",
                    "duration": round(d, 2), "provider": f"openverse/{source}", "genres": r.get("genres") or []})
    return out[:n]


def freesound(q, n=8, max_dur=None, min_dur=None):
    key = os.environ.get("FREESOUND_API_KEY")
    if not key: return []
    flt = "license:(\"Creative Commons 0\" OR \"Attribution\")"
    if max_dur or min_dur: flt += f" duration:[{min_dur or 0} TO {max_dur or 600}]"
    url = ("https://freesound.org/apiv2/search/text/?" + urllib.parse.urlencode(
        {"query": q, "filter": flt, "fields": "name,previews,license,username,url,duration", "page_size": n, "token": key}))
    return [{"title": r["name"], "url": r["previews"]["preview-hq-mp3"], "license": r["license"].split("/")[-3].upper(),
             "lic": "cc0" if "zero" in r["license"] else "by", "author": r["username"], "page": r["url"],
             "duration": r["duration"], "provider": "freesound"} for r in get_json(url).get("results", [])]


def pixabay(q, n=8, kind="music"):
    key = os.environ.get("PIXABAY_KEY")
    if not key: return []
    url = "https://pixabay.com/api/audio/?" + urllib.parse.urlencode({"key": key, "q": q, "per_page": n, "category": kind})
    return [{"title": r.get("title") or q, "url": r.get("audio") or r.get("url"), "license": "Pixabay Content License",
             "lic": "pixabay", "author": r.get("user", ""), "page": r.get("pageURL", ""), "duration": r.get("duration", 0),
             "provider": "pixabay"} for r in get_json(url).get("hits", [])]


MIXKIT_SFX = {  # query word -> Mixkit category pages
    "whoosh": ["whoosh", "transition"], "swoosh": ["swoosh", "whoosh"], "transition": ["transition"],
    "impact": ["impact", "cinematic"], "hit": ["impact", "cinematic"], "boom": ["cinematic", "explosion"],
    "riser": ["cinematic", "transition"], "pop": ["pop"], "click": ["click"], "glitch": ["glitch"],
    "cinematic": ["cinematic"], "trailer": ["cinematic"], "camera": ["camera"], "shutter": ["camera"],
    "magic": ["magic"], "sparkle": ["magic"], "notification": ["notification"], "bass": ["cinematic", "transition"],
    "typing": ["keyboard"], "crowd": ["crowd"], "applause": ["applause"], "explosion": ["explosion"],
}
MIXKIT_MUSIC = ["cinematic", "hip-hop", "electronic", "lo-fi", "corporate", "trap", "ambient", "pop", "rock",
                "dance", "chill", "dramatic", "epic", "funk", "house", "jazz", "piano", "sad", "happy", "upbeat"]


def mixkit(q, n=8, kind="sfx"):
    try:
        sys.path.insert(0, os.path.join(SKILL, "tools")); import mixkit as MK
    except Exception:
        return []
    words = [w for w in re.split(r"\W+", q.lower()) if w]
    if kind == "sfx":
        pages = [f"free-sound-effects/{c}/" for w in words for c in MIXKIT_SFX.get(w, [])] or ["free-sound-effects/cinematic/"]
    else:
        tags = [w for w in words if w in MIXKIT_MUSIC] or ["cinematic"]
        pages = [f"free-stock-music/tag/{t}/" for t in tags]
    out, seen = [], set()
    for p in dict.fromkeys(pages):
        try:
            for title, dur, url in MK.items(p):
                if url in seen: continue
                seen.add(url)
                mm, ss = (dur.split(":") + ["0"])[:2] if ":" in dur else ("0", "0")
                d = int(mm) * 60 + int(ss) if mm.isdigit() and ss.isdigit() else 0
                score = sum(w in title.lower() for w in words)
                out.append({"title": title, "url": url, "license": "Mixkit Free License", "lic": "mixkit",
                            "author": "Mixkit", "page": "https://mixkit.co/" + p, "duration": d,
                            "provider": "mixkit", "_s": score})
        except Exception as e:
            print("  ! mixkit", p, e)
    out.sort(key=lambda r: -r["_s"])
    return out[:n]


# ------------------------------------------------------------------ download + credits
def slug(s, k=48):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:k] or "sound"


def download(item, to, prefix=""):
    os.makedirs(to, exist_ok=True)
    ext = os.path.splitext(urllib.parse.urlparse(item["url"]).path)[1] or ".mp3"
    dst = os.path.join(to, f"{prefix}{slug(item['title'])}{ext}")
    if not os.path.exists(dst):
        try:
            data = urllib.request.urlopen(urllib.request.Request(item["url"], headers=UA), timeout=120).read()
        except Exception as e:
            print("  ! download failed", item["title"], e); return None
        open(dst, "wb").write(data)
    cred = os.path.join(to, "CREDITS.txt")
    line = f"{os.path.basename(dst)} | \"{item['title']}\" by {item['author'] or 'unknown'} | {item['license']} | {item['page'] or item['url']}\n"
    old = open(cred, encoding="utf-8").read() if os.path.exists(cred) else ""
    if os.path.basename(dst) not in old:
        open(cred, "a", encoding="utf-8").write(line)
    item["file"] = dst
    return dst


def search_sfx(q, n=4, max_dur=8):
    res = freesound(q, n, max_dur) + openverse(q, n * 2, "freesound", max_dur) + mixkit(q, n, "sfx")
    seen, out = set(), []
    for r in res:
        k = slug(r["title"])
        if k in seen or not r.get("url"): continue
        seen.add(k); out.append(r)
    return out


# ------------------------------------------------------------------ kits: role -> queries
KITS = {
    "cinematic": {"whoosh": ["cinematic whoosh", "fast whoosh transition"], "impact": ["cinematic impact hit", "deep impact"],
                  "boom": ["cinematic boom", "trailer boom"], "riser": ["cinematic riser", "reverse riser"],
                  "sub": ["sub drop", "bass drop impact"], "shimmer": ["magic sparkle shimmer"], "glitch": ["glitch transition"]},
    "trailer": {"braam": ["braam", "trailer horn hit"], "impact": ["trailer hit", "metal impact"], "boom": ["trailer boom", "deep boom"],
                "riser": ["trailer riser", "tension riser"], "whoosh": ["trailer whoosh"], "sub": ["sub drop"], "tick": ["clock tick tension"]},
    "viral": {"whoosh": ["fast whoosh", "swoosh transition"], "pop": ["pop", "bubble pop"], "click": ["click", "mouse click"],
              "shutter": ["camera shutter"], "bass": ["bass drop", "808 hit"], "scratch": ["record scratch"], "ding": ["notification ding"]},
    "tech": {"ui": ["ui interface beep", "technology transition"], "click": ["click", "keyboard typing"], "whoosh": ["digital whoosh", "tech transition"],
             "glitch": ["glitch", "digital glitch"], "data": ["data processing computer"], "ding": ["success notification"]},
    "musicvideo": {"whoosh": ["whoosh transition", "reverse cymbal"], "impact": ["impact hit", "drum hit"], "riser": ["riser", "uplifter"],
                   "sub": ["sub drop", "808"], "shimmer": ["shimmer sparkle"], "vinyl": ["vinyl crackle", "tape stop"], "crowd": ["crowd cheer"]},
    "ui": {"click": ["ui click", "button click"], "pop": ["pop up", "notification pop"], "swoosh": ["swoosh"], "ding": ["success chime"],
           "type": ["keyboard typing"]},
    "nature": {"wind": ["wind ambience"], "rain": ["rain ambience"], "birds": ["birds morning"], "water": ["water stream"],
               "fire": ["fire crackle"], "night": ["night crickets"]},
}


def index_lib(to, lib):
    subprocess.run([sys.executable, os.path.join(HERE, "sfx_lib.py"), "index", to, "--name", lib], check=False)
    print(f"\nindexed '{lib}': use role:/stack: cues as usual (SOUND.md), e.g. python audio/sfx_lib.py roles")


def cmd_kit(a):
    prof, to, lib = a[0], opt(a, "--to"), opt(a, "--lib", "film")
    n = opt(a, "--n", 3, int)
    if prof not in KITS: raise SystemExit(f"profiles: {', '.join(KITS)}")
    got, taken = 0, set()
    for role, qs in KITS[prof].items():
        picked = []
        for q in qs:
            for r in search_sfx(q, n + 2, 10 if prof != "nature" else 60):
                if len(picked) >= n: break
                if r["url"] in taken: continue                   # one file, one role
                if download(r, to, f"{role}_"): picked.append(r["title"]); taken.add(r["url"])
            if len(picked) >= n: break
        print(f"  {role:<9} {len(picked)}  {', '.join(p[:28] for p in picked)}"); got += len(picked)
    print(f"{got} sounds -> {to} (licences in CREDITS.txt)")
    index_lib(to, lib)


def cmd_sfx(a):
    q, to, lib = a[0], opt(a, "--to"), opt(a, "--lib", "film")
    res = search_sfx(q, opt(a, "--n", 4, int), opt(a, "--max", 8, float))[:opt(a, "--n", 4, int)]
    for r in res:
        if download(r, to, slug(q, 16) + "_"): print(f"  + {r['title'][:40]:<40} {r['duration']:6.1f}s  {r['license']:<22} {r['provider']}")
    index_lib(to, lib)


MOOD = {"dark": ("minor", -1), "tense": ("minor", -1), "sad": ("minor", -1), "epic": (None, 0), "bright": ("major", 1),
        "happy": ("major", 1), "uplifting": ("major", 1), "chill": (None, 0), "hype": (None, 0)}


def cmd_music(a):
    q, to = a[0], opt(a, "--to")
    n = opt(a, "--n", 6, int); bpm = opt(a, "--bpm", None, float); mood = opt(a, "--mood")
    mind = opt(a, "--min", 20, float)
    cands = (pixabay(q, n) + openverse(q, n, "jamendo", None, mind) + mixkit(q, n, "music") +
             openverse(q, max(2, n // 2), "wikimedia_audio", None, mind))
    seen, pool = set(), []
    for r in cands:
        k = slug(r["title"])
        if k not in seen: seen.add(k); pool.append(r)
    pool = pool[:n * 2]
    import music as MU
    rows = []
    for r in pool[:n + 2]:
        f = download(r, to, "m_")
        if not f: continue
        try:
            A = MU.analyse(f)
        except Exception as e:
            print("  ! analyse failed", r["title"], e); continue
        s = 0.0; why = []
        if bpm:
            import math
            oct = min(abs(math.log2(A["bpm"] / bpm)), abs(math.log2(A["bpm"] * 2 / bpm)), abs(math.log2(A["bpm"] / 2 / bpm)))
            s += 3 * max(0, 1 - oct / .25); why.append(f"tempo {A['bpm']}")
        if mood in MOOD and MOOD[mood][0]:
            s += 1.5 if A["mode"] == MOOD[mood][0] else 0; why.append(A["mode"])
        s += min(2.0, A["drop_jump_db"] / 5); why.append(f"drop +{A['drop_jump_db']} dB")
        s += 1.0 if A["duration"] >= mind else 0
        s += .5 * len(A.get("drops", []))
        rows.append((round(s, 2), r, A, ", ".join(why)))
        json.dump(A, open(os.path.splitext(f)[0] + ".music.json", "w"), indent=1)
        try: MU.sheet([os.path.splitext(f)[0] + ".music.json"])
        except Exception: pass
    rows.sort(key=lambda x: -x[0])
    md = [f"# Music candidates for \"{q}\"" + (f" ~{bpm:g} BPM" if bpm else "") + (f", {mood}" if mood else ""), "",
          "| rank | score | track | BPM | key | length | drops | licence | sheet |", "|---|---|---|---|---|---|---|---|---|"]
    for i, (s, r, A, why) in enumerate(rows, 1):
        md.append(f"| {i} | {s} | {r['title'][:40]} ({r['provider']}) | {A['bpm']} | {A['key']} {A['mode']} | {A['duration']:.0f}s | "
                  f"{[d['t'] for d in A.get('drops', [])]} | {r['license']} | {os.path.basename(os.path.splitext(r['file'])[0])}_music.png |")
    md += ["", "Read each sheet PNG, check the licence fits the platform, then:",
           "`python audio/music.py fit <file> --duration <film> --drop-at <reveal> --out assets/music_fit.wav`",
           "Check vocals by ear/description: under a voiceover use instrumental only."]
    out = os.path.join(to, "candidates.md"); open(out, "w", encoding="utf-8").write("\n".join(md))
    print("\n".join(md[:len(rows) + 4])); print("->", out)


def cmd_trends(a):
    region = opt(a, "--region", "India"); niche = opt(a, "--niche", "creator")
    y = time.strftime("%Y"); m = time.strftime("%B")
    qs = [f"Instagram Reels trending audio this week {m} {y}",
          f"trending reels songs {region} {m} {y}",
          f"TikTok trending sounds this week {m} {y} (Instagram follows 1-2 weeks later)",
          f"trending Telugu reels songs {m} {y}" if region.lower() in ("india", "telugu", "andhra", "telangana") else f"trending {region} reels songs {m} {y}",
          f"viral {niche} reels audio {m} {y}",
          f"phonk / velocity edit trending sound {m} {y}"]
    print("TREND RESEARCH PROTOCOL (run these as WebSearch, newest sources first; trends decay in days):")
    for q in qs: print("  -", q)
    print("""Then record in brief.md: sound name + artist, why it fits the concept, its stage (rising/peak/decay),
which section creators use (start time), its BPM/mood if known, and whether the account type can use it.
Deliverables for a trending sound: the video WITHOUT it + "add <sound> in-app, start at m:ss, music 30 %".
For a baked version, find a licensed track with the same feel: source.py music "<genre mood>" --bpm <same>.""")


def cmd_kits(a):
    for k, v in KITS.items(): print(f"{k:<11} roles: {', '.join(v)}")


if __name__ == "__main__":
    cmds = {"kit": cmd_kit, "kits": cmd_kits, "sfx": cmd_sfx, "music": cmd_music, "trends": cmd_trends}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__); sys.exit(1)
    cmds[sys.argv[1]](sys.argv[2:])
