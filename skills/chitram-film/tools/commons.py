"""Wikimedia Commons: search and fetch free images / audio WITH licence logging.

    python tools/commons.py search "chess knight piece" [n] [--audio]
    python tools/commons.py get "File:Name.jpg" assets/raw/name.jpg [width] [--credits assets/CREDITS.txt]
    python tools/commons.py original "File:Sound.ogg" assets/sfx/sound.ogg      # full file (audio/video)

Rules: prefer Public domain / CC0 / CC BY; CC BY-SA and CC BY need a credit line in the caption.
Every download appends "<path> <title> <licence> <url>" to the credits file. Audio files must be
fetched with `original` (thumbnail URLs of audio are tiny placeholders).
"""
import sys, json, time, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "ChitramFilm/1.0 (educational motion design; python urllib)"}
API = "https://commons.wikimedia.org/w/api.php?"


def call(params):
    for i in range(5):
        try:
            req = urllib.request.Request(API + urllib.parse.urlencode(params), headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            time.sleep(2 + i * 2)
    raise SystemExit("api failed (retry, or shorten the query)")


def search(q, n=8, audio=False):
    d = call(dict(action="query", format="json", generator="search", gsrnamespace=6, gsrlimit=n,
                  gsrsearch=q + (" filetype:audio" if audio else " filetype:bitmap"), prop="imageinfo",
                  iiprop="size|extmetadata", iiextmetadatafilter="LicenseShortName"))
    for p in d.get("query", {}).get("pages", {}).values():
        ii = p["imageinfo"][0]
        lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "?")
        dur = f' | {round(ii.get("duration", 0) or 0, 1)}s' if audio else ""
        print(f'{p["title"]} | {ii.get("width")}x{ii.get("height")} | {lic}{dur}')


def fetch(title, out, width=None, credits="assets/CREDITS.txt"):
    params = dict(action="query", format="json", titles=title, prop="imageinfo", iiprop="url|extmetadata",
                  iiextmetadatafilter="LicenseShortName|Artist")
    if width: params["iiurlwidth"] = width
    p = list(call(params)["query"]["pages"].values())[0]
    ii = p["imageinfo"][0]
    url = (ii.get("thumburl") if width else None) or ii["url"]
    for i in range(5):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read(); break
        except Exception:
            time.sleep(3 + i * 3)
    open(out, "wb").write(data)
    lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "?")
    with open(credits, "a", encoding="utf-8") as f:
        f.write(f"{out}\t{title}\t{lic}\thttps://commons.wikimedia.org/wiki/{urllib.parse.quote(title)}\n")
    print("ok", out, len(data), lic)


if __name__ == "__main__":
    a = sys.argv[1:]
    cred = "assets/CREDITS.txt"
    if "--credits" in a: k = a.index("--credits"); cred = a[k + 1]; del a[k:k + 2]
    if a[0] == "search":
        search(a[1], int(a[2]) if len(a) > 2 and a[2].isdigit() else 8, "--audio" in a)
    elif a[0] == "get":
        fetch(a[1], a[2], int(a[3]) if len(a) > 3 else 1600, cred)
    elif a[0] == "original":
        fetch(a[1], a[2], None, cred)
