#!/usr/bin/env python3
"""T094 — Shopee price-parity + dead-link audit for petzdeals.

Data source reality (probed 2026-07-15):
  - Direct Shopee item API  → HTTP 403 anti-bot
  - Firecrawl render        → Shopee login-wall
  - Apify actor fmKWN5uByUCIy2Sam is a DISCOVERY actor (keyword/shop/category
    search only). Single-product URLs are NOT supported; shopUrls get
    captcha-blocked. So per-itemId refresh is impossible — we refresh by
    running category KEYWORD searches (country=TH) and matching returned
    items to our catalog by itemId.

Pipeline:
  A. Fire Apify keyword runs (country=TH) for our catalog's categories.
  B. Collect + TH-validate every item (Brazil-gate: reject .com.br / non-Thai).
  C. Build itemId -> parity map (price, originalPrice, discountPercent, isOnSale).
  D. Update products.json parity fields in place (idempotent, keyed by itemId).
  E. Liveness first-pass on catalog items NOT seen in any scrape (HTTP + redirect).

Outputs:
  data/parity-<date>.json      — full parity dataset (every catalog product + status)
  data/dead-links-<date>.json  — dead-listing candidates for swap

Usage: python3 scripts/parity-audit.py [--max=120] [--live]  (--live writes products.json)
"""
import json, os, re, sys, time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_PATH = os.path.join(BASE, "data", "products.json")
DATA_DIR = os.path.join(BASE, "data")
ENV = os.path.expanduser("~/.oracle/secrets/shopee-affiliate.env")
ACTOR_ID = "fmKWN5uByUCIy2Sam"
DATE = datetime.now().strftime("%Y-%m-%d")

