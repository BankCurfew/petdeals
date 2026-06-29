#!/usr/bin/env python3
"""Scrape Shopee Offer Pets page via Apify → filter real pet products → data/shopee-offers-raw.json"""
import json, os, time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ENV = os.path.expanduser("~/.oracle/secrets/shopee-affiliate.env")
creds = {}
for line in open(ENV):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip()

APIFY_TOKEN = creds.get("APIFY_API_TOKEN", "")
AFFILIATE_ID = creds.get("SHOPEE_AFFILIATE_ID", "an_15312860014")

SHOPEE_OFFER_URL = "https://shopee.co.th/m/offer-pets"

def run_apify_scrape():
    """Use Apify web scraper to fetch Shopee offers page."""
    url = "https://api.apify.com/v2/acts/apify~web-scraper/runs"
    body = json.dumps({
        "startUrls": [{"url": SHOPEE_OFFER_URL}],
        "pageFunction": """async function pageFunction(context) {
            const { page, request } = context;
            await page.waitForTimeout(5000);
            const products = await page.evaluate(() => {
                const items = [];
                document.querySelectorAll('[data-sqe="item"], .shopee-search-item-result__item, a[href*="-i."]').forEach((el, i) => {
                    if (i >= 50) return;
                    const link = el.querySelector('a[href*="-i."]') || el;
                    const href = link?.getAttribute('href') || '';
                    const match = href.match(/-i\\.(\\d+)\\.(\\d+)/);
                    if (!match) return;
                    const text = el.innerText || '';
                    const name = text.split('\\n').filter(l => l.length > 10 && !l.startsWith('฿'))[0] || '';
                    const priceMatch = text.match(/฿([\\d,.]+)/);
                    items.push({
                        shopId: match[1], itemId: match[2],
                        name: name.substring(0, 120),
                        price: priceMatch ? priceMatch[0] : '',
                        url: 'https://shopee.co.th' + href,
                    });
                });
                return items;
            });
            return products;
        }""",
        "proxyConfiguration": {"useApifyProxy": True},
        "maxRequestsPerCrawl": 3,
    }).encode()

    req = Request(f"{url}?token={APIFY_TOKEN}", data=body,
                  headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=30) as resp:
            run = json.loads(resp.read())
        run_id = run.get("data", {}).get("id")
        print(f"Apify run: {run_id}")
        return run_id
    except HTTPError as e:
        print(f"Apify error: {e.code} {e.read().decode()[:200]}")
        return None

def get_apify_results(run_id, max_wait=120):
    """Poll for Apify results."""
    for i in range(max_wait // 5):
        time.sleep(5)
        url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
        req = Request(url)
        with urlopen(req, timeout=10) as resp:
            status = json.loads(resp.read()).get("data", {}).get("status")
        if status in ("SUCCEEDED", "FAILED", "ABORTED"):
            print(f"Run {status} after {(i+1)*5}s")
            if status == "SUCCEEDED":
                dataset_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={APIFY_TOKEN}"
                with urlopen(Request(dataset_url), timeout=30) as resp:
                    return json.loads(resp.read())
            return []
    print("Timeout waiting for Apify")
    return []

def filter_pet_products(products):
    """Filter for real pet products with reasonable data."""
    pet_keywords = ["แมว", "สุนัข", "หมา", "cat", "dog", "pet", "อาหาร", "ทราย",
                     "ของเล่น", "สายจูง", "ที่นอน", "แชมพู", "กรง", "กระเป๋า"]
    filtered = []
    for p in products:
        name = (p.get("name", "") or "").lower()
        if any(k in name for k in pet_keywords):
            p["affiliate_url"] = f"{p['url']}?utm_source={AFFILIATE_ID}&utm_medium=affiliates&utm_campaign=petdeals&utm_content={p.get('itemId','')}"
            filtered.append(p)
    return filtered

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Shopee Offers Scrape: {today}")

    if not APIFY_TOKEN:
        print("ERROR: APIFY_API_TOKEN not set")
        return

    run_id = run_apify_scrape()
    if not run_id:
        print("Failed to start Apify run")
        return

    products = get_apify_results(run_id)
    all_products = []
    if isinstance(products, list):
        for batch in products:
            if isinstance(batch, list):
                all_products.extend(batch)
            elif isinstance(batch, dict):
                all_products.append(batch)

    print(f"Raw products: {len(all_products)}")
    filtered = filter_pet_products(all_products)
    print(f"Pet products: {len(filtered)}")

    outdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(outdir, exist_ok=True)

    raw_file = os.path.join(outdir, "shopee-offers-raw.json")
    with open(raw_file, "w") as f:
        json.dump({"scraped_at": datetime.now().isoformat(), "total": len(all_products), "products": all_products}, f, ensure_ascii=False, indent=2)
    print(f"Raw saved: {raw_file}")

    deals_file = os.path.join(outdir, "top-deals.json")
    with open(deals_file, "w") as f:
        json.dump({"updated_at": datetime.now().isoformat(), "total": len(filtered), "products": filtered}, f, ensure_ascii=False, indent=2)
    print(f"Deals saved: {deals_file}")

    for p in filtered[:5]:
        print(f"  {p.get('name','?')[:50]} | {p.get('price','?')}")

if __name__ == "__main__":
    main()
