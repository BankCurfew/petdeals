# SOP: Shopee Affiliate Link Management

## Overview

All product and campaign links on PetzDeals must use proper Shopee affiliate share links generated from the affiliate portal. UTM-constructed links do NOT track properly through Shopee's system.

## Portal Access

- **URL**: https://affiliate.shopee.co.th/dashboard
- **Account**: AP (AP_marketing)
- **Affiliate ID**: an_15312860014
- **Access via**: CDP (port 9222) connected to logged-in Chrome
- **Credentials**: `~/.oracle/security/shopee-affiliate.env` (600 perms, gitignored). NEVER commit/echo the password.

### CDP Auto-Login (when session is missing)

The portal is a **plain username/password login — NO OTP/2FA** on the `AP_marketing` account. Do NOT defer to "แบงค์ logs in" without trying this first (verified 2026-07-16, T094).

1. Ensure CDP is up: `curl -sf localhost:9222/json/version`. If not, relaunch Chrome on the `C:\ChromeCDP` profile (see BoB memory `mac-cdp-default-profile-block`).
2. Open a tab to `https://affiliate.shopee.co.th/dashboard`. If it redirects to `shopee.co.th/buyer/login`, the session is missing → auto-login:
3. Fill `input[name=loginKey]` = `$SHOPEE_AFFILIATE_USER`, `input[name=password]` = `$SHOPEE_AFFILIATE_PASS` using the **React-native value setter** (plain `.value=` won't register):
   ```js
   const set=(el,v)=>{const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;s.call(el,v);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));};
   ```
   then click the button whose text is `LOG IN`.
4. Success = URL becomes `affiliate.shopee.co.th/dashboard?is_from_login=true`, nav shows รายการ feed สินค้า / รายงานคำสั่งซื้อ / รายงานคลิก / ลิงก์ที่กำหนดเอง.
5. **Session persists in `C:\ChromeCDP`** — later pulls skip login. Only re-login if Shopee expired the cookie.
6. Pull the feed via **in-page clicks on the same tab** — never `page.goto`/full-nav that drops the SPA session (see BoB memory `never-goto-spa-session`).

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

## Batch Link Generation via CDP (proven process)

When you need to convert many URLs to affiliate links at once:

1. Open a **fresh Chrome tab** to `https://affiliate.shopee.co.th/offer/custom_link` via CDP:
   ```bash
   node -e "const http=require('http'); http.request({hostname:'localhost',port:9222,path:'/json/new?https://affiliate.shopee.co.th/offer/custom_link',method:'PUT'},(r)=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>console.log(JSON.parse(d).id))}).end()"
   ```
2. Use `Input.insertText` to type URLs into the textarea (max 5 per batch)
3. Click `button.ant-btn-primary` ("Get Link")
4. Read result from `.ant-modal textarea` value
5. Close modal with `.ant-modal-close` click
6. Navigate fresh for next batch

**Important**: Use a dedicated tab. Don't share with other CDP operations. Reuse the same WebSocket connection across batches.

**Proven**: 2026-06-29 session converted 100 product links (20 batches) + 56 article links (12 batches) = 156 links total, zero failures.

## Deployment

After updating any affiliate links:
1. `npx astro build` — verify build passes
2. Deploy: `CLOUDFLARE_API_TOKEN=<token> npx wrangler pages deploy dist --project-name=petzdeals --commit-dirty=true`
3. CF project name is `petzdeals` (NOT `petdeals`)
4. Verify live: `curl -s https://petzdeals.com/blog/<article>/ | grep 's.shopee.co.th'`

## CAR/PAR

### CAR #1 — Product Links (2026-06-29)
**Issue**: All 110 product affiliate links used UTM-constructed URLs (`?utm_source=an_15312860014`) instead of proper Shopee share links. These earn ZERO commission — Shopee's attribution cookie is never set.
**Root Cause**: Initial scraper built UTM links from affiliate ID without going through Shopee's Custom Link conversion system.
**Fix**: Generated proper `s.shopee.co.th/xxx` links for all 110 products via Custom Link portal (100 products) and Product Feed CSV (10 products). Campaign page links (vouchers/flash-sale/coins) also converted.
**Date**: 2026-06-29

### CAR #2 — Article Links (2026-06-29)
**Issue**: 56 links across 7 blog articles pointed to direct `shopee.co.th` URLs (search pages and UTM product pages). These either: (a) earn no commission (UTM format), (b) go to error pages (old product URLs), or (c) use search URLs without tracking.
**Root Cause**: Original article content was written with direct Shopee links or search URLs instead of affiliate-converted links.
**Fix**: Batch-converted all 56 URLs via Custom Link portal (12 batches of 5). All articles now have zero `shopee.co.th` direct links — every link is `s.shopee.co.th/xxx` format.
**Date**: 2026-06-29
**Verification**: `grep -c 'shopee.co.th/' src/content/blog/*.md` = 0

### CAR #3 — Deployment Gap (2026-06-29)
**Issue**: 12 commits pushed to GitHub but site served old version for ~2 hours. All fixes (WEBP, affiliate links, images, meta tags) were invisible to users.
**Root Cause**: CF Pages was not auto-deploying from GitHub pushes. Project name confusion (`petdeals` vs `petzdeals`). No CI/CD pipeline configured.
**Fix**: Manual deploy via `wrangler pages deploy dist --project-name=petzdeals`. 
**Date**: 2026-06-29

### PAR (Preventive Action Report)
**Prevention**:
1. **NEVER construct UTM links manually** — always use Custom Link portal or Product Feed
2. **Every link in content MUST be `s.shopee.co.th/xxx` format** — QA checks this before deploy
3. **Deploy after every push**: `CLOUDFLARE_API_TOKEN=... npx wrangler pages deploy dist --project-name=petzdeals`
4. **Verify live links**: `curl -s https://petzdeals.com/<page>/ | grep -c 'shopee.co.th/'` must be 0
5. **Weekly Product Feed sync** to keep affiliate links fresh
6. **New Page Checklist** (in SOP-SEO-TAGS.md) must be followed for every new page
7. **CF project name is `petzdeals`** — NOT `petdeals` (caused 2-hour outage)
8. Set up GitHub Actions CI/CD for auto-deploy (TODO)
