# SOP: PetzDeals Daily Operations — ระบบ Automatic ทุกวัน

## The System

```
DATA → ANALYZE → ACT → DEPLOY → MEASURE → IMPROVE
 ↑                                              ↓
 └──────────────── DAILY LOOP ←─────────────────┘
```

## Who Does What

| Oracle | Role | Daily Tasks |
|---|---|---|
| **Data** | Data Engineer | Fetch GSC + GA4 + Shopee data, scrape offers, sync products |
| **Researcher** | Analyst | Analyze data, find keyword gaps, recommend content |
| **Writer** | Content | Write/update articles based on data insights |
| **Dev** | Engineer | Update site, fix bugs, deploy, new features |
| **QA** | Quality | Verify deploys, check links, visual testing |
| **BoB** | Orchestrator | Coordinate, track, report to แบงค์ |

## Daily Schedule (GMT+7)

### Phase 1: DATA COLLECTION (02:00 - 08:00, automated)

| Time | Loop ID | Oracle | Task | Output |
|---|---|---|---|---|
| 02:00 | `petdeals-apify-sync` | Data | Scrape Shopee Offer Pets page (380+ products) | `data/shopee-offers-raw.json` |
| 02:30 | `petdeals-product-feed` | Data | Download Shopee Product Feed CSV → match new products | `data/new-products.json` |
| 03:00 | `petdeals-offer-filter` | Data | Filter: rating ≥4.0, sold >50, commission ≥30%, real pet product | `data/top-deals.json` updated |
| 03:30 | `petdeals-affiliate-gen` | Data | Generate Custom Link for any new products | `data/products.json` updated |
| 06:00 | `petdeals-gsc-pull` | Data | Pull GSC data (7-day): impressions, clicks, CTR, position by page+query | `data/analytics/gsc-YYYY-MM-DD.json` |
| 06:30 | `petdeals-ga4-pull` | Data | Pull GA4 data (24h): page views, affiliate_click events, scroll_depth | `data/analytics/ga4-YYYY-MM-DD.json` |
| 07:00 | `petdeals-shopee-pull` | Data | Pull Shopee affiliate dashboard: clicks, orders, commission | `data/analytics/shopee-YYYY-MM-DD.json` |

### Phase 2: ANALYSIS (08:00 - 09:00)

| Time | Loop ID | Oracle | Task | Output |
|---|---|---|---|---|
| 08:00 | `petdeals-daily-analysis` | Researcher | Analyze all 3 data sources → generate daily report | `docs/analytics/YYYY-MM-DD.md` |

**Daily Report must answer:**

1. **Traffic**: How many visitors? Which pages? Which keywords?
2. **Engagement**: How far do they scroll? Which articles hold attention?
3. **Clicks**: Which products get clicked? From which articles? Which link position (inline/CTA/card)?
4. **Revenue**: How many orders? How much commission? Which products convert?
5. **Trends**: Up or down vs last 7 days? Any spikes or drops?
6. **Opportunities**: High impressions + low CTR pages? High traffic + low click pages?
7. **Action items**: What to write? What to optimize? What to replace?

**Report format:**

```markdown
# PetzDeals Daily — YYYY-MM-DD

## Traffic (GSC 7-day)
| Page | Impressions | Clicks | CTR | Position | Trend |
|---|---|---|---|---|---|

## Top Keywords
| Keyword | Imp | Clicks | Pos | Our Page | Action |
|---|---|---|---|---|---|

## Engagement (GA4 24h)
| Page | Views | Avg Scroll % | Affiliate Clicks | Click Rate |
|---|---|---|---|---|

## Product Performance
| Product | Clicks | From Article | Position | Orders | Commission |
|---|---|---|---|---|---|

## Revenue (Shopee)
| Metric | Today | 7-day avg | Trend |
|---|---|---|---|

## Action Items
| Priority | Action | Assign | Deadline |
|---|---|---|---|
| P1 | [what to do] | [oracle] | [when] |
```