MAX_ITEMS = int(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--max=")), "120"))
LIVE = "--live" in sys.argv

creds = {}
for line in open(ENV):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip()
TOKEN = creds.get("APIFY_API_TOKEN", "")

# Search keywords derived from our actual catalog categories
KEYWORDS = [
    "อาหารแมว", "ขนมแมว", "อาหารเปียกแมว", "ทรายแมว",
    "อาหารสุนัข", "ขนมสุนัข", "อาหารเสริมสัตว์เลี้ยง",
    "เครื่องให้อาหารสัตว์", "ของเล่นแมว", "คอนโดแมว", "น้ำพุแมว",
]

THAI_RE = re.compile(r"[ก-๛]")
REJECT_DOMAINS = ["shopee.com.br", "shopee.com.mx", "shopee.com.co", "shopee.sg"]


def is_thai_item(it):
    """Brazil-gate: item must be Thai (shopee.co.th + Thai title)."""
    url = (it.get("url") or "")
    name = (it.get("name") or "")
    if any(d in url for d in REJECT_DOMAINS):
        return False
    if url and "shopee.co.th" not in url and ".co.th" not in url:
        return False
    return bool(THAI_RE.search(name))


def api_post(path, body):
    req = Request(f"https://api.apify.com/v2/{path}?token={TOKEN}",
                  data=json.dumps(body).encode(),
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def api_get(path):
    with urlopen(Request(f"https://api.apify.com/v2/{path}?token={TOKEN}"), timeout=30) as r:
        return json.loads(r.read())


def scrape_keywords():
    """Fire all keyword runs, poll, collect TH-valid items -> itemId map."""
    runs = {}
    for kw in KEYWORDS:
        try:
            rid = api_post(f"acts/{ACTOR_ID}/runs",
                           {"keywords": [kw], "country": "TH", "maxItems": MAX_ITEMS})["data"]["id"]
            runs[kw] = rid
            print(f"  fired '{kw}' -> {rid}")
        except Exception as e:
            print(f"  ERROR firing '{kw}': {e}")
        time.sleep(1)

    parity = {}   # itemId -> parity record
    raw_all = 0
    rejected = 0
    cost = 0.0
    for kw, rid in runs.items():
        status = "RUNNING"
        for _ in range(40):  # up to ~10 min per run
            time.sleep(15)
            d = api_get(f"actor-runs/{rid}")["data"]
            status = d["status"]
            if status in ("SUCCEEDED", "FAILED", "ABORTED"):
                cost += float(d.get("usageTotalUsd") or 0)
                break
        if status != "SUCCEEDED":
            print(f"  '{kw}' ended {status}")
            continue
        items = api_get(f"actor-runs/{rid}/dataset/items")
        kept = 0
        for it in items:
            if "warning" in it:
                continue
            raw_all += 1
            if not is_thai_item(it):
                rejected += 1
                continue
            iid = str(it.get("itemId", ""))
            if not iid:
                continue
            parity[iid] = {
                "itemId": iid,
                "shopId": str(it.get("shopId", "")),
                "price": it.get("price"),
                "originalPrice": it.get("originalPrice"),
                "discountPercent": it.get("discountPercent") or 0,
                "isOnSale": bool(it.get("isOnSale")),
                "sold": it.get("historicalSoldEstimated"),
                "name": it.get("name", ""),
                "seenVia": kw,
            }
            kept += 1
        print(f"  '{kw}' {status}: {len(items)} items, {kept} TH-kept")
    print(f"\nScrape totals: {len(parity)} unique TH products | raw {raw_all} | rejected(non-TH) {rejected} | cost ~${cost:.3f}")
    return parity, rejected, cost


def http_liveness(url):
    """First-pass liveness. IMPORTANT: Shopee product pages are a pure JS SPA —
    a live AND a dead listing both return HTTP 200 with an identical empty shell
    (no og:tags, no product name server-side; data loads via the 403-blocked API).
    So a 200-that-stays-on-the-product-URL is INCONCLUSIVE, not proof of life.
    Only a redirect to /search|homepage or a 404 is a reliable DEAD signal.
    200-stay -> 'unconfirmed' (must be verified by CDP render pass).
    Returns (status, detail). status in {dead, unconfirmed, blocked, unknown}."""
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/150"})
        resp = urlopen(req, timeout=8)
        final = resp.url
        if final.rstrip("/") == "https://shopee.co.th" or "/search" in final:
            return "dead", f"redirect->{final[:60]}"
        return "unconfirmed", f"200-shell {final[:50]}"  # SPA shell — needs render
    except HTTPError as e:
        if e.code in (403, 429):
            return "blocked", f"HTTP {e.code} (anti-bot)"
        if e.code == 404:
            return "dead", "HTTP 404"
        return "unknown", f"HTTP {e.code}"
    except (URLError, Exception) as e:
        return "unknown", str(e)[:50]


def main():
    if not TOKEN:
        print("ERROR: APIFY_API_TOKEN missing")
        return
    products = json.load(open(PRODUCTS_PATH))
    print(f"Catalog: {len(products)} products\n=== Phase A/B/C: keyword discovery scrape (maxItems={MAX_ITEMS}) ===")
    parity, rejected, cost = scrape_keywords()

    # Phase D: match + update parity
    matched, updated = 0, []
    dataset = []
    unmatched = []
    for p in products:
        iid = str(p.get("itemId", ""))
        rec = parity.get(iid)
        entry = {
            "itemId": iid, "slug": p.get("slug", ""), "title": p.get("title", ""),
            "shopId": str(p.get("shopId", "")), "url": p.get("url", ""),
            "old_price": p.get("price"), "old_discount": p.get("discountPercent"),
        }
        if rec:
            matched += 1
            new_price = f"฿{rec['price']:,.0f}" if isinstance(rec["price"], (int, float)) else str(rec["price"])
            orig = rec["originalPrice"]
            new_orig = f"฿{orig:,.0f}" if isinstance(orig, (int, float)) and orig and orig > (rec["price"] or 0) else ""
            entry.update({
                "status": "alive", "source": "apify-keyword",
                "price": new_price, "originalPrice": new_orig,
                "discountPercent": int(rec["discountPercent"] or 0),
                "isOnSale": rec["isOnSale"], "sold": rec["sold"],
            })
            if LIVE:
                p["price"] = new_price
                p["priceMax"] = new_orig
                p["price_before_discount"] = new_orig
                p["discountPercent"] = int(rec["discountPercent"] or 0)
                p["isOnSale"] = rec["isOnSale"]
                p["parityCheckedAt"] = DATE
                p["listingAlive"] = True
            updated.append(iid)
        else:
            unmatched.append(p)
            entry.update({"status": "unmatched-pending-liveness", "source": None})
        dataset.append(entry)

    print(f"\n=== Phase D: matched {matched}/{len(products)} ({100*matched//len(products)}%) refreshed from live scrape ===")

    # Phase E: liveness first-pass on unmatched (HTTP)
    print(f"=== Phase E: HTTP liveness first-pass on {len(unmatched)} unmatched ===")
    live_stats = {"unconfirmed": 0, "dead": 0, "blocked": 0, "unknown": 0}
    dead_links = []
    for i, p in enumerate(unmatched):
        st, detail = http_liveness(p.get("url", ""))
        live_stats[st] += 1
        for e in dataset:
            if e["itemId"] == str(p.get("itemId", "")):
                e["status"] = f"unmatched-{st}"
                e["liveness"] = detail
                if LIVE:
                    p["listingAlive"] = (st != "dead")
                    p["parityCheckedAt"] = DATE
                break
        if st == "dead":
            dead_links.append({"itemId": str(p.get("itemId", "")), "slug": p.get("slug", ""),
                               "title": p.get("title", ""), "url": p.get("url", ""), "reason": detail})
        if (i + 1) % 50 == 0:
            print(f"  liveness {i+1}/{len(unmatched)} — {live_stats}")
        time.sleep(0.25)
    print(f"  liveness done: {live_stats}")

    # Write outputs
    parity_out = os.path.join(DATA_DIR, f"parity-{DATE}.json")
    dead_out = os.path.join(DATA_DIR, f"dead-links-{DATE}.json")
    json.dump({"date": DATE, "catalog": len(products), "matched_live": matched,
               "scrape_cost_usd": round(cost, 3), "rejected_non_th": rejected,
               "liveness": live_stats, "products": dataset},
              open(parity_out, "w"), ensure_ascii=False, indent=2)
    json.dump({"date": DATE, "count": len(dead_links), "note": "HTTP first-pass; blocked items need CDP logged-in pass",
               "dead_links": dead_links},
              open(dead_out, "w"), ensure_ascii=False, indent=2)

    if LIVE:
        json.dump(products, open(PRODUCTS_PATH, "w"), ensure_ascii=False, indent=2)
        print("  products.json UPDATED (--live)")

    print(f"\n=== DONE ===\nParity dataset: {parity_out}\nDead-link list: {dead_out} ({len(dead_links)} hard-dead)")
    print(f"Liveness: {matched} ALIVE-confirmed (seen in live scrape); "
          f"{live_stats['dead']} DEAD (redirect/404); "
          f"{live_stats['unconfirmed']} unconfirmed 200-shell (need CDP render pass); "
          f"{live_stats['blocked']} blocked; {live_stats['unknown']} unknown")


if __name__ == "__main__":
    main()
