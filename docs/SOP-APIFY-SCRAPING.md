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

### CAR
**Issue**: Data used wrong Apify actors (shopee-scraper, web-scraper) → 403 Forbidden on all 13 searches. 30 min wasted.
**Root Cause**: No documentation of which Apify actor works. Data guessed wrong.
**Fix**: Documented working actor ID (fmKWN5uByUCIy2Sam) + CDP fallback method. Redirected to CDP for immediate scraping.
**Date**: 2026-06-30

### PAR
1. **Actor ID documented** in this SOP — always use fmKWN5uByUCIy2Sam
2. **CDP fallback** documented step-by-step
3. **Never guess actors** — check this SOP first
4. **Test with 1 search** before running batch
