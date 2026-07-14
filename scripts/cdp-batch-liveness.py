#!/usr/bin/env python3
"""T094 Part 2 — reliable dead-link pass via CDP render over unmatched products.

Reads data/parity-<date>.json, takes every product NOT already confirmed alive
by the live scrape (status != 'alive'), renders each in the logged-in :9222
Chrome, and classifies alive/dead. Writes the authoritative dead-link list.

HTTP can't judge Shopee liveness (SPA 200-shell) — only rendered DOM can.

Usage: python3 scripts/cdp-batch-liveness.py [--date=YYYY-MM-DD] [--limit=N] [--live]
"""
import json, os, sys, time
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
from cdp_liveness import cdp_check

DATE = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--date=")), datetime.now().strftime("%Y-%m-%d"))
LIMIT = int(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--limit=")), "100000"))
LIVE = "--live" in sys.argv

parity_path = os.path.join(BASE, "data", f"parity-{DATE}.json")
products_path = os.path.join(BASE, "data", "products.json")
data = json.load(open(parity_path))
todo = [e for e in data["products"] if e.get("status") != "alive"][:LIMIT]
print(f"CDP liveness over {len(todo)} not-yet-alive products (of {data['catalog']})")

stats = {"alive": 0, "dead": 0, "login_wall": 0, "unknown": 0, "error": 0}
dead = []
by_id = {e["itemId"]: e for e in data["products"]}
for i, e in enumerate(todo):
    st, detail = cdp_check(e["url"])
    stats[st] = stats.get(st, 0) + 1
    by_id[e["itemId"]]["status"] = f"cdp-{st}"
    by_id[e["itemId"]]["cdp_detail"] = detail
    if st == "dead":
        dead.append({"itemId": e["itemId"], "slug": e["slug"], "title": e["title"],
                     "url": e["url"], "reason": detail})
    if (i + 1) % 25 == 0:
        print(f"  {i+1}/{len(todo)} — {stats}")
    time.sleep(0.3)

print(f"\nCDP done: {stats}")
# merge with any HTTP-caught dead from the parity run
dead_path = os.path.join(BASE, "data", f"dead-links-{DATE}.json")
existing = {}
if os.path.exists(dead_path):
    for d in json.load(open(dead_path)).get("dead_links", []):
        existing[d["itemId"]] = d
for d in dead:
    existing[d["itemId"]] = d
dead_all = list(existing.values())
json.dump({"date": DATE, "count": len(dead_all), "method": "CDP render (logged-in :9222) + HTTP redirect",
           "cdp_stats": stats, "dead_links": dead_all},
          open(dead_path, "w"), ensure_ascii=False, indent=2)
json.dump(data, open(parity_path, "w"), ensure_ascii=False, indent=2)
print(f"Wrote {dead_path}: {len(dead_all)} dead links")

if LIVE:
    prods = json.load(open(products_path))
    deadids = {d["itemId"] for d in dead_all}
    for p in prods:
        if str(p.get("itemId", "")) in deadids:
            p["listingAlive"] = False
            p["parityCheckedAt"] = DATE
    json.dump(prods, open(products_path, "w"), ensure_ascii=False, indent=2)
    print(f"products.json: flagged {len(deadids)} dead listingAlive=False")
