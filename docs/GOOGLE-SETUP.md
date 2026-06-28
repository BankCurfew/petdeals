# PETDEALS — Google Services Setup & Management

> All Google service IDs, how to configure, and how to maintain.

---

## Service Directory

| Service | ID | Status |
|---|---|---|
| Google Search Console | `petzdeals.com` (domain property) | Verified (DNS TXT) |
| Google Tag Manager | `GTM-MXZC4NXN` (account 6363236236, container 256793462) | Created |
| Google Analytics 4 | `G-3TCK9V54XS` (account 399517815, property 543407169) | Created |
| Google Cloud Project | `petzdeal-500812` | Active |
| OAuth Client | `[OAUTH_CLIENT_ID — see ~/.oracle/secrets/shopee-affiliate.env]` | Published |

---

## 1. Google Search Console (GSC)

**Property**: `petzdeals.com` (domain-level, covers all subdomains + protocols)

**Verification**: DNS TXT record on Cloudflare
```
Type: TXT
Name: petzdeals.com
Value: google-site-verification=J1PyXQHoZTaFANJCcMq936jI4cc9UuRdMdefdorN_OU
```

**Key tasks**:

| Task | How |
|---|---|
| Submit sitemap | GSC → Sitemaps → enter `sitemap-index.xml` → Submit |
| Check indexing | GSC → Pages → see indexed vs excluded |
| Monitor performance | GSC → Performance → filter by query/page/country |
| Inspect URL | GSC → URL Inspection → paste URL → check status |
| Request indexing | URL Inspection → Request Indexing (max 10/day manual) |

**Programmatic indexing** (via Google Indexing API):
- Requires service account added as Owner in GSC
- Max 200 publish requests/day, 600 total/day
- Endpoint: `POST https://indexing.googleapis.com/v3/urlNotifications:publish`
- Body: `{"url": "https://petzdeals.com/...", "type": "URL_UPDATED"}`

---

## 2. Google Tag Manager (GTM)

**Container**: `GTM-MXZC4NXN`
**Account**: 6363236236
**Container ID**: 256793462
**Workspace URL**: `https://tagmanager.google.com/#/container/accounts/6363236236/containers/256793462/workspaces/2`

**Installation**: Already in `BaseLayout.astro` — head script + body noscript tag.

### Required Tags

| Tag | Type | Trigger | Parameters |
|---|---|---|---|
| GA4 Configuration | Google Analytics: GA4 Configuration | All Pages | Measurement ID: `G-3TCK9V54XS` |
| Affiliate Click | GA4 Event | Click URL contains `shopee.co.th` OR `shp.ee` | event: `affiliate_click`, link_url, product_name |
| View Item | GA4 Event | Page Path matches `/*/product-*` | event: `view_item`, item_id, item_name, price |
| Search | GA4 Event | Custom Event: `search` | event: `search`, search_term |
| Scroll Depth | Scroll Depth | Scroll Depth 25%, 50%, 75%, 90% | event: `scroll` |

### How to Add a Tag

1. Open GTM workspace
2. Tags → New → choose tag type
3. Configure tag (add measurement ID, event name, parameters)
4. Create trigger (Page View, Click, Custom Event, etc.)
5. Preview → test in debug mode
6. Submit → Publish

### DataLayer Push (from ProductCard component)

```javascript
dataLayer.push({
  event: 'affiliate_click',
  product_name: 'อาหารแมว Royal Canin',
  product_price: 459,
  product_category: 'อาหารแมว',
  affiliate_url: 'https://shopee.co.th/...'
});
```

---

## 3. Google Analytics 4 (GA4)

**Measurement ID**: `G-3TCK9V54XS`
**Account**: `accounts/399517815` (PetzDeals)
**Property**: `properties/543407169` (PetzDeals)
**Data Stream**: PetzDeals Web (`https://petzdeals.com`)

### Key Events to Track

| Event | When | Key Event? |
|---|---|---|
| `page_view` | Every page (auto via GA4 config) | No |
| `affiliate_click` | Click Shopee CTA button | **Yes** (mark as conversion) |
| `view_item` | Product detail page view | No |
| `view_item_list` | Category listing page | No |
| `search` | On-site search | No |
| `scroll` | 75%+ scroll on article | No |

### Custom Dimensions (set up in GA4 Admin → Custom definitions)

| Dimension | Scope | Description |
|---|---|---|
| `product_category` | Event | อาหารแมว, ของเล่น, etc. |
| `article_type` | Event | review, comparison, guide |

### Link GSC ↔ GA4

1. GA4 → Admin → Product links → Search Console
2. Click Link → select `petzdeals.com` property
3. Confirm

---

## 4. OAuth Credentials

**Cloud Project**: `petzdeal-500812`
**OAuth Client ID**: `[OAUTH_CLIENT_ID — see ~/.oracle/secrets/shopee-affiliate.env]`
**Client Secret**: stored in `~/.oracle/secrets/shopee-affiliate.env`
**Redirect URIs**: `http://localhost:3333/callback`, `http://localhost:8888`
**Scopes**: `analytics.edit`, `analytics.provision`

### How to Get a New OAuth Token

```bash
# 1. Start callback server
cat > /tmp/oauth-server.ts << 'EOF'
const server = Bun.serve({
  port: 3333,
  async fetch(req) {
    const code = new URL(req.url).searchParams.get("code");
    if (code) {
      const res = await fetch("https://oauth2.googleapis.com/token", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: `code=${code}&client_id=[OAUTH_CLIENT_ID — see ~/.oracle/secrets/shopee-affiliate.env]&client_secret=[OAUTH_CLIENT_SECRET — see secrets file]&redirect_uri=http%3A%2F%2Flocalhost%3A3333%2Fcallback&grant_type=authorization_code`
      });
      const tokens = await res.json();
      console.log("TOKEN:", tokens.access_token);
      await Bun.write("/tmp/access-token.txt", tokens.access_token);
      server.stop();
      return new Response("Done");
    }
    return new Response("waiting");
  }
});
EOF
bun /tmp/oauth-server.ts &

# 2. Open auth URL in Chrome (via CDP)
# Navigate to: https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=948937708529-...&redirect_uri=http%3A%2F%2Flocalhost%3A3333%2Fcallback&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fanalytics.edit&access_type=offline

# 3. Click through consent: Account → Advanced → Go to petzdeal (unsafe) → Continue

# 4. Token saved to /tmp/access-token.txt
```

### Enabled APIs

- Google Analytics Admin API
- Google Tag Manager API (enabled)
- Google Search Console API (enabled)

---

## 5. API Key

**Key**: `AIzaSyDW0reowS0xQvmsAx8uhvHtIkPTGffIe98`

API keys do NOT work for management APIs (Analytics, GTM, GSC). They only work for public-data APIs. Use OAuth2 tokens for all management operations.

Use `x-goog-api-key` header for supported APIs:
```bash
curl -H "x-goog-api-key: AIzaSyDW0reowS0xQvmsAx8uhvHtIkPTGffIe98" https://...
```
