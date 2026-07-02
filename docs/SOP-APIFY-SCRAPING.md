# SOP: Apify Scraping — Product Data Collection

## Overview

PetzDeals uses Apify to scrape product data from Shopee Thailand. This SOP covers which actor to use, how to run scrapes, and fallback methods.

## Credentials

```bash
# Stored in ~/.oracle/secrets/shopee-affiliate.env
# APIFY_API_TOKEN=***  (see vault)
# APIFY_USER_ID=***  (see vault)
```

## Working Actor

| Field | Value |
|---|---|
| **Actor ID** | `fmKWN5uByUCIy2Sam` |
| **Version** | 0.4.9 |
| **Total runs** | 16+ (all SUCCEEDED) |
| **Plan** | Apify Starter ($49/mo) |

**This is the ONLY actor that works with Shopee Thailand.** Generic actors (shopee-scraper, web-scraper) get 403 Forbidden.

## Method 1: Apify Actor (Primary)

### Run via API

```bash
export APIFY_TOKEN=$(grep APIFY_API_TOKEN ~/.oracle/secrets/shopee-affiliate.env | cut -d= -f2)

# Start a run
curl -X POST "https://api.apify.com/v2/acts/fmKWN5uByUCIy2Sam/runs?token=$APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "searchTerms": ["Royal Canin อาหารแมว", "Hill'\''s Science Diet แมว"],
    "maxItems": 20,
    "country": "TH"
  }'

# Check run status
curl -s "https://api.apify.com/v2/actor-runs/{RUN_ID}?token=$APIFY_TOKEN"

# Get results
curl -s "https://api.apify.com/v2/actor-runs/{RUN_ID}/dataset/items?token=$APIFY_TOKEN"
```

### Run via Apify Console

1. Go to https://console.apify.com
2. Find actor `fmKWN5uByUCIy2Sam`
3. Set search terms + maxItems
4. Click Run
5. Download results as JSON

### Expected Output Fields

```json
{
  "title": "Royal Canin Indoor 4kg",
  "price": 850,
  "originalPrice": 950,
  "rating": 4.9,
  "reviewCount": 15000,
  "sold": "50000+",
  "images": ["https://cf.shopee.com.br/file/..."],
  "shopId": 76673436,
  "itemId": 1420780700,
  "shopName": "Royal Canin Official",
  "url": "https://shopee.co.th/...",
  "category": "อาหารแมว"
}
```

## Method 2: CDP Scraping (Fallback)

When Apify gets blocked or rate-limited, use Chrome DevTools Protocol connected to the real Chrome browser (port 9222).

### Prerequisites

- Chrome running on Windows with `--remote-debugging-port=9222`
- Logged into Shopee in Chrome
- WSL can reach localhost:9222

### Step-by-Step

```python
import asyncio, json, websockets, http.client

# 1. Open new tab with Shopee search
conn = http.client.HTTPConnection("localhost", 9222)
keyword = "Royal+Canin+อาหารแมว"
conn.request("PUT", f"/json/new?https://shopee.co.th/search?keyword={keyword}")
resp = conn.getresponse()
tab_id = json.loads(resp.read())["id"]

# 2. Wait for page load
await asyncio.sleep(5)

# 3. Connect and extract products
uri = f"ws://localhost:9222/devtools/page/{tab_id}"
async with websockets.connect(uri, max_size=10*1024*1024) as ws:
    js = """
    (function() {
        const items = [];
        // Extract from Shopee search results DOM
        document.querySelectorAll('[data-sqe="item"]').forEach(el => {
            const title = el.querySelector('[class*="name"]')?.textContent || '';
            const price = el.querySelector('[class*="price"]')?.textContent || '';
            const img = el.querySelector('img')?.src || '';
            const link = el.querySelector('a')?.href || '';
            if (title) items.push({title, price, image: img, url: link});
        });
        return JSON.stringify(items);
    })()
    """
    await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": js}}))
    resp = json.loads(await ws.recv())
    products = json.loads(resp["result"]["result"]["value"])

# 4. Close tab
conn.request("PUT", f"/json/close/{tab_id}")
conn.getresponse()
```

### CDP Tips

- **Fresh tab per search** — don't reuse tabs, they go stale
- **Wait 5s** after opening tab before extracting
- **max_size=10*1024*1024** on websocket connection
- **Close tabs** after use — too many open = Chrome slows down
- Shopee search results load via JavaScript — need to wait for DOM render

