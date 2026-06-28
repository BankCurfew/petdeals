# PETDEALS — Team Responsibilities & Daily Operations

> This is a revenue project — pays our bills. Zero tolerance for missed tasks.

## Team Assignments

| Oracle | Role | Daily Tasks | Accountability |
|---|---|---|---|
| **BoB** | Project Manager | Monitor all oracles, deploy, escalate | Overall revenue target |
| **Data** | CDP Pipeline | Scrape products, update prices, images | Product freshness daily |
| **Dev** | Engineering | Fix bugs, new pages, schema markup | Site uptime + Core Web Vitals |
| **QA** | Quality | Visual QA (pw-cli), link verify, price check | Zero broken links/images |
| **Writer** | Content | Product articles, SEO content, descriptions | 1 article/day minimum |
| **Editor** | Quality | Content authority audit, brand consistency | Zero wrong claims/prices |
| **Designer** | UX/UI | Design improvements, responsive, brand | User experience |
| **Admin** | Infrastructure | GTM/GA4 config, CF deploy, monitoring | Infra uptime |
| **Researcher** | SEO Strategy | Keyword tracking, competitor analysis | Ranking improvements |

## Daily Loops (maw loop)

| Loop ID | Schedule | Oracle | Task |
|---|---|---|---|
| petdeals-qa-daily | 09:00 daily | QA | pw-cli visual check + link verify + price accuracy |
| petdeals-scrape | 02:00 daily | Data | CDP scrape new/trending products |
| petdeals-sync | 04:00 daily | Data | Price/stock sync existing products |
| petdeals-publish | 08:00 daily | BotDev | Publish scheduled content + rebuild + deploy |
| petdeals-analytics | 10:00 daily | Researcher | Check GSC + GA4 + Shopee affiliate stats |
| petdeals-content | 09:00 daily | Writer | Write 1 new article or update existing |

## Analytics — Check Daily

### Google Search Console
- Clicks, impressions, CTR, avg position
- New pages indexed vs submitted
- Coverage errors (404s, crawl issues)
- Core Web Vitals status

### GA4 (G-3TCK9V54XS)
- Active users
- affiliate_click events (→ Shopee)
- Top products by clicks
- Traffic sources (organic, direct, social)
- Conversion: visit → affiliate_click rate

### Shopee Affiliate Dashboard
- Login: affiliate.shopee.co.th (AP_marketing)
- Check: clicks, orders, commission earned
- Cross-reference with GA4 affiliate_click events
- Track: which products earn most commission
- Report weekly to แบงค์

## Revenue Tracking

| Metric | Where | How Often |
|---|---|---|
| Affiliate clicks | GA4 events | Daily |
| Shopee orders | Shopee affiliate dashboard | Daily |
| Commission earned | Shopee affiliate dashboard | Weekly |
| Search rankings | GSC Performance | Weekly |
| Organic traffic | GA4 + GSC | Weekly |
| Revenue vs cost | แบงค์ report | Monthly |

## Analysis Docs

Every week, Researcher produces:
1. **Weekly SEO Report** — rankings, new keywords, competitor moves
2. **Revenue Analysis** — commission earned, top products, conversion rate
3. **Content Performance** — which articles drive traffic, which need updates
4. **Action Items** — what to improve next week

Save to: `ψ/memory/analytics/YYYY-WW_weekly-report.md`

## Enforcement

- **BoB** checks every oracle runs their daily loop
- **QA** visual check is MANDATORY before deploy (pw-cli)
- **Editor** content authority audit every new publish
- Missing loop = violation → escalate
- Wrong data on production = immediate hotfix + CAR

## This Pays Our Bills

> "ถ้าเว็บนี้ไม่ได้เงิน = เราทำไม่ดีพอ" — แบงค์

Every detail matters:
- Every broken image = lost trust = lost click = lost commission
- Every wrong price = lost trust
- Every missing article = lost SEO ranking = lost traffic = lost revenue
- Every day without new content = competitors catch up
