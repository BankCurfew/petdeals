# /petdeals-sync — Sync prices, stock, and trends from Shopee

Re-check all published products on Shopee for price changes, stock status, and new deals. Update the database and flag products that need attention.

## Usage
```
/petdeals-sync                        # Sync all published products
/petdeals-sync --category อาหารแมว   # Sync specific category only
/petdeals-sync --deals                # Only check for new deals/price drops
/petdeals-sync --limit 100            # Limit batch size
/petdeals-sync --report               # Just report, don't update
```

## What it does

1. **Query Supabase** for all published products
2. **Open Shopee via CDP** (pw-cli.sh with saved state)
3. **For each product**, visit product URL and check:
   - Current price (changed?)
   - Stock status (in stock / out of stock?)
   - Rating (updated?)
   - Sold count (updated?)
   - Product still exists? (not removed by seller?)
4. **Update Supabase**:
   - Price changed → update price, original_price, discount_percent
   - Out of stock → set stock_status: 'out_of_stock', hide from site
   - Back in stock → set stock_status: 'in_stock', show again
   - Price drop > 20% → flag as 'deal', add to deals page
   - Product removed → set status: 'archived'
5. **Trigger rebuild** if any changes found
6. **Report** — changes table

## Sync Priority

| Priority | Products | Frequency |
|---|---|---|
| High | Best sellers (sold > 1000) | Daily |
| Medium | Regular products | Every 3 days |
| Low | Low-traffic products | Weekly |

## Deal Detection

```
IF new_price < old_price * 0.80:  # 20%+ drop
  → flag as 'deal'
  → add to /ดีล/ page
  → could trigger social post (future)

IF new_price > old_price * 1.20:  # 20%+ increase
  → update silently (normal market)

IF product.stock_status changed to 'out_of_stock':
  → hide from listings
  → keep page (for SEO, show "สินค้าหมด" message)
  → suggest alternatives (same category, similar price)
```

## Anti-bot precautions
- 3-5 second delay between product checks
- Max 100 products per session
- Rotate through products over multiple days
- If blocked → pause 10 min → resume
- Run during off-peak (02:00-06:00 GMT+7)

## Output
- Summary table: updated / unchanged / out_of_stock / deals / errors
- Log saved to Supabase sync_log table
