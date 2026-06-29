#!/usr/bin/env python3
"""Sync top-deals.json — update affiliate links, merge new products, remove stale."""
import json, os
from datetime import datetime

ENV = os.path.expanduser("~/.oracle/secrets/shopee-affiliate.env")
creds = {}
for line in open(ENV):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip()

AFFILIATE_ID = creds.get("SHOPEE_AFFILIATE_ID", "an_15312860014")

def generate_affiliate_link(product_url, item_id, slug=""):
    content = slug or item_id
    return f"{product_url}?utm_source={AFFILIATE_ID}&utm_medium=affiliates&utm_campaign=petdeals&utm_content={content}"

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    datadir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    deals_file = os.path.join(datadir, "top-deals.json")
    if not os.path.exists(deals_file):
        print("No top-deals.json — run scrape-offers.py first")
        return

    with open(deals_file) as f:
        deals = json.load(f)

    products = deals.get("products", [])
    print(f"Products in top-deals: {len(products)}")

    updated = 0
    for p in products:
        url = p.get("url", "")
        item_id = p.get("itemId", "")
        if url and item_id:
            new_link = generate_affiliate_link(url, item_id)
            if p.get("affiliate_url") != new_link:
                p["affiliate_url"] = new_link
                updated += 1

    deals["updated_at"] = datetime.now().isoformat()
    deals["sync_date"] = today

    with open(deals_file, "w") as f:
        json.dump(deals, f, ensure_ascii=False, indent=2)

    print(f"Updated affiliate links: {updated}")
    print(f"Saved: {deals_file}")

    for p in products[:5]:
        print(f"  {p.get('name','?')[:50]} | {p.get('affiliate_url','?')[:60]}")

if __name__ == "__main__":
    main()