### Phase 3: ACTION (09:00 - 16:00)

| Time | Oracle | Task | Trigger |
|---|---|---|---|
| 09:00 | **Writer** | Write new article OR optimize existing (based on report) | Researcher's action items |
| 09:00 | **Data** | Update ดีลเด็ด page with new high-commission products | Offer scrape results |
| 10:00 | **Dev** | Deploy content updates + any site fixes | Writer/Data changes |
| 10:30 | **QA** | Verify deploy: links, images, mobile, SEO | Post-deploy |
| 11:00 | **BoB** | Review daily report → forward key insights to แบงค์ | Report ready |

### Phase 4: DEPLOY & VERIFY (10:00 - 12:00)

```bash
# Dev runs after content updates:
cd ~/repos/github.com/BankCurfew/petdeals
npx astro build
CLOUDFLARE_API_TOKEN=... npx wrangler pages deploy dist --project-name=petzdeals
```

After deploy, QA verifies:
- [ ] New/updated pages load correctly
- [ ] All affiliate links are s.shopee.co.th
- [ ] Images load on mobile + desktop
- [ ] GSC sitemap resubmitted if new pages added

### Phase 5: MEASURE (16:00 - 17:00)

| Time | Oracle | Task |
|---|---|---|
| 16:00 | Data | Pull afternoon GA4 snapshot (did morning content get traffic?) |
| 16:30 | Researcher | Compare morning vs afternoon — any immediate impact? |
| 17:00 | BoB | End-of-day summary to แบงค์ (if significant changes) |

## Weekly Cycle

