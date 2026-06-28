# /petdeals-scrape — Scrape product details from Shopee

Scrape full product details from a Shopee product page using CDP. Gets everything the API can't: full description, all images, specs, reviews.

## Usage
```
/petdeals-scrape                      # Scrape all draft products (no details yet)
/petdeals-scrape --url <shopee-url>   # Scrape specific product
/petdeals-scrape --limit 20           # Limit batch size
/petdeals-scrape --id <product-id>    # Scrape by DB id
```

## What it does

1. **Query Supabase** for products with status='draft' and no description
2. **Open each product URL** via CDP (pw-cli.sh)
3. **Extract from product page**:
   - Full title (Thai)
   - All images (main + gallery, up to 9)
   - Price, original price, discount
   - Rating (stars + review count)
   - Sold count
   - Shop name + shop rating
   - Product description (full text)
   - Specifications/attributes table
   - Category breadcrumb
   - Stock/availability
4. **AI rewrite** — generate:
   - SEO title (60-70 chars, remove spam, add benefit)
   - URL slug (English, descriptive)
   - Short description (150-300 words, unique content)
5. **Download images** → optimize WebP → upload to CF R2
6. **Update Supabase** with enriched data, status: 'scheduled'
7. **Schedule publish date** — stagger 10-20/day

## Implementation

```bash
pw=~/.oracle/tools/pw-cli.sh
$pw -s=shopee open
$pw state-load shopee

# For each product URL:
$pw goto "$PRODUCT_URL"
sleep 3  # wait for full page load

# Screenshot for visual verification
$pw screenshot

# Snapshot → parse product details from accessibility tree
$pw snapshot
# Parse: title, price, rating, description, specs, images

# Extract image URLs from page
# Download each image
# Optimize with sharp/imagemagick → WebP
# Upload to R2

$pw close
```

## Data extraction targets

| Field | Where on page | How to extract |
|---|---|---|
| Title | h1 or product-title class | Snapshot text |
| Price | price section | Snapshot, parse ฿ amount |
| Images | product gallery carousel | Snapshot img refs or page evaluate |
| Description | product-detail section | Snapshot or innerText |
| Specs | specifications table | Snapshot table rows |
| Rating | rating-stars section | Snapshot text |
| Sold count | "ขายแล้ว X ชิ้น" | Snapshot text, parse number |
| Shop name | shop section | Snapshot text |

## Anti-bot precautions
- 3-5 second delay between products
- Max 20 products per session
- Rotate user-agent if needed
- Use saved login state
- If blocked → wait 10 min → retry with new session