## Method 3: Product Feed CSV (Bulk)

For massive product lists, use the Shopee Affiliate Product Feed (1M+ products daily).

1. Log into affiliate.shopee.co.th → Creative → Product Feed
2. Click "View Link" → copy CSV download URL
3. Download: `curl -L "$URL" -b "$COOKIES" -o feed.csv`
4. Match by shopId + itemId
5. Feed has `product_short link` column = affiliate link

**Limitation**: Feed only includes products with rating >1 and stock >0.

## After Scraping — Processing Pipeline

For EVERY new product scraped:

### 1. Generate Affiliate Link

```python
# Via Custom Link page (CDP)
# Batch 5 URLs at a time
# Navigate to affiliate.shopee.co.th/offer/custom_link
# Input URLs → click Get Link → read modal textarea
# Result: s.shopee.co.th/XXXXX
```

### 2. Download Image as WEBP

```bash
# Download + convert
curl -sL -o /tmp/product.jpg "$IMAGE_URL"
convert /tmp/product.jpg -resize 200x200 -quality 75 public/products/$SLUG.webp
```

### 3. Add to products.json

```python
# APPEND to existing products — never overwrite
with open('data/products.json') as f:
    products = json.load(f)
products.append({
    "title": "...",
    "price": 850,
    "priceMax": 950,  # if available
    "rating": 4.9,
    "reviewCount": 15000,
    "sold": "50000+",
    "images": ["https://..."],
    "localImage": "/products/slug.webp",
    "affiliateUrl": "https://s.shopee.co.th/XXXXX",
    "slug": "royal-canin-indoor-4kg",
    "brand": "Royal Canin",
    "category": "อาหารแมว",
    "shopId": "76673436",
    "itemId": "1420780700",
    "url": "https://shopee.co.th/...",
    "scrapedAt": "2026-06-30"
})
```

### 4. Build + Deploy

```bash
npx astro build
CLOUDFLARE_API_TOKEN=... npx wrangler pages deploy dist --project-name=petzdeals
```

### 5. GSC Submit (for new category pages)

```python
# Resubmit sitemap + URL inspection
# See SOP-SEO-TAGS.md "New Page Checklist"
```

## Scraping Schedule

| Time | What | Method | Oracle |
|---|---|---|---|
| 02:00 daily | Shopee Offer Pets page | CDP or Apify | Data |
| Weekly Mon | New brand products | Apify actor fmKWN5uByUCIy2Sam | Data |
| On demand | Missing brands/categories | CDP fallback | Data |

## Common Issues

| Issue | Cause | Fix |
|---|---|---|
| Apify 403 Forbidden | Wrong actor or IP blocked | Use actor fmKWN5uByUCIy2Sam or switch to CDP |
| CDP tab returns 500 | Tab crashed or stale | Close tab, open fresh one |
| Shopee CDN images don't load on site | Hotlink protection | Download locally as WEBP |
| Affiliate link not s.shopee.co.th | Skipped Custom Link step | Re-generate via affiliate portal |
| products.json overwritten | Used write instead of append | Always load → append → save |

## CAR/PAR

### CAR #1 — Wrong Actor (2026-06-30)
**Issue**: Data used wrong Apify actors (shopee-scraper, web-scraper) → 403 Forbidden on all 13 searches.
**Root Cause**: No documentation of which Apify actor works.
**Fix**: Documented working actor ID + CDP fallback.

### CAR #2 — BRAZIL DATA DISASTER (2026-06-30)
**Issue**: Apify actor fmKWN5uByUCIy2Sam scraped **Shopee BRAZIL** (shopee.com.br) instead of Thailand (shopee.co.th). 231 products were Brazilian furniture, underwear, floor wax — NOT pet products. Portuguese titles ("Armário De Armazenamento", "Calcinha para Senhora", "Cera Acrílica") were deployed to petzdeals.com.
**Root Cause**: Actor fmKWN5uByUCIy2Sam defaults to Brazil market. The `location=Thailand` parameter was not sufficient or incorrect.
**Impact**: 231 fake products on live site for ~12 hours. Products had no images, wrong language, wrong category. แบงค์ found it.
**Fix**: Removed all 231 Brazilian products. Reverted to original 109 Thai products. Hidden 10 empty categories.
**Date**: 2026-06-30

