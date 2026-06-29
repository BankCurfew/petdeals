# SOP: SEO Tags, Meta, and Content Structure

## Overview

Every page on PetzDeals must have proper SEO structure: tags, headings, meta tags, structured data, and image optimization. This SOP covers the standards and how to maintain them.

## Blog Article Requirements

### Frontmatter (Required Fields)

```yaml
---
title: "Full SEO title with keywords"
description: "150-160 char meta description"
date: "YYYY-MM-DD"
author: "น้องดีล 🐾"
category: "รีวิว|ดีล|แนะนำ"
tags: ["keyword1", "keyword2", "brandname", "2026", "ทาสแมว"]
---
```

### Tag Guidelines

| Rule | Example |
|---|---|
| 5-10 tags per article | `["อาหารแมว", "รีวิว", "Royal Canin", "2026"]` |
| Include category keywords | รีวิว article → `"รีวิว"` tag |
| Include brand names mentioned | Article about Royal Canin → `"Royal Canin"` tag |
| Include year | Always include `"2026"` |
| Include audience | `"ทาสแมว"` or `"ทาสหมา"` |
| Thai keywords preferred | `"อาหารแมว"` not `"cat food"` |

### Heading Structure

```
H1: Title (rendered by template, NOT in markdown)
  H2: Main section
    H3: Sub-section
      Content
  H2: Next section
    H3: Sub-section
```

**Rules:**
- Never use H1 in markdown (template renders title as H1)
- Every article must have H2 sections
- H3 for sub-topics within H2
- Don't skip levels (no H2 → H4)
- Include keywords in H2/H3 naturally

### Content Formatting

| Do | Don't |
|---|---|
| Ordered/unordered lists | Code blocks (triple backticks) for content |
| Tables for comparisons | Inline HTML |
| Bold for emphasis | ALL CAPS for emphasis |
| Blockquotes for tips | Images without context |

## Product Page SEO

### Image Alt Tags

| Element | Alt Format |
|---|---|
| Main product image | `alt={seoTitle}` |
| Thumbnail images | `alt="{seoTitle} - ภาพที่ {n}"` |
| Hero deal images | `alt={product.title}` |
| Brand/mascot images | `alt="น้องดีล"` |

### Product Slug Format

**Old (bad)**: `product-76673436-1420780700`
**New (good)**: `royal-canin-indoor-4kg` or `royalcanin-cat-food-4kg`

Rules:
- Generate from product title
- Lowercase, hyphens only
- Include brand + key descriptor
- Max 60 characters
- Always add 301 redirects from old → new slugs in `public/_redirects`

## Meta Tags (BaseLayout.astro)

### Required on all pages

```html
<meta name="description" content="{description}" />
<link rel="canonical" href="{canonicalURL}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:type" content="{website|article}" />
<meta property="og:url" content="{canonicalURL}" />
<meta property="og:image" content="{image}" />
<meta property="og:locale" content="th_TH" />
<meta property="og:site_name" content="PetzDeals" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title}" />
<meta name="twitter:description" content="{description}" />
<meta name="twitter:image" content="{image}" />
```

### og:type by page type

| Page | og:type |
|---|---|
| Homepage, deals, category | `website` |
| Blog articles | `article` |
| Product pages | `website` (with Product schema) |

## Structured Data (JSON-LD)

### Product Pages
- `Product` schema with name, image, description, brand, offers, aggregateRating
- `FAQPage` schema with category-specific Q&A
- `BreadcrumbList` schema

### Blog Pages
- `Article` schema with headline, description, datePublished, dateModified, image, author, publisher, mainEntityOfPage

## AEO (AI Engine Optimization)

### robots.txt
All AI crawlers explicitly allowed:
- GPTBot, ClaudeBot, anthropic-ai, Google-Extended, PerplexityBot, Bingbot, CCBot, cohere-ai, FacebookBot

