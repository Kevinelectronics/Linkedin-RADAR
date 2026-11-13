"""Radar de oportunidades (lunes): posts de config/people.json + búsquedas de contratación vía Apify.

Uso: python scripts/fetch_opps.py
Necesita APIFY_TOKEN. Guarda data/raw/opps-people-<fecha>.json y data/raw/opps-search-<fecha>.json
"""
import json, os, sys, datetime, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTOR = "harvestapi~linkedin-post-search"
TOKEN = os.environ.get("APIFY_TOKEN")
if not TOKEN and os.name == "nt":
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            TOKEN = winreg.QueryValueEx(k, "APIFY_TOKEN")[0]
    except OSError:
        pass
if not TOKEN:
    sys.exit("Falta APIFY_TOKEN en las variables de entorno.")

QUERIES = ["hiring technical writer", "looking for a technical writer", "freelance technical writer",
           "developer content writer", "looking for a content writer SaaS", "devrel content",
           "API documentation writer"]

def call(path, body=None):
    req = urllib.request.Request("https://api.apify.com/v2/" + path, method="POST" if body else "GET",
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)

def run(body):
    r = call(f"acts/{ACTOR}/runs?waitForFinish=300", body)["data"]
    while r["status"] in ("READY", "RUNNING"):
        r = call(f"actor-runs/{r['id']}?waitForFinish=60")["data"]
    return call(f"datasets/{r['defaultDatasetId']}/items?format=json")

def slim(p):
    e = p.get("engagement") or {}
    a = p.get("author") or {}
    return {"id": p.get("id"), "url": (p.get("linkedinUrl") or "").split("?")[0], "author": (a.get("name") or "").strip(),
            "authorUrl": a.get("linkedinUrl"), "headline": (a.get("info") or "")[:140],
            "likes": e.get("likes", 0), "comments": e.get("comments", 0),
            "date": ((p.get("postedAt") or {}).get("date") or "")[:10], "text": p.get("content") or "",
            "query": p.get("query") or (p.get("searchInput") or ""),
            "commentsList": [{"author": ((c.get("actor") or {}).get("name") or ""),
                              "headline": ((c.get("actor") or {}).get("position") or (c.get("actor") or {}).get("info") or "")[:120],
                              "text": (c.get("commentary") or c.get("content") or "")[:400]}
                             for c in (p.get("comments") or [])]}

day = datetime.date.today().isoformat()
os.makedirs(os.path.join(ROOT, "data", "raw"), exist_ok=True)
people = [x["url"] for x in json.load(open(os.path.join(ROOT, "config", "people.json"), encoding="utf-8"))["people"]]

jobs = [("people", {"authorUrls": people[i:i + 10], "maxPosts": 10, "postedLimit": "week", "sortBy": "date"})
        for i in range(0, len(people), 10)]
jobs += [("search:" + q, {"searchQueries": [q], "maxPosts": 30, "postedLimit": "week", "sortBy": "date"}) for q in QUERIES]

def work(job):
    tag, body = job
    try:
        items = run(body)
    except Exception as ex:
        print("ERROR", tag, ex)
        return tag, []
    out = [slim(p) for p in items if p.get("id")]
    for o in out:
        o["query"] = tag
    print(tag, len(out))
    return tag, out

with ThreadPoolExecutor(max_workers=5) as ex:
    results = list(ex.map(work, jobs))

ppl, srch, seen = [], [], set()
for tag, out in results:
    for o in out:
        if o["id"] in seen:
            continue
        seen.add(o["id"])
        (ppl if tag == "people" else srch).append(o)
json.dump(ppl, open(os.path.join(ROOT, "data", "raw", f"opps-people-{day}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(srch, open(os.path.join(ROOT, "data", "raw", f"opps-search-{day}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"people {len(ppl)} · search {len(srch)}")
