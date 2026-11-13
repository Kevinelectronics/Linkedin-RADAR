"""Recoge lanzamientos recientes de SaaS / dev tools para el radar (pestaña «Lanzamientos»).

  python scripts/fetch_launches.py            # escribe data/raw/launches-YYYY-MM-DD.json y lo imprime resumido

Fuentes gratis:
  1. Product Hunt: feed RSS del día (https://www.producthunt.com/feed).
  2. Hacker News: «Show HN» de los últimos 2 días con 15+ puntos (API de Algolia).
  3. Changelogs/blogs de config/launch_watchlist.json: busca su RSS (o lee los títulos de la página) y solo devuelve
     entradas que no estaban en data/launches_seen.json (la primera vez solo guarda lo que hay, sin devolverlo).
LinkedIn no va aquí: la tarea busca en Clay al fundador/maker de cada lanzamiento bueno (suele anunciarlo en LinkedIn).
No filtra ni puntúa: eso lo hace la tarea (encaje para un vídeo demo de función).
"""
import datetime as dt, hashlib, html, json, os, re, sys, time
from urllib.parse import urljoin
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"}
SEEN = os.path.join(ROOT, "data", "launches_seen.json")
TODAY = dt.date.today().isoformat()


def get(url, **kw):
    return requests.get(url, headers=UA, timeout=25, **kw)


def strip(s):
    s = s or ""
    for _ in range(3):  # el feed de Product Hunt viene escapado varias veces
        s = html.unescape(s)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def rss_items(xml):
    out = []
    for block in re.findall(r"<(?:item|entry)\b.*?</(?:item|entry)>", xml, re.S):
        t = re.search(r"<title[^>]*>(.*?)</title>", block, re.S)
        l = re.search(r"<link[^>]*href=\"([^\"]+)\"", block) or re.search(r"<link>(.*?)</link>", block, re.S)
        d = re.search(r"<(?:pubDate|published|updated)>(.*?)</", block, re.S)
        s = re.search(r"<(?:description|summary|content)[^>]*>(.*?)</(?:description|summary|content)>", block, re.S)
        if t and l:
            out.append({"title": strip(t.group(1).replace("<![CDATA[", "").replace("]]>", "")),
                        "url": strip(l.group(1)), "date": strip(d.group(1)) if d else "",
                        "summary": strip((s.group(1) if s else "").replace("<![CDATA[", "").replace("]]>", ""))[:400]})
    return out


def product_hunt():
    try:
        items = rss_items(get("https://www.producthunt.com/feed").text)
    except Exception as e:
        return [], f"Product Hunt: {e}"
    return [{"source": "producthunt", "company": i["title"], "title": i["title"], "summary": i["summary"].split(" Discuss")[0].split(" | ")[0],
             "url": i["url"], "date": i["date"]} for i in items[:40]], None


def show_hn():
    since = int(time.time()) - 2 * 86400
    try:
        r = get("https://hn.algolia.com/api/v1/search_by_date",
                params={"tags": "show_hn", "numericFilters": f"points>=15,created_at_i>{since}", "hitsPerPage": 40}).json()
    except Exception as e:
        return [], f"Hacker News: {e}"
    out = []
    for h in r.get("hits", []):
        out.append({"source": "hackernews", "company": re.sub(r"^Show HN:\s*", "", h.get("title", "")).split(" – ")[0].split(" - ")[0][:60],
                    "title": h.get("title", ""), "summary": "", "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
                    "hn": f"https://news.ycombinator.com/item?id={h['objectID']}", "points": h.get("points"), "date": h.get("created_at", "")[:10]})
    return out, None


def watchlist(seen):
    cfg = json.load(open(os.path.join(ROOT, "config", "launch_watchlist.json"), encoding="utf-8"))
    out, errs = [], []
    for c in cfg["companies"]:
        key = c["company"]
        try:
            page = get(c["url"])
            items = []
            m = re.search(r"<link[^>]+type=\"application/(?:rss|atom)\+xml\"[^>]*href=\"([^\"]+)\"", page.text) or \
                re.search(r"<link[^>]+href=\"([^\"]+)\"[^>]*type=\"application/(?:rss|atom)\+xml\"", page.text)
            if m:
                items = rss_items(get(urljoin(c["url"], html.unescape(m.group(1)))).text)
            if not items:  # sin RSS: títulos de la página con su enlace
                for href, txt in re.findall(r"<a[^>]+href=\"([^\"#]+)\"[^>]*>\s*(?:<[^>]+>\s*)*([^<]{12,140})<", page.text):
                    if re.search(r"(changelog|blog|post|news|release|update)", href, re.I):
                        items.append({"title": strip(txt), "url": urljoin(c["url"], href), "date": "", "summary": ""})
            items = items[:15]
        except Exception as e:
            errs.append(f"{key}: {str(e)[:80]}")
            continue
        old = set(seen.get(key, []))
        first_time = key not in seen
        ids = [hashlib.md5(i["url"].encode()).hexdigest()[:12] for i in items]
        for i, h in zip(items, ids):
            if not first_time and h not in old:
                out.append({"source": "changelog", "company": key, "title": i["title"], "summary": i["summary"],
                            "url": i["url"], "date": i["date"], "why": c.get("why", "")})
        seen[key] = list(dict.fromkeys(ids + list(old)))[:200]
    return out, errs


if __name__ == "__main__":
    seen = json.load(open(SEEN, encoding="utf-8")) if os.path.exists(SEEN) else {}
    res, errors = [], []
    for fn in (product_hunt, show_hn):
        items, err = fn()
        res += items
        if err: errors.append(err)
    items, errs = watchlist(seen)
    res += items; errors += errs
    json.dump(seen, open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out = os.path.join(ROOT, "data", "raw", f"launches-{TODAY}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"date": TODAY, "items": res, "errors": errors}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    by = {}
    for r in res: by[r["source"]] = by.get(r["source"], 0) + 1
    print(out, by, "errores:", len(errors))
    for e in errors: print("  !", e)
