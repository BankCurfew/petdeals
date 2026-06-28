# /petdeals-publish — Publish scheduled products and rebuild site

Publish products that are scheduled for today, trigger Astro rebuild, deploy to CF Pages, and submit new URLs to Google for indexing.

## Usage
```
/petdeals-publish                     # Publish today's scheduled products + rebuild
/petdeals-publish --dry-run           # Show what would be published without doing it
/petdeals-publish --force-rebuild     # Force rebuild even if nothing new
/petdeals-publish --index-only        # Only submit URLs to Google (no rebuild)
```

## What it does

1. **Query Supabase** for products WHERE status='scheduled' AND scheduled_at <= NOW()
2. **Update status** to 'published', set published_at = NOW()
3. **Trigger Astro rebuild**:
   ```bash
   cd /home/curfew/repos/github.com/BankCurfew/petdeals
   bun run build
   ```
4. **Deploy to CF Pages**:
   ```bash
   CLOUDFLARE_API_TOKEN=<token> \
   CLOUDFLARE_ACCOUNT_ID=3b1af24a7513b520e418d7e707f6491e \
   npx wrangler pages deploy dist --project-name=petzdeals
   ```
5. **Submit to Google Indexing API** (max 200/day):
   - For each newly published product URL
   - POST to indexing.googleapis.com/v3/urlNotifications:publish
   - Body: { "url": "https://petzdeals.com/{category}/{slug}", "type": "URL_UPDATED" }
6. **Submit to IndexNow** (Bing/Yandex):
   - POST to api.indexnow.org/indexnow
   - Include all new URLs in batch
7. **Report** — products published, build status, indexing results

## Schedule
- Daily 08:00 GMT+7 (via maw loop or manual)
- Publish 10-20 products/day (staggered over time)

## Prerequisites
- Products must have: title_seo, slug, description, image_url, affiliate_url, category_id
- Products missing any field → skip, log warning
- Google Indexing API service account must be set up in Google Cloud Console

## Verification
After publish:
- Check petzdeals.com for new products
- Google Rich Results Test on 1-2 new pages
- Verify affiliate links work (click → Shopee product page)