| Day | Focus | Lead |
|---|---|---|
| **Mon** | New article (keyword gap from last week's data) | Writer |
| **Tue** | Optimize lowest-performing article (add images, CTAs, rewrite intro) | Writer |
| **Wed** | New products from Shopee Offer (high commission) → ดีลเด็ด refresh | Data |
| **Thu** | Technical SEO check (broken links, new redirects, Core Web Vitals) | Dev + QA |
| **Fri** | Weekly report + next week plan | Researcher + BoB |
| **Sat** | Auto: loops run, no manual work | Automated |
| **Sun** | Auto: loops run, no manual work | Automated |

## Monthly Cycle

| Week | Focus |
|---|---|
| Week 1 | Content push — 2 new articles targeting top keyword gaps |
| Week 2 | Product expansion — scrape new categories, add 50+ products |
| Week 3 | Optimization — rewrite underperforming articles, A/B test CTAs |
| Week 4 | Review — monthly report, commission analysis, KPI check |

## Improvement Rules (Automatic)

| Signal | Threshold | Action | Who |
|---|---|---|---|
| Page has impressions but 0 clicks | >100 imp, 0 clicks, 7 days | Rewrite title + meta description | Writer |
| Article has traffic but low affiliate clicks | >50 views, <2% click rate | Add product images + CTAs in article | Writer |
| Product has 0 clicks for 7 days | 0 clicks across all pages | Replace with higher-performing product | Data |
| Keyword ranking dropped >5 positions | Position went from <10 to >15 | Add internal links, update content | Writer + Dev |
| New high-commission product appears | Commission ≥50% + rating ≥4.5 | Auto-add to ดีลเด็ด | Data (auto) |
| Article scroll depth <25% average | 7-day avg scroll <25% | Flag for content quality review | QA → Writer |
| Shopee link returns 404 | Link check fails | Regenerate via Custom Link | Data |

## Data Flow Diagram

```
SHOPEE OFFER ──→ Data scrapes ──→ top-deals.json ──→ /deals/today/ page
                                                  ↘
PRODUCT FEED ──→ Data matches ──→ products.json ──→ Product pages + cards
                                                  ↘
GSC API ────────→ Data pulls ───→ gsc-daily.json ──→ Researcher analyzes
GA4 API ────────→ Data pulls ───→ ga4-daily.json ──→ ┐
SHOPEE DASH ────→ Data pulls ───→ shopee-daily.json → Daily Report
                                                      ↓
                                              Action Items
                                                ↙     ↘
                                    Writer writes    Data updates
                                        ↓                ↓
                                    New content      New products
                                        ↓                ↓
                                    Dev deploys ←────────┘
                                        ↓
                                    QA verifies
                                        ↓
                                    Live on site → GSC/GA4 tracks → LOOP
```

## KPIs & Targets

| Metric | Week 1 | Month 1 | Month 3 | Month 6 |
|---|---|---|---|---|
| GSC Impressions/day | 100 | 1,000 | 10,000 | 50,000 |
| GSC Clicks/day | 5 | 50 | 500 | 2,500 |
| Affiliate Clicks/day | 2 | 20 | 200 | 1,000 |
| Shopee Orders/day | 0 | 1 | 10 | 50 |
| Commission/day | ฿0 | ฿50 | ฿500 | ฿2,500 |
| Articles | 7 | 15 | 30 | 50 |
| Products | 110 | 200 | 500 | 1,000 |
| Avg Click Rate | - | 2% | 5% | 8% |

## Loop Registration

All daily loops must be registered in `maw loop`:

```bash
# Data collection loops
maw loop add '{"id":"petdeals-apify-sync","oracle":"data","schedule":"0 2 * * *","prompt":"Scrape Shopee Offer Pets page → update top-deals.json"}'
maw loop add '{"id":"petdeals-gsc-pull","oracle":"data","schedule":"0 6 * * *","prompt":"Pull GSC data 7-day → save gsc-daily.json"}'
maw loop add '{"id":"petdeals-ga4-pull","oracle":"data","schedule":"30 6 * * *","prompt":"Pull GA4 data 24h → save ga4-daily.json"}'
maw loop add '{"id":"petdeals-shopee-pull","oracle":"data","schedule":"0 7 * * *","prompt":"Pull Shopee affiliate dashboard → save shopee-daily.json"}'

# Analysis loop
maw loop add '{"id":"petdeals-daily-analysis","oracle":"researcher","schedule":"0 8 * * *","prompt":"Analyze GSC+GA4+Shopee data → generate daily report with action items"}'

# Content loop
maw loop add '{"id":"petdeals-content","oracle":"writer","schedule":"0 9 * * *","prompt":"Check daily report action items → write or optimize one article"}'

# Deploy + QA loop
maw loop add '{"id":"petdeals-deploy-qa","oracle":"qa","schedule":"0 10 * * *","prompt":"Check if new content committed → deploy → verify links + images + mobile"}'

# BoB daily check
maw loop add '{"id":"petdeals-bob-review","oracle":"bob","schedule":"0 11 * * *","prompt":"Review daily report → summarize for แบงค์ → check oracle progress"}'
```

## Emergency Response

| Event | Response | Who | SLA |
|---|---|---|---|
| Site down (CF error) | Check CF status, redeploy | Dev | 30 min |
| Affiliate links broken | Regenerate via Custom Link | Data | 1 hour |
| Google ranking drop >50% | Audit site for issues, check GSC | Researcher + Dev | Same day |
| Shopee product removed | Remove from site, replace | Data | Same day |
| Commission rate changed | Update product data, re-evaluate | Data + Researcher | Same day |

## CAR/PAR

### CAR
**Issue**: No systematic daily operations — content, analytics, and product updates were ad-hoc. No data-driven decisions. No assigned responsibilities. No automated loops.
**Root Cause**: Site just launched, focused on building not operating.
**Fix**: Complete daily ops system with 8 automated loops, 6 oracle assignments, weekly/monthly cycles, improvement rules, KPI targets.
**Date**: 2026-06-29

### PAR
1. All loops registered in `maw loop` — visible on dashboard
2. Daily report is mandatory — Researcher must produce by 08:00
3. BoB reviews oracle progress daily at 11:00
4. Weekly report every Friday — KPI tracking against targets
5. Monthly review with แบงค์ — commission trends, content ROI