### Content for AI
- Clear Q&A format in FAQ sections (AI can extract answers)
- Structured data for machine readability
- Clean heading hierarchy for context understanding
- Natural language descriptions (not keyword stuffing)

## New Page Checklist (MANDATORY)

Every time a new page is added to PetzDeals, complete ALL steps before considering it done.

### Before Deploy

| # | Check | How |
|---|---|---|
| 1 | **Title tag** | Unique, keyword-rich, under 60 chars |
| 2 | **Meta description** | 150-160 chars, includes CTA |
| 3 | **H1 heading** | One per page, matches intent |
| 4 | **og:type** | "website" for pages, "article" for blog posts |
| 5 | **og:image** | Set specific image or default `og-default.png` |
| 6 | **Canonical URL** | Auto from BaseLayout — verify no duplicates |
| 7 | **Internal links** | Add to navigation/footer/related sections |
| 8 | **Image alt tags** | Every `<img>` has descriptive alt text |
| 9 | **Structured data** | JSON-LD schema appropriate for page type |
| 10 | **Build passes** | `npx astro build` — 0 errors |

### After Deploy

| # | Check | How | Command/URL |
|---|---|---|---|
| 1 | **Sitemap updated** | Verify new URL is in sitemap-0.xml | `grep "new-page" dist/sitemap-0.xml` |
| 2 | **GSC sitemap resubmit** | Resubmit sitemap via GSC API | See script below |
| 3 | **GSC URL inspection** | Request indexing for new URL | See script below |
| 4 | **GA4 tracking** | Auto via BaseLayout gtag.js — verify in GA4 Realtime | analytics.google.com → Realtime |
| 5 | **GTM container** | Auto via BaseLayout GTM snippet | tagmanager.google.com |
| 6 | **Affiliate links** | All product links use `s.shopee.co.th` (not UTM) | Check with grep |
| 7 | **Navigation link** | New page accessible from nav/footer/related | Click-test on live site |

### GSC Submission Script

```python
import requests

# Get access token
token_resp = requests.post("https://oauth2.googleapis.com/token", data={
    "client_id": "from shopee-affiliate.env",
    "client_secret": "from shopee-affiliate.env",
    "refresh_token": "from shopee-affiliate.env",
    "grant_type": "refresh_token"
})
token = token_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Resubmit sitemap
import urllib.parse
site = "sc-domain:petzdeals.com"
sitemap = "https://petzdeals.com/sitemap-index.xml"
requests.put(
    f"https://www.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(site, safe='')}/sitemaps/{urllib.parse.quote(sitemap, safe='')}",
    headers=headers
)

# Request indexing for new page
requests.post(
    "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
    headers=headers,
    json={"inspectionUrl": "https://petzdeals.com/deals/today/", "siteUrl": site}
)
```

### GTM Event Tracking (for new page types)

If the new page has special interactions (e.g., deal clicks, form submissions), add custom dataLayer events:

```javascript
window.dataLayer.push({
  event: 'deal_click',
  deal_name: 'product title',
  deal_price: 149,
  deal_source: 'shopee-offer'
});
```

Then configure a matching GA4 Event Tag in GTM to capture these events.

## CAR/PAR

### CAR
**Issue**: 7 blog articles had no `tags`, no Twitter Card meta, no `og:locale`, blog `og:type` was "website" not "article", thumbnail images had empty `alt=""`, code blocks rendered ugly in article content.
**Root Cause**: Initial build focused on content and products, SEO meta layer was incomplete.
**Fix**: Added tags to schema + all articles, Twitter Cards, og:locale, dynamic og:type, image alt tags, code block styling. Commit: `25e931e`.
**Date**: 2026-06-29

### PAR
**Prevention**:
1. Content schema enforces required fields (tags now in schema)
2. This SOP must be read before adding new articles
3. QA checks SEO checklist before deploy
4. Blog template has code block styles that match brand (teal/cream, not dark)
5. Default og:image ensures social shares always have a preview image
