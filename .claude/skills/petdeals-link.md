# /petdeals-link — Generate Shopee affiliate links via CDP

Generate affiliate tracking links using the Shopee Affiliate dashboard. No API needed — uses browser automation to paste product URLs and get tracking links.

## Usage
```
/petdeals-link                        # Generate links for all products without affiliate_url
/petdeals-link --limit 50             # Limit batch size
/petdeals-link --id <product-id>      # Generate for specific product
```

## What it does

1. **Query Supabase** for products WHERE affiliate_url IS NULL
2. **Open Shopee Affiliate Dashboard** via CDP (pw-cli.sh with saved state)
3. **Navigate to link generator** — affiliate.shopee.co.th > Generate Link
4. **For each product**:
   - Paste product URL into the link generator
   - Click generate
   - Copy the tracking short link (shp.ee/xxxxx)
   - Save to Supabase products.affiliate_url
5. **Report** — how many links generated, any failures

## Implementation

```bash
pw=~/.oracle/tools/pw-cli.sh
$pw -s=shopee open
$pw state-load shopee

# Navigate to affiliate dashboard
$pw goto "https://affiliate.shopee.co.th"

# Find the "Generate Link" or "สร้างลิ้งค์" section
$pw snapshot
# Look for link generator input field

# For each product URL:
# 1. Clear input
# 2. Paste product URL
# 3. Click generate
# 4. Copy result link
# 5. Save to DB

# Alternative: Some affiliate dashboards have a URL pattern
# https://affiliate.shopee.co.th/offer/product?itemId=XXX
# that auto-generates tracking links

$pw close
```

## Alternative approaches if dashboard is blocked

1. **Shopee affiliate link format** — some affiliates use:
   `https://shopee.co.th/product/{shopId}/{itemId}?af_id={affiliateId}`
   Check if this format works for tracking

2. **Involve Asia** — if Shopee direct is hard, use Involve Asia as intermediary
   (limit: 1,000 links/month)

3. **Deep link SDK** — Shopee may have a JS SDK for generating affiliate links client-side

## Anti-bot precautions
- 2-3 second delay between link generations
- Max 50 links per session
- Use saved session state
- If CAPTCHA appears → pause, notify แบงค์
