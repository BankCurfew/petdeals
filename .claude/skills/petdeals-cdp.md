# /petdeals-cdp — Master CDP automation for Shopee

One-command Shopee automation: login → scrape products → get details → generate affiliate links → save to DB. Uses real Chrome via CDP (port 9222).

## Usage
```
/petdeals-cdp                         # Full pipeline: discover + scrape + links
/petdeals-cdp --discover              # Only: find trending products
/petdeals-cdp --scrape <itemId>       # Only: scrape one product detail
/petdeals-cdp --link <productUrl>     # Only: get affiliate link for URL
/petdeals-cdp --sync                  # Only: update prices/stock
/petdeals-cdp --category อาหารแมว     # Discover specific category
/petdeals-cdp --limit 20              # Limit products per run
```

## Prerequisites
- Windows Chrome running with `--remote-debugging-port=9222`
- If Chrome not running: launch from WSL:
  ```bash
  nohup "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
    --remote-debugging-port=9222 \
    --disable-blink-features=AutomationControlled \
    --no-first-run > /dev/null 2>&1 &
  ```
- Shopee credentials: `~/.oracle/secrets/shopee-affiliate.env`

## How it works

### Step 1: Connect to Chrome CDP
```typescript
// Test connection
curl -s http://localhost:9222/json/version

// Connect to specific tab
const ws = new WebSocket(`ws://localhost:9222/devtools/page/${TAB_ID}`);

// Open new tab
curl -X PUT "http://localhost:9222/json/new?${ENCODED_URL}"
```

### Step 2: Login to Shopee (if needed)
```typescript
// Navigate to login
await cdp(ws, "Page.navigate", { url: "https://shopee.co.th/buyer/login" });

// Type with CDP keyboard (bypasses React state issues)
for (const char of "AP_marketing") {
  await cdp(ws, "Input.dispatchKeyEvent", { type: "keyDown", text: char });
  await cdp(ws, "Input.dispatchKeyEvent", { type: "keyUp", text: char });
}
// Tab to password, type, Enter to submit
```

### Step 3: Discover products
```typescript
// Search pet category
await cdp(ws, "Page.navigate", { 
  url: "https://shopee.co.th/search?keyword=อาหารแมว&sortBy=sales" 
});

// Extract product URLs
const products = await cdp(ws, "Runtime.evaluate", {
  expression: `JSON.stringify(
    [...document.querySelectorAll('a[href*="-i."]')].map(a => {
      const href = a.getAttribute('href');
      const match = href.match(/-i\\.(\\d+)\\.(\\d+)/);
      return { 
        url: 'https://shopee.co.th' + href, 
        shopId: match?.[1], 
        itemId: match?.[2] 
      };
    }).filter(p => p.shopId)
  )`
});
```

### Step 4: Scrape product detail
```typescript
await cdp(ws, "Page.navigate", { url: productUrl });
// Wait 5s for page load
// Screenshot: cdp(ws, "Page.captureScreenshot", { format: "png" })
// Extract: title, price, images, description, rating, sold count, specs
```

### Step 5: Generate affiliate link
```
Affiliate ID: an_15312860014 (from ~/.oracle/secrets/shopee-affiliate.env)
Format: {product_url}?utm_source=an_15312860014&utm_medium=affiliates&utm_campaign=petdeals&utm_content={slug}

Short link format: https://s.shopee.co.th/XXXXXXXXXX
(Short links generated from Shopee app share button — web share doesn't work)
```

### Step 6: Save to Supabase
```typescript
// Upsert product to Supabase
// Download + optimize images → upload to R2
// Generate SEO title + description via AI
// Set publish_status: 'scheduled'
```

## CDP Helper Functions

```typescript
let msgId = 1;
function cdp(ws: WebSocket, method: string, params: any = {}): Promise<any> {
  return new Promise((resolve, reject) => {
    const id = msgId++;
    const t = setTimeout(() => reject(new Error(`Timeout`)), 25000);
    const h = (event: MessageEvent) => {
      const d = JSON.parse(event.data as string);
      if (d.id === id) {
        clearTimeout(t);
        ws.removeEventListener("message", h);
        d.error ? reject(new Error(d.error.message)) : resolve(d.result);
      }
    };
    ws.addEventListener("message", h);
    ws.send(JSON.stringify({ id, method, params }));
  });
}
```

## Anti-bot Rules
- Random delays: 2-5 seconds between page navigations
- Max 20 products per session
- Use real Chrome (NOT Playwright) — Shopee blocks Playwright fingerprint
- CDP keyboard input (NOT DOM value setter) — bypasses React state
- Run during off-peak: 02:00-06:00 GMT+7
- If blocked: close tab, wait 10 min, open new tab

## Known Working (tested 2026-06-28)
- ✅ Login via CDP keyboard input
- ✅ Search results scraping (product names + shopId + itemId)
- ✅ Product detail page navigation
- ✅ Screenshot capture
- ✅ Affiliate dashboard access (affiliate.shopee.co.th/dashboard)
- ❌ Share button on web (doesn't generate affiliate link — app only)
- ❌ Playwright browser (blocked by Shopee anti-bot)
- ❌ Google c-wiz input (GTM/GA4 creation needs manual)

## Affiliate Link Approach
Since web share doesn't work, use UTM-based tracking:
```
AFFILIATE_ID = an_15312860014
LINK = {product_url}?utm_source=${AFFILIATE_ID}&utm_medium=affiliates&utm_campaign=petdeals
```
Verify tracking works by checking Shopee affiliate dashboard → Report → filter by utm_source.
