# CDP SOP — Chrome DevTools Protocol Scraping Procedure

## Prerequisites

```bash
# Chrome running with remote debugging
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --disable-blink-features=AutomationControlled \
  --no-first-run &

# Verify
curl -s http://localhost:9222/json/version
```

## Connection

```typescript
// Use raw WebSocket — Playwright connectOverCDP times out on WSL
const ws = new WebSocket("ws://localhost:9222/devtools/page/TAB_ID");

// Open new tab
curl -X PUT "http://localhost:9222/json/new?about:blank"

// List tabs
curl -s http://localhost:9222/json
```

## Step 1: Login

```typescript
await cdp(ws, 'Page.navigate', {url: 'https://shopee.co.th/buyer/login'});
// Type via CDP keyboard (bypasses React state issues)
for (const c of "AP_marketing") {
  await cdp(ws, 'Input.dispatchKeyEvent', {type:'keyDown', text:c});
  await cdp(ws, 'Input.dispatchKeyEvent', {type:'keyUp', text:c});
}
// Tab → password → Enter
```

## Step 2: Search Products

```typescript
await cdp(ws, 'Page.navigate', {
  url: 'https://shopee.co.th/search?keyword=อาหารแมว&sortBy=sales'
});
// Extract: document.querySelectorAll('a[href*="-i."]')
// Parse shopId + itemId: href.match(/-i\.(\d+)\.(\d+)/)
```

## Step 3: Scrape Product Details

Navigate to product URL, extract: title, prices, rating, sold, images, description, specs.

## Step 4: Download Images

```typescript
const imgRes = await fetch(imageUrl);
// Upload to R2 via CF API
```

## Step 5: Affiliate Link

```
{product_url}?utm_source=an_15312860014&utm_medium=affiliates&utm_campaign=petdeals&utm_content={itemId}
```

## Anti-Bot Rules

- Real Chrome ONLY (not Playwright)
- CDP keyboard input (not DOM setter)
- Random delays 2-5s between pages
- Max 20 products per session
- Run overnight 02:00-06:00 GMT+7
- Blocked → wait 10 min → new tab

## Credentials: ~/.oracle/secrets/shopee-affiliate.env
