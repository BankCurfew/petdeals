# SOP: Funnel Marketing Strategy — PetzDeals

## The Funnel

```
DISCOVER → READ → CLICK → BUY
  GSC       GA4    Event   Shopee
```

| Stage | Metric | Source | Goal |
|---|---|---|---|
| **Discover** | Impressions, Clicks, CTR, Position | GSC API | Get found on Google + AI |
| **Read** | Page views, Scroll depth, Time on page | GA4 | Keep readers engaged |
| **Click** | Affiliate link clicks by article/product/position | GA4 Events | Drive clicks to Shopee |
| **Buy** | Orders, Commission | Shopee Affiliate Dashboard | Revenue |

## Tracking System (implemented)

### Events Fired

| Event | When | Params | Source |
|---|---|---|---|
| `page_view` | Every page load | page_path, page_title | GA4 auto |
| `affiliate_click` | Any s.shopee.co.th link clicked | article_slug, product_name, link_position, link_url, page_type | BaseLayout.astro |
| `scroll_depth` | Reader hits 25/50/75/100% | scroll_pct, article_slug | BaseLayout.astro |

### Link Position Values

| Position | Meaning | Example |
|---|---|---|
| `cta` | CTA button ("เช็คราคาให้เจ้านาย") | Product page main CTA, card CTA |
| `card` | ProductCard component | Homepage grid, related products |
| `inline` | Link inside article text | "เช็คราคาที่ Shopee →" in blog |
| `other` | Navigation, deals page, etc. | Top nav, footer |

### What We Can Analyze

From these events + GSC data, we know:

| Question | How to Answer |
|---|---|
| Which article drives most clicks? | GA4: `affiliate_click` count by `article_slug` |
| Which product is most clicked? | GA4: `affiliate_click` count by `product_name` |
| Do readers click inline links or CTAs? | GA4: `affiliate_click` by `link_position` |
| How far do readers scroll? | GA4: `scroll_depth` distribution |
| Which keywords bring traffic? | GSC: queries by page |
| Which articles rank well but have low CTR? | GSC: high impressions + low CTR = improve title/description |
| Which articles have traffic but low clicks? | GA4: high page_view + low affiliate_click = improve CTA placement |

## Daily Automation Loop

### Schedule

| Time | Task | Oracle | Output |
|---|---|---|---|
| **08:00** | Pull GSC data (7-day) | Data | `data/analytics/gsc-daily.json` |
| **08:30** | Pull GA4 data (24h) | Data | `data/analytics/ga4-daily.json` |
| **09:00** | Pull Shopee dashboard (commission, clicks) | BoB/Data | `data/analytics/shopee-daily.json` |
| **09:30** | Analysis report | Researcher | `docs/analytics/YYYY-MM-DD.md` |
| **10:00** | Content brief (if needed) | Writer | New article or optimization |
| **14:00** | Shopee Offer scrape → update ดีลเด็ด | Data | `data/top-deals.json` |
| **16:00** | QA check deployed changes | QA | Pass/fail report |

### Daily Analysis Report Format

```markdown
# PetzDeals Daily Report — YYYY-MM-DD

## GSC Summary (7-day)
| Page | Impressions | Clicks | CTR | Avg Position |
|---|---|---|---|---|

## Top Keywords
| Keyword | Impressions | Clicks | Position |
|---|---|---|---|

## GA4 Summary (24h)
| Page | Views | Affiliate Clicks | Click Rate | Avg Scroll |
|---|---|---|---|---|

## Top Clicked Products
| Product | Clicks | From Article | Position |
|---|---|---|---|

## Shopee Commission (yesterday)
| Metric | Value |
|---|---|
| Clicks | |
| Orders | |
| Commission | |

## Recommendations
1. [action item]
2. [action item]
```

### Analysis Script

```python
# GSC data pull (requires OAuth)
import requests

token = get_access_token()  # from shopee-affiliate.env
headers = {"Authorization": f"Bearer {token}"}
site = "sc-domain:petzdeals.com"

# Search analytics
resp = requests.post(
    f"https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query",
    headers=headers,
    json={
        "startDate": "2026-06-22",
        "endDate": "2026-06-29",
        "dimensions": ["page", "query"],
        "rowLimit": 100
    }
)
```

## Content Strategy — What to Write

### Priority Matrix

| Keyword Signal | Action |
|---|---|
| High impressions, low CTR | Optimize title + meta description |
| High CTR, low clicks (few impressions) | Build backlinks, add internal links |
| High traffic, low affiliate clicks | Improve CTA placement, add product images |
| Competitor ranks, we don't | Write new article targeting that keyword |
| Shopee Offer high commission product | Feature in ดีลเด็ด or write dedicated review |

### Article Types by Funnel Stage

| Stage | Article Type | Example | Goal |
|---|---|---|---|
| **Top (Discover)** | Keyword-rich guide | "วิธีเลือกอาหารแมว 2026" | Attract Google traffic |
| **Middle (Read)** | Review/comparison | "10 อาหารแมว ยี่ห้อไหนดี" | Build trust, show products |
| **Bottom (Click)** | Deal page | "ดีลเด็ดวันนี้", "7.7 Mega Sale" | Drive affiliate clicks |
| **Retain** | Tips/how-to | "เปลี่ยนอาหารแมวยังไง" | Bring readers back |

### Weekly Content Calendar

| Day | Content | Oracle |
|---|---|---|
| Mon | New article (based on keyword gap analysis) | Writer |
| Tue | Optimize existing article (based on GSC data) | Writer |
| Wed | Update ดีลเด็ด (new Shopee Offer products) | Data |
| Thu | Social share / cross-link optimization | Writer |
| Fri | Weekly report + next week plan | Researcher |
| Sat-Sun | Auto: Shopee Offer sync, GSC monitoring | Loops |

## Improvement Automation

### Auto-Detect & Fix

| Signal | Auto-Action |
|---|---|
| Article scroll < 25% avg | Flag for content quality review |
| Article click rate < 2% | Add more CTAs + product images |
| Product click count = 0 for 7 days | Replace with higher-performing product |
| GSC position > 20 for target keyword | Add internal links from other articles |
| New Shopee Offer product (>50% commission) | Auto-add to ดีลเด็ด page |

### KPIs

| Metric | Target (Month 1) | Target (Month 3) |
|---|---|---|
| GSC Impressions | 1,000/day | 10,000/day |
| GSC Clicks | 50/day | 500/day |
| Affiliate Clicks | 20/day | 200/day |
| Shopee Orders | 1/day | 10/day |
| Commission | ฿50/day | ฿500/day |
| Articles | 7 (current) | 20+ |
| Products | 110 (current) | 300+ |

## CAR/PAR

### CAR
**Issue**: No click tracking on inline article links (เช็คราคาที่ Shopee). Only ProductCard CTA had `dataLayer.push`. 60% of affiliate links on the site had zero analytics.
**Root Cause**: Click tracking was added only to ProductCard component, not globally.
**Fix**: Added global click listener in BaseLayout.astro that tracks ALL `s.shopee.co.th` and `shope.ee` link clicks with article_slug, product_name, link_position, page_type. Also added scroll_depth tracking for articles.
**Date**: 2026-06-29

### PAR
1. Every new link type must fire `affiliate_click` event — enforced by global listener
2. QA checks GA4 Realtime for events after deploy
3. Daily analysis loop catches zero-click products/articles
4. Weekly KPI review against targets
