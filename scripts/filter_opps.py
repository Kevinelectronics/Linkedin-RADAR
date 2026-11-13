"""Prefiltra data/raw/opps-search-<fecha>.json: quita buscadores de empleo, autopromoción y agregadores.
Uso: python scripts/filter_opps.py [fecha]  -> data/raw/opps-candidates-<fecha>.json"""
import json, os, re, sys, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
day = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
posts = json.load(open(os.path.join(ROOT, "data", "raw", f"opps-search-{day}.json"), encoding="utf-8"))
old = set(json.load(open(os.path.join(ROOT, "data", "seen-opps.json")))) if os.path.exists(os.path.join(ROOT, "data", "seen-opps.json")) else set()
SEEK = re.compile(r"open to work|#opentowork|seeking (a |new )?(role|opportunit|position)|i'?m (currently )?(looking for|seeking) (a |new |my next )|available for (freelance|new|work|projects)|estou em busca|busco (empleo|trabajo)|hire me|dm me if you need a writer|i help (saas|b2b|companies|brands)|my services|job ?alert|jobs? (of the week|roundup)|\d+ (freelance )?(writing )?(gigs|jobs)", re.I)
HIRE = re.compile(r"\bhiring\b|we'?re looking for|we are looking for|looking for (a|an) (freelance |contract |experienced |senior )?(technical|content|developer|devrel|api|docs?|tech)|seeking (a|an) (freelance |contract )?(technical|content)|join (our|the) team|open (role|position)|contrata|buscamos|apply|send (me )?(your )?(portfolio|samples)|drop (your|a) (portfolio|comment)|recommend(ations)? (for )?a (technical|content) writer|anyone know a (good )?(technical|content) writer", re.I)
TOPIC = re.compile(r"technical writ|content writ|developer content|devrel|developer relations|documentation|docs\b|api|sdk|developer advocate|copywriter", re.I)
out = []
for p in posts:
    t = p["text"]
    if not t or p["id"] in old: continue
    if SEEK.search(t[:600]): continue
    if not (HIRE.search(t) and TOPIC.search(t)): continue
    if p["date"] and p["date"] < (datetime.date.fromisoformat(day) - datetime.timedelta(days=8)).isoformat(): continue
    out.append(p)
json.dump(out, open(os.path.join(ROOT, "data", "raw", f"opps-candidates-{day}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(posts), "->", len(out))
