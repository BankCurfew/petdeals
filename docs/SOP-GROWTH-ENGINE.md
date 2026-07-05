---
owner: BoB
updated: 2026-07-05
verified: 2026-07-05
status: active
supersedes: none
---
# SOP — PETDEALS Growth Engine (petdeals#22)

> แบงค์'s mandate 2026-07-05: seasonal promo pages always current, an article on every product with all images, full SEO/metadata at all times — **fully automatic. Nobody remembers anything; the loops and gates do.**

## 🇹🇭 IRON RULE — THAI MARKET ONLY (แบงค์ 2026-07-05)
Everything in this engine is strictly Thailand: shopee.co.th only (never .com.br/.sg/.com), Thai-language products/campaigns/articles, THB prices, TH sellers/shipping. Enforced by: TH gate at ingest (country=TH + language validation, Brazil CAR #7), promo scrape targets shopee.co.th hub only, niche seeds must be validated on shopee.co.th before entering sync keywords (global market data = sizing context only, never sourcing).

## The machine (all automatic — no manual steps)

| Time | Loop | Oracle | Does |
|------|------|--------|------|
| 02:00 daily | petdeals-apify-sync | Data | Scrape → TH+category gates → products.json (+slug/source/affiliate/local-images at ingest) → commit+push → Action deploys |
| 08:00 daily | petdeals-gsc-daily | Researcher | GSC coverage/crawl errors + sitemap + submit URLs + **GA4/GTM tags-firing realtime check** + **image spot-check (10 HEAD 200s)** — red → BoB immediately |
| 08:30 Mon | petdeals-seasonal-prep | Data | Campaign ≤10 days out? → verify page populates, guide exists, dates right |
| 09:00 daily | petdeals-promo-check | Data | **Scrape Shopee promotion hub via CDP** (real campaign names/dates/mechanics/banners) → seasons.json + top-deals.json → push; new campaign → cc Writer |
| 09:00 daily | petdeals-content | Writer | Campaign ≤7 days & no guide → write it; else product-cluster article |
| 09:00 daily | petdeals-qa-daily | QA | pw-cli visual sweep, 7 areas |
| 10:00 daily | petdeals-analytics | Researcher | Traffic/affiliate report to BoB |
| 10:00 1st/mo | petdeals-niche-research | Researcher | Rising niches → new keywords/topics → docs/niche-research/ |
| Mon 08:00 | office-canary-weekly | Admin | Incl. Apify credits, CI green, live-page SEO sample |

## Data flow
```
Shopee ──Apify──▶ scrape-offers.py [TH gate·category gate·slug·affiliate·WEBP images]
   ──▶ products.json + seasons.json ──commit/push──▶ GitHub Action ──▶ build
        [SEO CI GATE: every page needs title/desc/canonical/og/schema or BUILD FAILS]
   ──▶ petzdeals.com (product pages + seasonal /deals/[campaign] + articles)
   ──▶ GSC/GA4/Shopee metrics ──▶ Researcher daily report ──▶ niche research loop
```

## AEO (Answer Engine Optimization — every campaign guide)
Campaign guide articles carry: FAQPage schema (top 5 shopper questions), speakable/direct-answer opening paragraph, llms.txt updated with seasonal pages, campaign mechanics stated as facts with dates (AI-quotable). Visuals: campaign banner ref from promo scrape + Designer poster when Wingman schedules.

## Campaign calendar (data/seasons.json — Data owns; promo loop feeds REAL data from Shopee's own promotion page)
Shopee doubles: 8.8, 9.9, 10.10, 11.11, 12.12, 1.1 · payday 15th+25th · seasonal: หน้าร้อน (Mar-May), หน้าฝน (Jun-Oct), ปีใหม่/สงกรานต์. Each entry: id, name, start/end, keywords[], products[] (auto-filled by promo loop).

## Article-per-product (Phase 2 — target state)
Every product page carries generated sections (คุณสมบัติเด่น/เหมาะกับใคร/วิธีเลือก/FAQ/เปรียบเทียบ) rendered from product data at build. New product from nightly sync ⇒ arrives WITH article, local images, complete SEO — zero manual steps. Writer deep-writes top products by clicks.

## Failure handling
- Loop misses/queue stuck → liveness alert to BoB (loop-engine, automatic)
- Build fails SEO gate → Action red → Dev fixes (CI is the enforcement)
- Apify dead/credits out → weekly canary alerts BoB
- Any incident → CAR as GitHub issue labeled `car` (per governance)

## Change rule (Doc-Sync, Rule #15)
Change any pipeline behavior ⇒ update THIS file + the loop prompt in the same commit. The SOP staleness canary (governance WS3) verifies paths/commands in this doc weekly.
