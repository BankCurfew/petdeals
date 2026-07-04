#!/usr/bin/env python3
"""Daily Apify sync — scrape Thai pet products via correct actor fmKWN5uByUCIy2Sam
Params: keywords=[], country="TH" (uppercase), maxItems>=10

Validation gate: rejects non-Thai items (shopee.com.br URLs, non-Thai titles).
Emits slug + source at ingest so products render in Astro build.
"""
import json, os, re, sys, time, unicodedata
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

REJECTED_DOMAINS = ["shopee.com.br", "shopee.com.mx", "shopee.com.co", "shopee.sg"]
THAI_CHAR_RE = re.compile(r"[ก-ฺเ-๎]")

CAT_KEYWORDS = re.compile(r"แมว|cat|kitten|catnip|แคทนิป|มาทาทาบิ|ลับเล็บ|ฝนเล็บ|ขูดเล็บ|คอนโด|ไม้ตกแมว|ไม้ล่อแมว|อุโมงค์แมว|teaser", re.IGNORECASE)
DOG_KEYWORDS = re.compile(r"สุนัข|หมา|dog|puppy", re.IGNORECASE)

CATEGORY_REMAP = {
    "ลับเล็บ": "ลับเล็บแมว",
    "คอนโด": "คอนโดแมว",
    "อุโมงค์": "ของเล่นแมว",
}


def has_thai(text):
    return bool(THAI_CHAR_RE.search(text))


def correct_category(title, assigned_category):
    """Fix category when title keywords contradict the assigned search category."""
    has_cat = bool(CAT_KEYWORDS.search(title))
    has_dog = bool(DOG_KEYWORDS.search(title))

    if "สุนัข" in assigned_category and has_cat and not has_dog:
        for keyword, cat in CATEGORY_REMAP.items():
            if keyword in title:
                return cat
        return "ของเล่นแมว"

    if "แมว" in assigned_category and has_dog and not has_cat:
        return "อาหารสุนัข"

    return assigned_category


def is_valid_th_product(item):
    """Validation gate: reject non-Thai items. Returns (ok, reason)."""
    title = item.get("name", "") or ""
    url = item.get("url", "") or ""

    for domain in REJECTED_DOMAINS:
        if domain in url:
            return False, f"REJECTED: non-TH URL ({domain})"

    if not has_thai(title):
        return False, f"REJECTED: non-Thai title: {title[:40]}"

    return True, "OK"


def generate_slug(title, item_id, existing_slugs):
    """Generate URL-safe slug from title. Uses English tokens + itemId suffix for uniqueness."""
    ascii_parts = re.findall(r"[a-zA-Z0-9]+", title)
    if ascii_parts:
        base = "-".join(ascii_parts[:6]).lower()
    else:
        base = "product"

    slug = f"{base}-{item_id[-6:]}"
    slug = re.sub(r"-+", "-", slug).strip("-")[:80]

    if slug in existing_slugs:
        slug = f"{slug}-{item_id[-4:]}"

    return slug


def make_affiliate_url(shop_id, item_id):
    """Generate Shopee affiliate URL with proper tracking params."""
    base = f"https://shopee.co.th/product/{shop_id}/{item_id}"
    return f"{base}?utm_source={AFFILIATE_ID}&utm_medium=affiliates&utm_campaign=petdeals&utm_content={item_id}"


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
    existing_slugs = {p.get("slug", "") for p in products if p.get("slug")}
    print(f"Existing: {len(products)} products")

    all_new = []
    rejected_count = 0
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

                ok, reason = is_valid_th_product(item)
                if not ok:
                    print(f"  !! {reason}")
                    rejected_count += 1
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

                slug = generate_slug(title, item_id, existing_slugs)
                existing_slugs.add(slug)

                product_url = f"https://shopee.co.th/product/{shop_id}/{item_id}"

                all_new.append({
                    "shopId": shop_id,
                    "itemId": item_id,
                    "title": title[:150],
                    "slug": slug,
                    "source": "apify-daily-sync",
                    "price": str(price),
                    "priceMax": str(orig) if orig else "",
                    "rating": str(item.get("rating", "")),
                    "reviewCount": str(item.get("reviewCount", "")),
                    "sold": str(item.get("historicalSoldEstimated", "")),
                    "brand": brand,
                    "category": correct_category(title, category),
                    "images": (item.get("images") or [])[:5],
                    "url": product_url,
                    "affiliateUrl": make_affiliate_url(shop_id, item_id),
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
    print(f"New: {len(all_new)} | Rejected: {rejected_count} | Total: {len(products)}")

    if rejected_count > 0:
        print(f"\n!! ALERT: {rejected_count} non-TH items rejected by validation gate")


if __name__ == "__main__":
    main()
