# Shopee Offer Scraper Spec

## Data Source

**URL**: `https://affiliate.shopee.co.th/offer/shopee_offer/100631?type=2`
**Offer**: Direct 2% / Indirect 0.6% - Pets (ID: 100631)
**Period**: 20-04-2026 - No limit
**Base Commission**: up to 2% (but individual products have XTRA up to 82%)

## Current Inventory (scraped 2026-06-29)

| Metric | Value |
|---|---|
| Total Pets products | 380 |
| Pages | 19 (20 products/page) |
| High commission (50%+) | 113 products |
| With sales data | 224 products |
| Commission range | 22% - 82% |

### Commission Rate Distribution

| Comm Rate | Count | Notes |
|---|---|---|
| 82% | 2 | กล่องชันโรง (beehive boxes) |
| 72% | 9 | Pet toys, accessories |
| 52% | ~30 | Cat/dog toys, scratchers, cooling mats |
| 40-49% | ~30 | Mixed accessories |
| 30-39% | ~50 | Leashes, grooming, beds |
| 22-29% | ~100+ | Food, treats, litter |

## Product Card Data Structure

Each `product-offer-item` card contains:

```json
{
  "title": "Product title in Thai",
  "price": "149.00",
  "sold": 90,
  "commRate": 82,
  "discount": 20,
  "image": "https://down-th.img.susercontent.com/file/..."
}
```

### DOM Structure
```
.product-offer-item
  img (product image)
  title text
  ฿{price}
  {sold} sold
  Comm Rate {commRate}%
  [discount badge: {discount}% OFF]
  button "Get Link" → generates affiliate short link
```

### Pagination
- **Class**: `.page-page`, `.page-next`, `.page-prev`, `.page-more`
- **Active page**: `.page-page.active`
- **20 products per page**
- Total pages calculated by: navigate to last visible page → check if more exists → continue

## All Available Category Offers (Page 1 of 2)

| Offer ID | Category | Commission |
|---|---|---|
| 100001 | Health & Wellness | up to 2% |
| 100009 | Fashion Accessories | up to 2% |
| 100010 | Home Appliances | up to 2% |
| 100011 | Men Clothes | up to 2% |
| 100012 | Men Shoes | up to 2% |
| 100013 | Mobile & Tablets | up to 2% |
| 100014 | Baby & Toys | up to 2% |
| 100015 | Bags | up to 2% |
| 100017 | Women Clothes | up to 2% |
| 100532 | Women Shoes | up to 2% |
| 100534 | Watches & Glasses | up to 2% |
| 100535 | Cameras | up to 2% |
| 100629 | Food & Beverages | up to 2% |
| 100630 | Beauty & Personal Care | up to 2% |
| **100631** | **Pets** | **up to 2%** |
| 100632 | Baby & Toys | up to 2% |
| 100634 | Gaming & Accessories | up to 2% |

**Note**: "up to 2%" is the base rate. Individual products within offers have XTRA commission (22-82%).

## Scraping Strategy

### Option A: CDP via pw-cli (Recommended for now)

**Pros**: Works with existing auth, no API key needed, full access to "Get Link" feature
**Cons**: Slower, needs browser session, harder to schedule

```python
# CDP connection pattern
import websockets
ws = websockets.connect("ws://localhost:9222/devtools/page/{TAB_ID}", max_size=10*1024*1024)
# Navigate: Page.navigate
# Extract: Runtime.evaluate with DOM queries
# Paginate: click .page-page elements
```

### Option B: Apify Actor (Recommended for daily automation)

**Pros**: Scheduled, reliable, no local browser needed
**Cons**: Needs Apify subscription ($49/mo Starter), needs Shopee auth cookie injection

**Actor design**:
1. Input: Shopee affiliate auth cookies (from CDP `Network.getCookies`)
2. Navigate to offer page with cookies
3. Scrape all pages sequentially
4. Output: JSON array of products with affiliate links
5. Schedule: daily at 03:00 GMT+7

### Option C: Product Feed CSV (Bulk but limited)

**Pros**: 1M products, daily update, proper affiliate links
**Cons**: No commission rate data, our products may not be in feed (only 10/110 matched)

## Recommended Daily Sync Workflow

```
03:00  Apify runs → scrape Pets offer page (380+ products)
       ↓
       Output: shopee-offer-pets-{date}.json
       ↓
03:30  Sync script:
       1. Match new products against our catalog (by title/shopId)
       2. Update commission rates for existing products
       3. Flag new high-commission products (50%+) for review
       4. Generate "Get Link" affiliate URLs for new additions
       ↓
04:00  Build & deploy (if changes detected)
       ↓
09:00  QA daily check (petdeals-qa-daily loop)
```

## Integration with PetzDeals

### New features enabled:
1. **Commission badge** on product cards (show "82% คอมมิชชัน" for high-comm products)
2. **"Hot Commission" section** on deals page (products with 50%+ commission)
3. **Sort by commission** option for internal prioritization
4. **Daily fresh data** — prices, sold counts, commission rates updated daily

### Data pipeline:
```
Shopee Offer (380 products)
  → filter: Thai pet supplies only (exclude beehive boxes etc.)
  → filter: commission >= 30%
  → match: against our existing catalog
  → output: products.json updates + new product suggestions
```

## Sample Data (Top 10 by Commission Rate)

See `/tmp/shopee-pets-all-products.json` for full dataset.