### CAR #3 — No Data Validation (2026-06-30)
**Issue**: 231 products were committed without ANY validation that titles were Thai or products were pet-related.
**Root Cause**: No validation step in the scraping pipeline. Data blindly appended Apify results.
**Fix**: Added validation rules below.

### PAR (Preventive Action Report)
1. **Actor fmKWN5uByUCIy2Sam scrapes BRAZIL by default** — DO NOT USE for Thailand without verified country parameter
2. **VALIDATE BEFORE COMMIT**: Every scraped product MUST have Thai characters (฀-๿) in the title. If title is Portuguese/English with no Thai → REJECT
3. **Spot-check 5 products manually** before batch import — open URLs, verify they're Thai Shopee pages
4. **Use CDP for Thailand** — connect to Chrome logged into shopee.co.th, scrape search results directly. This guarantees Thai products
5. **Never commit >20 products without review** — batch imports need BoB approval
6. **Test with 1 search first** — verify country/language before running 13 searches
7. **Product title language check** (automated):
   ```python
   import re
   thai_re = re.compile(r'[฀-๿]')
   for p in new_products:
       if not thai_re.search(p['title']):
           raise ValueError(f"Non-Thai product: {p['title'][:50]}")
   ```
8. **CAR for every data incident** — document what went wrong, why, and prevention

### CAR #4 — Country Parameter Case-Sensitivity (2026-07-01)
**Issue**: Apify actor requires `"country": "TH"` (uppercase). Using `"th"` (lowercase) was rejected with error. Previous runs defaulted to Brazil because no country was specified.
**Root Cause**: Actor fmKWN5uByUCIy2Sam defaults to `"BR"` (Brazil) when country parameter is omitted or lowercase. Allowed values: `"BR", "ID", "TH", "MY", "SG", "PH", "VN", "MX"`.
**Fix**: Always specify `"country": "TH"` (uppercase) in Apify input JSON. Also `"maxItems"` must be >= 10.
**Correct input format**:
```json
{
  "keywords": ["อาหารแมว", "ของเล่นแมว"],
  "maxItems": 20,
  "country": "TH"
}
```
**Wrong**: `"country": "th"` (rejected), `"country"` omitted (defaults to Brazil), `"maxItems": 5` (rejected, min 10)

### PAR Addition
9. **ALWAYS specify `"country": "TH"`** in every Apify run — NEVER omit, NEVER lowercase
10. **`maxItems` minimum 10** — lower values are rejected by the actor

### CAR #5 — itemCount Stats Show 0 But Dataset Has Items (2026-07-02)
**Issue**: All Apify runs showed `itemCount: 0` in stats, leading team to believe scraper was broken. Wasted 24+ hours trying to fix (different builds, keywords, CDP fallback). Actually the dataset DID have items — stats were just wrong.
**Root Cause**: Actor's `stats.itemCount` counter doesn't update properly on Starter plan. The actual dataset contains products. Must check `dataset/items` endpoint directly, NOT rely on `stats.itemCount`.
**Impact**: 24 hours of wasted debugging. Tried build 0.4.9 vs 0.4.11, Thai vs English keywords, single vs batch, CDP fallback — all unnecessary.
**Fix**: Always check `GET /actor-runs/{id}/dataset/items` to verify actual data. Don't trust `stats.itemCount`.
**Date**: 2026-07-02

### CAR #6 — Full Input Schema Required (2026-07-02)
**Issue**: Partial input JSON (only keywords + maxItems + country) sometimes failed silently. Full schema with all fields works reliably.
**Root Cause**: Actor expects all fields present even if empty.
**Correct input format**:
```json
{
  "keywords": ["ของเล่นแมว", "คอนโดแมว"],
  "categoryUrls": [],
  "shopUrls": [],
  "country": "TH",
  "maxItems": 200,
  "priceSlicing": false,
  "debug": false
}
```

### PAR Addition
11. **NEVER trust `stats.itemCount`** — always check `dataset/items` endpoint for actual data
12. **Use FULL input schema** — include all fields (keywords, categoryUrls, shopUrls, country, maxItems, priceSlicing, debug)
13. **Use `debug: true`** for test runs to see logs (📦 Total final: N itens confirms actual count)
