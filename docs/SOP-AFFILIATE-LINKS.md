# SOP: Shopee Affiliate Link Management

## Overview

All product and campaign links on PetzDeals must use proper Shopee affiliate share links generated from the affiliate portal. UTM-constructed links do NOT track properly through Shopee's system.

## Portal Access

- **URL**: https://affiliate.shopee.co.th/dashboard
- **Account**: AP (AP_marketing)
- **Affiliate ID**: an_15312860014
- **Access via**: CDP (port 9222) connected to logged-in Chrome

## Portal Directory

| Section | Page | URL | Status | Purpose |
|---|---|---|---|---|
| **Dashboard** | Dashboard | /dashboard | Active | Key metrics: clicks, orders, commission |
| **Offer** | Shopee Offer | /offer/shopee_offer | Active | Browse Shopee offers with commission |
| | Commissions XTRA | /offer/brand_offer | Needs tier | Higher commission program (1000+ orders) |
| | Product Offer | /offer/product_offer | Active | Product-level commission offers |
| | Exclusive Offers | /offer/offer_for_me | Active | Special deals for your account |
| | **Custom Link** | /offer/custom_link | **Active** | Convert URLs → affiliate links (5 at a time) |
| **Campaign** | Affiliate Campaigns | /campaign/campaign_list | Needs tier | Campaign management |
| **Creative** | **Product Feed** | /creative/product_feed | **Active** | Daily CSV with 1M+ products + affiliate links |
| **Report** | Conversion Report | /report/conversion_report | Active | Track conversions |
| | Click Report | /report/click_report | Active | Track clicks |
| **Payment** | Commission Bill | /payment/billing | Active | View commissions earned |
| | Payout Record | /payment/payout_record | Active | View payouts |
| **Open API** | Open API | /open_api | Needs 1000 orders | GraphQL API for programmatic access |

## Method 1: Custom Link (Manual / Small Batch)

Best for: campaign pages, new products, one-off links.

### Steps

1. Navigate to https://affiliate.shopee.co.th/offer/custom_link
2. Paste up to **5 Shopee URLs** in the text area (one per line)
3. Set Sub_ids for tracking:
   - `Sub_id1`: `petdeals` (source)
   - `Sub_id2`: product slug or campaign name
4. Click **"Get Link"**
5. Copy the generated affiliate links
6. Update `data/products.json` or blog content with the new links

### Supported URL types
- Product Detail Pages: `https://shopee.co.th/{product-slug}-i.{shopId}.{itemId}`
- Campaign Pages: `https://shopee.co.th/m/vouchers`, `/m/flash-sale`, `/m/coins`
- Shop Pages: `https://shopee.co.th/{shop-name}`
- Category Pages: `https://shopee.co.th/{category}`
- Homepage: `https://shopee.co.th/`

### Limits
- Max 5 URLs per batch
- 5 Sub_id fields available per batch

## Method 2: Product Feed CSV (Bulk)

Best for: updating all 110+ product affiliate links at once.

### Steps

1. Navigate to https://affiliate.shopee.co.th/creative/product_feed
2. Click **"View Link"** on "Product Feed All Global Category"
3. Modal shows CSV download link — click **"Copy"**
4. Download the CSV (1M+ products per file, updated daily)
5. Match our products by `shopId` + `itemId`
6. Extract the `affiliate_link` column
7. Update `data/products.json`

### CSV Feed Details
- **Feed**: Product Feed All Global Category
- **Updated**: Daily at ~07:43
- **Fields**: stock, itemsold, item rating >1, New item only
- **Size**: 1M products per CSV file
- **Format**: CSV with affiliate short-links

### Automation Script

```bash
# Download feed (requires auth cookies from CDP)
curl -L "$FEED_URL" -b "$COOKIES" -o /tmp/shopee-feed.csv.gz

# Match our products
python3 scripts/match-affiliate-links.py \
  --feed /tmp/shopee-feed.csv \
  --products data/products.json \
  --output data/products-updated.json
```

## Method 3: Share from Shopee App/Website

Best for: individual products when browsing.

### Steps

1. Login to Shopee with the affiliate-connected account
2. Navigate to the product page
3. Click the **Share** button
4. The share link automatically includes affiliate tracking
5. Use that link in content

## Tracking & Sub_ids

| Sub_id | Use |
|---|---|
| `Sub_id1` | Source: `petdeals` |
| `Sub_id2` | Page type: `product`, `blog`, `deal` |
| `Sub_id3` | Specific slug or campaign name |
| `Sub_id4` | Position: `hero`, `card`, `cta`, `article-link` |
| `Sub_id5` | Date: `YYYYMMDD` |

## When to Update Links

- **Daily**: Product Feed auto-updates. Run sync script weekly.
- **New product added**: Generate link via Custom Link immediately.
- **Campaign page links**: Generate before campaign start (e.g., 7.7 voucher links before July 1).
- **Link broken**: Re-generate via Custom Link.

## Open API (Future — needs 1000+ orders)

Once we hit 1000 orders, apply for Open API access:
- **Protocol**: GraphQL over HTTP
- **Docs**: https://graphql.org/
- **Enables**: Programmatic link generation, bulk operations, real-time data

## CAR/PAR

### CAR (Corrective Action Report)
**Issue**: All 110 product affiliate links used UTM-constructed URLs instead of proper Shopee share links. Campaign page links had no affiliate tracking at all.
**Root Cause**: Initial scraper built UTM links from affiliate ID without going through Shopee's link conversion system.
**Fix**: Use Custom Link portal or Product Feed CSV to generate proper affiliate links for all products and campaign pages.
**Date**: 2026-06-29

### PAR (Preventive Action Report)
**Prevention**:
1. All new products MUST have affiliate links generated via Custom Link or Product Feed — never construct UTM links manually
2. Weekly Product Feed sync script to keep affiliate links fresh
3. Sub_id tracking on all links for attribution analysis
4. SOP review before any link-related code change
