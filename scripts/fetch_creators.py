"""Trae los posts recientes de los creadores de config/creators.json vía Apify.

Uso: python scripts/fetch_creators.py [week|month]
Necesita la variable de entorno APIFY_TOKEN. Guarda data/raw/creators-<fecha>.json
y solo devuelve posts que no se hayan visto antes (data/seen.json).
"""
import json, os, sys, datetime, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTOR = "harvestapi~linkedin-post-search"
TOKEN = os.environ.get("APIFY_TOKEN")
if not TOKEN:
    sys.exit("Falta APIFY_TOKEN en las variables de entorno.")

def call(path, body=None):
    req = urllib.request.Request("https://api.apify.com/v2/" + path, method="POST" if body else "GET",
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=330) as r:
        return json.load(r)

def fmt(p):
    v = json.dumps(p.get("postVideo") or {})
    if p.get("document"): return "carrusel"
    if "playlist/vid" in v: return "vídeo"
    if p.get("postImages") or "media.licdn" in v: return "imagen"
    return "texto"

limit = sys.argv[1] if len(sys.argv) > 1 else "week"
creators = json.load(open(os.path.join(ROOT, "config", "creators.json"), encoding="utf-8"))["creators"]
urls = [c["url"] for c in creators]
posts = []
for i in range(0, len(urls), 10):
    run = call(f"acts/{ACTOR}/runs?waitForFinish=300",
               {"authorUrls": urls[i:i + 10], "maxPosts": 15, "postedLimit": limit, "sortBy": "date"})["data"]
    posts += call(f"datasets/{run['defaultDatasetId']}/items?format=json")

seen_path = os.path.join(ROOT, "data", "seen.json")
seen = set(json.load(open(seen_path))) if os.path.exists(seen_path) else set()
out = []
for p in posts:
    e = p.get("engagement") or {}
    a = p.get("author") or {}
    out.append({"id": p["id"], "url": p["linkedinUrl"].split("?")[0], "author": a.get("name", "").strip(),
                "headline": (a.get("info") or "")[:90], "likes": e.get("likes", 0), "comments": e.get("comments", 0),
                "shares": e.get("shares", 0), "date": p["postedAt"]["date"][:10], "format": fmt(p),
                "text": p.get("content") or "", "images": [im["url"] for im in (p.get("postImages") or [])],
                "new": p["id"] not in seen})
out.sort(key=lambda x: -(x["likes"] + 3 * x["comments"] + 2 * x["shares"]))
os.makedirs(os.path.join(ROOT, "data", "raw"), exist_ok=True)
day = datetime.date.today().isoformat()
json.dump(out, open(os.path.join(ROOT, "data", "raw", f"creators-{day}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(sorted(seen | {p["id"] for p in out}), open(seen_path, "w"))
print(f"{len(out)} posts ({sum(p['new'] for p in out)} nuevos) -> data/raw/creators-{day}.json")
