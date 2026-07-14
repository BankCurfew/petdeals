#!/usr/bin/env python3
"""T094 Part 3 — replace UTM links with real Shopee affiliate feed links.

Current products.json links are UTM-pattern (utm_source=an_...) which do NOT
track through Shopee = ZERO commission (SOP-AFFILIATE-LINKS.md). The fix:
match each product by shopId+itemId against the Shopee Affiliate Product Feed
CSV and use its `affiliate_link` column (an s.shopee.co.th redirect that tracks
commission). Researcher verdict 2026-07-15: feed link is final format; optionally
append &sub_id=petdeals-{slug} for our own conversion attribution (does NOT affect
commission).

Usage:
  python3 scripts/match-affiliate-links.py --feed /tmp/shopee-feed.csv [--subid] [--live]

Feed CSV is expected to have (Shopee standard headers, auto-detected):
  itemid / item_id, shopid / shop_id, product_link / offer_link, affiliate_link / short_link
Outputs:
  data/affiliate-map-<date>.json   — {itemId: {affiliate_link, matched, sub_id_link}}
  (with --live) rewrites products.json affiliateUrl
"""
import csv, json, os, sys, io, gzip
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE = datetime.now().strftime("%Y-%m-%d")
FEED = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--feed=")), "")
SUBID = "--subid" in sys.argv
LIVE = "--live" in sys.argv

ITEM_KEYS = ["itemid", "item_id", "itemId", "item id"]
SHOP_KEYS = ["shopid", "shop_id", "shopId", "shop id"]
AFF_KEYS = ["affiliate_link", "short_link", "offer_link", "affiliatelink", "shortlink"]


def pick(row, keys):
    for k in keys:
        for rk in row:
            if rk and rk.strip().lower() == k.lower():
                return row[rk]
    return None


def load_feed(path):
    opener = gzip.open if path.endswith(".gz") else open
    feed = {}
    with opener(path, "rt", encoding="utf-8", errors="ignore") as f:
        # sniff delimiter
        sample = f.read(4096); f.seek(0)
        delim = "\t" if sample.count("\t") > sample.count(",") else ","
        reader = csv.DictReader(f, delimiter=delim)
        for row in reader:
            iid = pick(row, ITEM_KEYS)
            aff = pick(row, AFF_KEYS)
            if iid and aff:
                feed[str(iid).strip()] = aff.strip()
    return feed


def main():
    if not FEED or not os.path.exists(FEED):
        print(f"ERROR: feed CSV not found: {FEED}\n(pull it from affiliate.shopee.co.th/creative/product_feed via CDP first)")
        sys.exit(1)
    feed = load_feed(FEED)
    print(f"Feed: {len(feed):,} products with affiliate_link")
    products = json.load(open(os.path.join(BASE, "data", "products.json")))
    mapping = {}
    matched = 0
    for p in products:
        iid = str(p.get("itemId", ""))
        aff = feed.get(iid)
        if aff:
            matched += 1
            link = aff
            if SUBID and p.get("slug"):
                sep = "&" if "?" in link else "?"
                link = f"{link}{sep}sub_id=petdeals-{p['slug']}"
            mapping[iid] = {"affiliate_link": aff, "sub_id_link": link if SUBID else None,
                            "slug": p.get("slug", ""), "matched": True}
            if LIVE:
                p["affiliateUrl"] = link
                p["affiliate_ok"] = True
                p["affiliateSource"] = "shopee-feed"
                p["affiliateUpdatedAt"] = DATE
        else:
            mapping[iid] = {"affiliate_link": None, "matched": False, "slug": p.get("slug", "")}
    out = os.path.join(BASE, "data", f"affiliate-map-{DATE}.json")
    json.dump({"date": DATE, "catalog": len(products), "matched": matched,
               "unmatched": len(products) - matched, "sub_id_appended": SUBID,
               "feed_size": len(feed), "map": mapping},
              open(out, "w"), ensure_ascii=False, indent=2)
    print(f"Matched {matched}/{len(products)} ({100*matched//len(products)}%) -> {out}")
    if LIVE:
        json.dump(products, open(os.path.join(BASE, "data", "products.json"), "w"), ensure_ascii=False, indent=2)
        print(f"products.json: {matched} affiliateUrl replaced with feed links (affiliate_ok=True)")
    else:
        print("[dry-run — pass --live to rewrite products.json]")


if __name__ == "__main__":
    main()
