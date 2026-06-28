# SOP: PETDEALS Operations

> Standard Operating Procedure for daily operations of petzdeals.com
> Every oracle working on PETDEALS reads this before starting.

## Daily Pipeline (Automated)

### Schedule (GMT+7)

| Time | Task | Skill | Oracle |
|---|---|---|---|
| 02:00 | Product discovery — scrape Shopee trending | `/petdeals-cdp --discover` | Data |
| 03:00 | Product detail scrape — enrich new products | `/petdeals-cdp --scrape` | Data |
| 04:00 | Price/stock sync — update existing products | `/petdeals-cdp --sync` | Data |
| 05:00 | AI content — generate SEO titles + descriptions | `/petdeals-article` | Writer |
| 08:00 | Publish — release scheduled products | `/petdeals-publish` | BotDev |
| 08:30 | Index — submit new URLs to Google | `/petdeals-publish --index-only` | BotDev |
| 09:00 | Monitor — check build, page count, errors | Admin |

### Pipeline Flow

```
Discover → Scrape → Enrich → Schedule → Publish → Index → Monitor
   ↓          ↓        ↓         ↓          ↓         ↓        ↓
  CDP      CDP+R2    AI+DB     Supabase   Astro     Google   Dashboard
```

## Infrastructure

| Service | Detail | API Access |
|---|---|---|
| CF Zone | petzdeals.com (50181bfbd24d46d29eba7e09f74dcaf5) | CF API ✅ |
| CF Pages | petzdeals.pages.dev | CF API ✅ |
| CF R2 | petzdeals-images bucket | CF API ✅ |
| Supabase | 4 tables (products, categories, articles, site_config) | Supabase API ✅ |
| Chrome CDP | port 9222 (real Windows Chrome) | WebSocket ✅ |
| Shopee | CDP login (AP_marketing) | CDP only ❌ no API |
| GSC | petzdeals.com (verified via DNS TXT) | Browser ✅ |
| GTM | TBD — needs manual creation | Browser |
| GA4 | TBD — needs manual creation | Browser |

## Credentials (NEVER in git)

```
~/.oracle/secrets/shopee-affiliate.env
  SHOPEE_AFFILIATE_USER=AP_marketing
  SHOPEE_AFFILIATE_PASS=****
  SHOPEE_AFFILIATE_ID=an_15312860014
```

## Chrome CDP — How to Connect

```bash
# 1. Check Chrome is running
curl -s http://localhost:9222/json/version

# 2. If not running, launch:
nohup "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --disable-blink-features=AutomationControlled \
  --no-first-run > /dev/null 2>&1 &

# 3. Open new tab
curl -X PUT "http://localhost:9222/json/new?https://shopee.co.th"

# 4. List tabs
curl -s http://localhost:9222/json | python3 -c "import sys,json; [print(f'{p[\"title\"][:40]} | {p[\"id\"]}') for p in json.load(sys.stdin) if p.get('type')=='page']"

# 5. Connect via bun
const ws = new WebSocket("ws://localhost:9222/devtools/page/TAB_ID");
```

## Shopee Scraping — Proven Approach

### What Works
- Login via CDP keyboard input (Input.dispatchKeyEvent)
- Search results → product URLs (a[href*="-i."])
- Product detail pages → title, images, price
- Affiliate dashboard accessible
- Screenshot via Page.captureScreenshot

### What Doesn't Work
- Playwright browser (blocked by anti-bot fingerprint)
- DOM value setter for React inputs (use keyboard events)
- Web share button for affiliate links (app-only feature)
- Google c-wiz inputs (GTM/GA4 need manual creation)

### Anti-Bot Protocol
1. Use REAL Chrome only (not Playwright/Puppeteer managed)
2. CDP keyboard input (not DOM manipulation)
3. Random delays 2-5 seconds between navigations
4. Max 20 products per scrape session
5. Run overnight (02:00-06:00 GMT+7)
6. If blocked: wait 10 min, close tab, open new tab

## Content Pipeline

