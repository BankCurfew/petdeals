#!/usr/bin/env python3
"""Daily Apify sync — scrape Thai pet products via correct actor fmKWN5uByUCIy2Sam
Params: keywords=[], country="TH" (uppercase), maxItems>=10
"""
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
ACTOR_ID = "fmKWN5uByUCIy2Sam"
PRODUCTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "products.json")

DAILY_SEARCHES = [
    (["อาหารแมว"], "", "อาหารแมว", 20),
    (["อาหารเปียกแมว"], "", "อาหารเปียก", 15),
    (["ขนมแมว"], "", "ขนมแมว", 15),
    (["ทรายแมว"], "", "ทรายแมว", 15),
    (["อาหารสุนัข"], "", "อาหารสุนัข", 15),
]

def run_actor(keywords, max_items):
    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}"
    body = json.dumps({
        "keywords": keywords,
        "maxItems": max(max_items, 10),
        "country": "TH",
    }).encode()
    req = Request(url, data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read()).get("data", {}).get("id")

def wait_results(run_id, max_wait=120):
    for i in range(max_wait // 5):
        time.sleep(5)
        url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
        with urlopen(Request(url), timeout=10) as resp:
            status = json.loads(resp.read()).get("data", {}).get("status")
        if status == "SUCCEEDED":
            ds = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={APIFY_TOKEN}"
            with urlopen(Request(ds), timeout=30) as resp:
                return json.loads(resp.read())
        elif status in ("FAILED", "ABORTED"):
            return []
    return []

def main():
    if not APIFY_TOKEN:
        print("ERROR: APIFY_API_TOKEN not set")
        return

    with open(PRODUCTS_PATH) as f:
        existing = json.load(f)
    products = existing if isinstance(existing, list) else existing.get("products", [])
    existing_ids = {str(p.get("itemId", "")) for p in products}
    print(f"Existing: {len(products)} products")

    all_new = []
    for keywords, brand, category, max_items in DAILY_SEARCHES:
        print(f"\n=== {keywords[0]} (max={max_items}) ===")
        try:
            run_id = run_actor(keywords, max_items)
            if not run_id:
                print("  No run ID")
                continue
            print(f"  Run: {run_id}")
            results = wait_results(run_id)
            print(f"  Results: {len(results)}")

            new_count = 0
            for item in results:
                if "error" in item:
                    continue
                item_id = str(item.get("itemId", ""))
                if not item_id or item_id in existing_ids:
                    continue
                existing_ids.add(item_id)
                title = item.get("name", "")
                if not title or len(title) < 5:
                    continue

                shop_id = str(item.get("shopId", ""))
                price = item.get("price", "")
                if isinstance(price, (int, float)):
                    price = f"฿{price:,.0f}"
                orig = item.get("originalPrice", "")
                if isinstance(orig, (int, float)) and orig > 0:
                    orig = f"฿{orig:,.0f}"

                url = item.get("url", f"https://shopee.co.th/product-i.{shop_id}.{item_id}")

                all_new.append({
                    "shopId": shop_id,
                    "itemId": item_id,
                    "title": title[:150],
                    "price": str(price),
                    "priceMax": str(orig) if orig else "",
                    "rating": str(item.get("rating", "")),
                    "reviewCount": str(item.get("reviewCount", "")),
                    "sold": str(item.get("historicalSoldEstimated", "")),
                    "brand": brand,
                    "category": category,
                    "images": (item.get("images") or [])[:5],
                    "url": url,
                    "affiliateUrl": f"{url}?utm_source={AFFILIATE_ID}&utm_medium=affiliates&utm_campaign=petdeals&utm_content={item_id}",
                    "scrapedAt": datetime.now().strftime("%Y-%m-%d"),
                })
                new_count += 1
            print(f"  New: {new_count}")
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(2)

    products.extend(all_new)
    output = products if isinstance(existing, list) else {**existing, "products": products}
    with open(PRODUCTS_PATH, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n=== DONE ===")
    print(f"New: {len(all_new)} | Total: {len(products)}")

if __name__ == "__main__":
    main()
