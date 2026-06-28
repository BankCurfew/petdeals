# /petdeals-discover — Find trending pet products on Shopee

Discover trending pet products from Shopee Thailand using CDP browser automation. Scrapes trending pages, flash sales, and category best sellers.

## Usage
```
/petdeals-discover                    # Discover trending pet products (all categories)
/petdeals-discover --category แมว     # Specific: cat products only
/petdeals-discover --category สุนัข   # Specific: dog products only
/petdeals-discover --flash            # Flash sale deals only
/petdeals-discover --limit 50         # Limit number of products
```

## What it does

1. **Open Shopee via CDP** (pw-cli.sh with saved shopee state)
2. **Browse pet categories** — search trending keywords:
   - อาหารแมว, อาหารสุนัข, ของเล่นแมว, ของเล่นสุนัข
   - อุปกรณ์ดูแลสัตว์เลี้ยง, ทรายแมว, สายจูง
   - เครื่องให้อาหารอัตโนมัติ, ที่นอนสัตว์เลี้ยง
3. **Sort by sales/popularity** — get best sellers
4. **Extract product data** from listing page:
   - Product name, price, original price, discount %
   - Rating, sold count
   - Product URL (for detail scraping later)
   - Thumbnail image URL
5. **Check for duplicates** against Supabase (by shopee_item_id)
6. **Save new products** to Supabase with status: 'draft'
7. **Report** — table of new products found

## Implementation

```bash
pw=~/.oracle/tools/pw-cli.sh

# Load saved Shopee session
$pw -s=shopee open
$pw state-load shopee

# Navigate to pet category
$pw goto "https://shopee.co.th/search?keyword=อาหารแมว&sortBy=sales"

# Snapshot → parse product cards from accessibility tree
$pw snapshot

# Extract data from snapshot YAML
# Each product card contains: name, price, rating, sold, URL

# Paginate: scroll down or click next page
# Repeat for each category keyword

# Save to Supabase via edge function or direct API
```

## Categories to search

| Priority | Keyword | Expected Volume |
|---|---|---|
| 1 | อาหารแมว | High |
| 1 | อาหารสุนัข | High |
| 2 | ของเล่นแมว | Medium |
| 2 | ทรายแมว | Medium |
| 3 | เครื่องให้อาหารอัตโนมัติ | Medium |
| 3 | สายจูงสุนัข | Medium |
| 4 | ที่นอนสัตว์เลี้ยง | Low |
| 4 | แชมพูสุนัข | Low |

## Output
- Products saved to Supabase `products` table (status: draft)
- Summary table printed to console
- Count: new vs duplicate vs filtered out

## Anti-bot precautions
- Random delays between page loads (2-5 seconds)
- Max 50 products per session
- Use saved session state (don't re-login)
- Run during off-peak hours (02:00-06:00 GMT+7)