### Product Description (per SYSTEM-DESIGN.md §4)
1. AI rewrites Shopee title → SEO title (60-70 chars)
2. AI generates unique description (150-300 words)
3. Generates English URL slug
4. Editor reviews templates (per CONTENT-GUIDELINES.md)

### Articles (per SEO-CONTENT-STYLE-GUIDE.md)
1. Researcher provides keywords + content calendar
2. Writer creates article from template (1,500-2,000 words)
3. Editor reviews quality + SEO compliance
4. Schedule 1 article/day, 3 months ahead

### Image Pipeline
1. Download product images from Shopee CDN
2. Optimize: WebP, 800x800 main, 400x400 thumbnail
3. Upload to CF R2 (petzdeals-images bucket)
4. Store R2 URL in Supabase

## Deploy Pipeline

```bash
# Build
cd ~/repos/github.com/BankCurfew/petdeals
bun run build

# Deploy
CLOUDFLARE_API_TOKEN=<token> \
CLOUDFLARE_ACCOUNT_ID=3b1af24a7513b520e418d7e707f6491e \
npx wrangler pages deploy dist --project-name=petzdeals

# Verify
curl -s https://petzdeals.com | head -5
```

## Quality Checklist (before launch)

- [ ] 200+ product pages live
- [ ] 10+ articles published
- [ ] Schema markup valid (Google Rich Results Test)
- [ ] GSC verified + sitemap submitted
- [ ] GTM + GA4 tracking working
- [ ] Mobile responsive (390px test)
- [ ] Core Web Vitals: LCP < 2.5s, CLS < 0.1
- [ ] Affiliate links work (test click → Shopee)
- [ ] Images optimized (WebP, < 50KB each)
- [ ] robots.txt + sitemap.xml correct

## Monitoring

| What | How | Frequency |
|---|---|---|
| Build status | CF Pages dashboard | Per deploy |
| Page count | Astro build output | Daily |
| Search Console | GSC Performance tab | Weekly |
| Traffic | GA4 | Weekly |
| Affiliate revenue | Shopee affiliate dashboard | Weekly |
| Product freshness | Supabase last_synced_at | Daily |
| Image CDN | CF R2 analytics | Monthly |

## Incident Response

| Issue | Fix |
|---|---|
| Shopee blocks scraping | Wait 10 min → new Chrome tab → retry |
| Build fails | Check Astro error → fix → redeploy |
| Images broken | Check R2 bucket → re-upload |
| Prices stale | Run `/petdeals-cdp --sync` |
| Google deindex | Check GSC Coverage → fix issues → resubmit |
| CF Pages down | Check CF status → wait or switch DNS |

## CAR/PAR Log

| Date | Type | Issue | Fix | Prevention |
|---|---|---|---|---|
| 2026-06-28 | CAR | Shopee blocks Playwright | Switch to real Chrome CDP | Always use CDP, never Playwright for Shopee |
| 2026-06-28 | CAR | Google c-wiz blocks CDP input | Manual GTM/GA4 creation | Use Google APIs for future automation |
| 2026-06-28 | PAR | Web share no affiliate link | Use UTM params with affiliate ID | Build affiliate link from known format |

## Visual QA — MANDATORY (pw-cli)

**Every deploy MUST be visually verified using pw-cli.sh**

```bash
pw=~/.oracle/tools/pw-cli.sh
$pw open
$pw goto "https://petzdeals.com"
$pw screenshot  # Save + review

# Check:
# 1. Product images load (NOT placeholders)
# 2. Prices display correctly
# 3. Product names readable
# 4. CTA buttons visible
# 5. Mobile responsive (resize)
# 6. Affiliate links clickable

$pw goto "https://petzdeals.com/products/product-279775864-16255141757"
$pw screenshot  # Product detail page

$pw goto "https://petzdeals.com/blog"
$pw screenshot  # Articles page

$pw close
```

**CAR-2026-06-28**: QA passed affiliate links but missed placeholder images. Visual check was not done. Now MANDATORY in SOP.

**Rule**: No deploy is "production-ready" without pw-cli screenshot verification showing real product images + correct prices.
