# PETDEALS — Shopee Affiliate Pet Supplies

> petzdeals.com — ดีลอุปกรณ์สัตว์เลี้ยง Shopee ราคาดี

## Project

Fully automated Shopee affiliate website for premium pet supplies in Thailand.
Built with Astro 6 + Supabase + Cloudflare. Content pipeline uses CDP browser
automation (NOT Shopee API — they block bots).

## Stack

- **Framework**: Astro 6 (SSG — pure HTML, SEO perfect)
- **Database**: Supabase (PostgreSQL)
- **Deploy**: Cloudflare Pages (petzdeals.pages.dev → petzdeals.com)
- **Images**: Cloudflare R2
- **Cron/Workers**: Cloudflare Workers
- **Browser Automation**: pw-cli.sh (CDP-based, NOT Playwright MCP)
- **Affiliate**: Shopee Affiliate Program (แบงค์ has account: AP_marketing)

## Data Flow

```
CDP scrape Shopee → Supabase → Astro SSG build → CF Pages deploy → Google Index
```

1. `/petdeals-discover` — find trending products via CDP
2. `/petdeals-scrape` — get full details + images via CDP
3. `/petdeals-link` — generate affiliate links via CDP
4. `/petdeals-article` — AI generate articles from product data
5. `/petdeals-publish` — publish + rebuild + index
6. `/petdeals-sync` — daily price/stock check via CDP

## Key Files

- `docs/SYSTEM-DESIGN.md` — full system design, templates, pipeline
- `.claude/skills/petdeals-*.md` — 6 automation skills
- `src/` — Astro project (pages, components, layouts)
- `workers/` — CF Workers (cron jobs)

## Infrastructure

| Service | ID/URL |
|---|---|
| CF Zone | petzdeals.com (50181bfbd24d46d29eba7e09f74dcaf5) |
| CF Pages | petzdeals.pages.dev |
| CF Account | 3b1af24a7513b520e418d7e707f6491e |
| GitHub | BankCurfew/petdeals |
| Supabase | TBD — create project "petdeals" |
| Google Search Console | TBD — verify domain |
| GTM Container | TBD — create |
| GA4 Property | TBD — create |

## Credentials

**NEVER commit credentials to git.**
- Shopee: `~/.oracle/secrets/shopee-affiliate.env`
- CF token: use existing `cfat_soNNaf...` (has Pages Write permission)
- Google service account: TBD

## Anti-Bot Rules

Shopee has aggressive anti-bot detection. ALL scraping must:
1. Use pw-cli.sh with saved session state (`$pw state-load shopee`)
2. Random delays 2-5 seconds between actions
3. Max 50 products per scrape session
4. Run overnight (02:00-06:00 GMT+7) when traffic is low
5. If blocked → wait 10 min → new session
6. NEVER use direct HTTP requests to Shopee (will be blocked immediately)

## Oracle Team

| Oracle | Responsibility |
|---|---|
| Dev | Astro project, components, schema markup |
| Data | CDP scraping pipeline, Supabase schema, image pipeline |
| BotDev | Affiliate link automation, content scheduler |
| Designer | Brand, dark theme, product cards, responsive |
| Admin | CF infra, GTM, GA4, Search Console, DNS |
| Writer | Product descriptions, articles, SEO titles |
| Researcher | Keywords, content calendar, trends |
| QA | Testing, schema validation, speed |

## Commands

```bash
# Build
bun run build          # or: astro build
bun run dev            # local dev server

# Deploy
CLOUDFLARE_API_TOKEN=<token> \
CLOUDFLARE_ACCOUNT_ID=3b1af24a7513b520e418d7e707f6491e \
npx wrangler pages deploy dist --project-name=petzdeals

# Skills
/petdeals-discover     # find products
/petdeals-scrape       # get details
/petdeals-link         # get affiliate links
/petdeals-publish      # publish + deploy
/petdeals-article      # write articles
/petdeals-sync         # update prices
```
