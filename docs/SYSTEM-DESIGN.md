# PETDEALS — System Design & Content Pipeline

> How products flow from Shopee API → database → pages → Google.
> Every oracle reads this before working on PETDEALS.

---

## 1. Product Pipeline (Daily Automated)

```
┌─────────────────────────────────────────────────────────────┐
│ SHOPEE API (02:00 daily)                                     │
│ productOfferV2 → search 20 categories × 5 pages × 50/query │
│ = up to 5,000 products/night                                 │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ FILTER                                                       │
│ commission ≥ 4% AND rating ≥ 4.0 AND sold_count ≥ 100       │
│ Remove duplicates (by shopee_item_id)                        │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ ENRICH                                                       │
│ 1. product_item_get → full details (specs, all images)      │
│ 2. generateShortLink → affiliate tracking URL               │
│ 3. AI rewrite → SEO title + description + slug              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ IMAGE PIPELINE                                               │
│ Fetch main image + 3 additional → optimize WebP/AVIF        │
│ Upload to CF R2 → store R2 URL in database                  │
│ NO hotlinking to Shopee (breaks, no CDN control)            │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ SUPABASE (upsert)                                            │
│ New product → status: 'scheduled', scheduled_at: +N days    │
│ Existing → update price, stock, sold_count, commission      │
│ Out of stock → status: 'hidden'                              │
│ Price drop > 20% → flag: 'deal'                              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ PUBLISH (08:00 daily)                                        │
│ 10-20 products/day (staggered, not bulk)                    │
│ Set status: 'published'                                      │
│ Trigger Astro rebuild → CF Pages deploy                     │
│ Submit to Google Indexing API (max 200/day)                  │
│ Submit to IndexNow (Bing/Yandex)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Page Structure & URL Mapping

### Site Map

```
petzdeals.com/
├── index                          → Homepage (hero, best sellers, categories, deals)
├── อาหารแมว/                      → Category: cat food
│   ├── index                      → Category listing (filtered products)
│   ├── royal-canin-indoor-2kg     → Product detail page
│   └── whiskas-tuna-3kg           → Product detail page
├── อาหารสุนัข/                    → Category: dog food
├── ของเล่นแมว/                    → Category: cat toys
├── ของเล่นสุนัข/                  → Category: dog toys
├── อุปกรณ์ดูแล/                   → Category: grooming
├── ที่นอน/                        → Category: beds
├── สายจูง/                        → Category: leashes & collars
├── เครื่องให้อาหาร/                → Category: auto feeders
├── กรงและกระเป๋า/                 → Category: crates & carriers
├── สุขภาพ/                        → Category: health supplements
├── บทความ/                        → Articles hub
│   ├── index                      → Article listing
│   ├── วิธีเลือกอาหารแมว-2026     → Review article
│   └── เปรียบเทียบ-royal-canin-vs-whiskas → Comparison article
├── แบรนด์/                        → Brands hub
│   ├── royal-canin               → Brand page (all Royal Canin products)
│   └── hills                     → Brand page
├── ดีล/                           → Deals page (price drops > 20%)
├── search                        → Client-side search
├── sitemap-index.xml             → Sitemap index
├── sitemap-products.xml          → Product sitemap
├── sitemap-articles.xml          → Article sitemap
├── sitemap-categories.xml        → Category sitemap
└── robots.txt                    → Crawler rules
```

### URL Rules

| Page Type | URL Pattern | Example |
|---|---|---|
| Homepage | `/` | petzdeals.com |
| Category | `/{category-slug}/` | petzdeals.com/อาหารแมว/ |
| Product | `/{category-slug}/{product-slug}` | petzdeals.com/อาหารแมว/royal-canin-indoor-2kg |
| Article | `/บทความ/{article-slug}` | petzdeals.com/บทความ/วิธีเลือกอาหารแมว-2026 |
| Brand | `/แบรนด์/{brand-slug}` | petzdeals.com/แบรนด์/royal-canin |
| Deals | `/ดีล/` | petzdeals.com/ดีล/ |
| Search | `/search?q={term}` | petzdeals.com/search?q=อาหารแมว |

- Category slugs: **Thai** (for SEO — Thai users search in Thai)
- Product slugs: **English** (readable when shared on LINE/Facebook)
- Always trailing slash on categories, no trailing slash on products

---

## 3. Categories (Pet Supplies Taxonomy)

| ID | Thai Name | English Slug | Icon | Shopee Keywords |
|---|---|---|---|---|
| 1 | อาหารแมว | cat-food | 🐱 | อาหารแมว, cat food, อาหารเปียกแมว, อาหารเม็ดแมว |
| 2 | อาหารสุนัข | dog-food | 🐕 | อาหารสุนัข, dog food, อาหารหมา |
| 3 | ของเล่นแมว | cat-toys | 🎾 | ของเล่นแมว, cat toy, คอนโดแมว, ที่ลับเล็บแมว |
| 4 | ของเล่นสุนัข | dog-toys | 🦴 | ของเล่นสุนัข, dog toy, ลูกบอลสุนัข |
| 5 | อุปกรณ์ดูแล | grooming | ✂️ | แปรงขน, ที่ตัดเล็บ, แชมพูสุนัข, แชมพูแมว |
| 6 | ที่นอนสัตว์เลี้ยง | beds | 🛏️ | ที่นอนแมว, ที่นอนสุนัข, เบาะสัตว์เลี้ยง |
| 7 | สายจูงและปลอกคอ | leashes | 🦮 | สายจูง, ปลอกคอ, สายรัด harness |
| 8 | เครื่องให้อาหารอัตโนมัติ | auto-feeders | ⚙️ | เครื่องให้อาหาร, น้ำพุแมว, automatic feeder |
| 9 | กรงและกระเป๋า | carriers | 🧳 | กรงสัตว์เลี้ยง, กระเป๋าแมว, carrier |
| 10 | สุขภาพ | health | 💊 | วิตามินสัตว์เลี้ยง, ยาหยอดเห็บ, supplement |
| 11 | ทรายแมว | cat-litter | 🪣 | ทรายแมว, cat litter, ห้องน้ำแมว |
| 12 | ชุดเดินทาง | travel | 🚗 | คาร์ซีทสุนัข, กระเป๋าเดินทาง, travel pet |

---

## 4. Product Data Template

### What Shopee API returns (basic):

```json
{
  "itemId": 12345678,
  "shopId": 87654321,
  "itemName": "อาหารแมว Royal Canin Indoor 2kg แพ็ค x3 ส่งฟรี!!!",
  "price": 45900,
  "originalPrice": 59900,
  "image": "https://cf.shopee.co.th/file/xxxxx",
  "commissionRate": 0.042,
  "sales": 1523,
  "ratingStar": 4.7,
  "shopName": "RoyalCaninOfficialTH"
}
```

### What we store (enriched):

```json
{
  "id": "uuid",
  "shopee_item_id": 12345678,
  "shopee_shop_id": 87654321,
  "title_th": "อาหารแมว Royal Canin Indoor 2kg แพ็ค x3 ส่งฟรี!!!",
  "title_seo": "อาหารแมว Royal Canin Indoor 2kg — สูตรแมวเลี้ยงในบ้าน ลดกลิ่นอึ",
  "slug": "royal-canin-indoor-cat-food-2kg",
  "description": "อาหารเม็ดสำหรับแมวเลี้ยงในบ้าน อายุ 1 ปีขึ้นไป...(AI generated, 150-300 words)",
  "price": 459,
  "original_price": 599,
  "discount_percent": 23,
  "commission_rate": 4.2,
  "category_id": 1,
  "brand": "Royal Canin",
  "image_url": "https://r2.petzdeals.com/products/royal-canin-indoor-2kg-main.webp",
  "images": [
    "https://r2.petzdeals.com/products/royal-canin-indoor-2kg-1.webp",
    "https://r2.petzdeals.com/products/royal-canin-indoor-2kg-2.webp"
  ],
  "affiliate_url": "https://shp.ee/xxxxx",
  "rating": 4.7,
  "sold_count": 1523,
  "stock_status": "in_stock",
  "specs": {
    "weight": "2kg",
    "flavor": "ไก่",
    "age_range": "1+ ปี",
    "type": "อาหารเม็ด"
  },
  "publish_status": "published",
  "published_at": "2026-07-05T08:00:00Z",
  "last_synced_at": "2026-07-10T02:00:00Z"
}
```

### SEO Title Rewrite Rules

| Bad (Shopee original) | Good (SEO optimized) |
|---|---|
| อาหารแมว Royal Canin 2kg แพ็ค x3 ส่งฟรี!!! | อาหารแมว Royal Canin Indoor 2kg — สูตรแมวเลี้ยงในบ้าน ลดกลิ่นอึ |
| 🔥ของเล่นแมว MEGA SALE 50% OFF🔥 | ของเล่นแมว Tower Ball — หอคอย 3 ชั้น ลูกบอลหมุน ออกกำลังกาย |
| ที่นอนสุนัข size S-XL ราคาถูก [COD] | ที่นอนสุนัข Memory Foam ไซส์ M — รองรับน้ำหนัก กันไรฝุ่น |

**Rules:**
1. Remove emoji, ALL CAPS, !!!, 🔥, spam keywords
2. Add benefit/feature after product name
3. Keep brand name
4. 60-70 characters max (Google truncates at ~60)
5. Format: `{product} {brand} {size} — {benefit}`

### Description Template (by category)

```markdown
## อาหารสัตว์เลี้ยง Template
{product_name} จาก {brand} เป็น{type}สำหรับ{animal} {age_range}

**จุดเด่น:**
- {benefit_1}
- {benefit_2}
- {benefit_3}

**เหมาะสำหรับ:** {target_audience}

**ข้อมูลโภชนาการ:** {nutrition_info — from specs if available}

**ขนาด:** {weight/size} | **ราคา:** ฿{price} (ลด {discount}% จาก ฿{original_price})

⭐ {rating}/5 จาก {sold_count} รีวิว
```

```markdown
## อุปกรณ์/ของเล่น Template
{product_name} จาก {brand} — {one_line_benefit}

**คุณสมบัติ:**
- {feature_1}
- {feature_2}
- {feature_3}

**วัสดุ:** {material}
**ขนาด:** {dimensions}
**เหมาะกับ:** {animal_type} {size_range}

**ข้อควรระวัง:** {caution — if applicable}

⭐ {rating}/5 | ขายแล้ว {sold_count} ชิ้น
```

---

## 5. Image Pipeline Detail

### Fetch Process

```
1. Shopee API returns image URL: https://cf.shopee.co.th/file/{hash}
2. CF Worker fetches original image (max 5 images per product)
3. Process:
   - Main image → 800x800 WebP (product card) + 400x400 WebP (thumbnail)
   - Additional images → 800x800 WebP only
   - All images: quality 85, strip metadata
4. Upload to R2: petzdeals-images/{category}/{product-slug}-{n}.webp
5. Store R2 URL in Supabase products.image_url and products.images[]
```

### Image Naming Convention

```
R2 path: products/{category-slug}/{product-slug}-main.webp
         products/{category-slug}/{product-slug}-1.webp
         products/{category-slug}/{product-slug}-2.webp

Example:
  products/cat-food/royal-canin-indoor-2kg-main.webp
  products/cat-food/royal-canin-indoor-2kg-1.webp
```

### Image Optimization Targets

| Metric | Target | Why |
|---|---|---|
| Format | WebP (AVIF fallback) | 30% smaller than JPEG |
| Main image | 800x800, < 50KB | Product detail page |
| Thumbnail | 400x400, < 20KB | Product cards |
| Quality | 85% | Good enough, small file |
| Lazy loading | Below-fold images | Core Web Vitals |

---

## 6. Article & Product Linking Strategy

### How Articles Link to Products

```
Article: "วิธีเลือกอาหารแมว — คู่มือฉบับสมบูรณ์ 2026"
  ↓ mentions specific products
  → Link to: /อาหารแมว/royal-canin-indoor-2kg (internal link)
  → Link to: /อาหารแมว/whiskas-tuna-3kg (internal link)
  → CTA: "ดูอาหารแมวทั้งหมด" → /อาหารแมว/ (category link)

Product: /อาหารแมว/royal-canin-indoor-2kg
  ↓ related content section
  → Link to: /บทความ/วิธีเลือกอาหารแมว-2026 (article link)
  → Link to: /บทความ/เปรียบเทียบ-royal-canin-vs-whiskas (comparison link)
  → "สินค้าที่คุณอาจสนใจ" → 4 related products (same category)
```

### Internal Linking Architecture

```
Homepage
  ├── → Top categories (6 cards)
  ├── → Best sellers (8 product cards)
  ├── → Latest articles (3 cards)
  └── → Current deals

Category Page (/อาหารแมว/)
  ├── → Breadcrumb: หน้าแรก > อาหารแมว
  ├── → Product cards (paginated, 20/page)
  ├── → Filter: brand, price range, rating
  ├── → Related articles sidebar
  └── → Sub-categories (if any)

Product Page (/อาหารแมว/royal-canin-indoor-2kg)
  ├── → Breadcrumb: หน้าแรก > อาหารแมว > Royal Canin Indoor 2kg
  ├── → Main CTA: "เช็คราคา & สั่งซื้อ (Shopee)" → affiliate link
  ├── → Product specs table
  ├── → AI-generated description
  ├── → Related articles
  ├── → Similar products (4 cards)
  └── → Brand page link

Article Page (/บทความ/วิธีเลือกอาหารแมว-2026)
  ├── → Breadcrumb: หน้าแรก > บทความ > วิธีเลือกอาหารแมว
  ├── → Table of Contents
  ├── → Inline product mentions → link to product pages
  ├── → Product comparison table → link to each product
  ├── → CTA sections → affiliate links
  ├── → FAQ section (FAQ schema)
  └── → Related articles
```

### Content Calendar Template (3-Month)

| Week | Products/Day | Articles | Article Topics |
|---|---|---|---|
| 1-2 | 10 | 2 guides | "วิธีเลือกอาหารแมว", "อุปกรณ์จำเป็นเลี้ยงแมวครั้งแรก" |
| 3-4 | 15 | 3 reviews | "รีวิว 10 เครื่องให้อาหารอัตโนมัติ", "5 ทรายแมวยอดนิยม" |
| 5-6 | 15 | 2 comparisons | "Royal Canin vs Whiskas vs Me-O", "เปรียบเทียบน้ำพุแมว 5 ยี่ห้อ" |
| 7-8 | 20 | 3 mixed | Seasonal content (หน้าร้อน/หน้าฝน tips) |
| 9-10 | 20 | 2 guides | "วิธีเลือกสายจูง", "แชมพูสุนัขยี่ห้อไหนดี" |
| 11-12 | 20 | 3 reviews | Brand deep-dives, new product launches |

**Total Month 1-3:** ~500 products + ~15 articles

---

## 7. Article Types & Templates

### Type 1: Buying Guide (คู่มือเลือกซื้อ)

```markdown
# วิธีเลือก{product_category} — คู่มือฉบับสมบูรณ์ {year}

{1 paragraph direct answer — for AEO citation}

## สารบัญ
1. {product_category}คืออะไร
2. ปัจจัยที่ต้องดูก่อนซื้อ
3. {N} {product_category} แนะนำ
4. ตารางเปรียบเทียบ
5. คำถามที่พบบ่อย

## {product_category}คืออะไร
{explanation paragraph}

## ปัจจัยที่ต้องดูก่อนซื้อ
### 1. {factor_1}
### 2. {factor_2}
### 3. {factor_3}

## {N} {product_category} แนะนำ {year}
### 1. {product_name} — {benefit}
{review paragraph}
[➡️ เช็คราคาที่ Shopee](affiliate_link)

## ตารางเปรียบเทียบ
| สินค้า | ราคา | คะแนน | จุดเด่น |
|---|---|---|---|

## คำถามที่พบบ่อย (FAQ)
**Q: {question_1}?**
A: {answer_1}

**Q: {question_2}?**
A: {answer_2}
```

### Type 2: Product Comparison (เปรียบเทียบ)

```markdown
# เปรียบเทียบ {brand_a} vs {brand_b} [vs {brand_c}] — {year}

{1 paragraph verdict — for AEO}

## ตารางเปรียบเทียบ
| | {brand_a} | {brand_b} | {brand_c} |
|---|---|---|---|
| ราคา | ฿{price} | ฿{price} | ฿{price} |
| คะแนน | ⭐{rating} | ⭐{rating} | ⭐{rating} |
| จุดเด่น | {pro} | {pro} | {pro} |
| จุดด้อย | {con} | {con} | {con} |
| เหมาะกับ | {audience} | {audience} | {audience} |

## รีวิวแต่ละตัว
### {brand_a}
### {brand_b}
### {brand_c}

## สรุป: ควรเลือกตัวไหน?
{verdict based on use case}
```

### Type 3: Top-N Review (รีวิวรวม)

```markdown
# รีวิว {N} {product_category} ยี่ห้อไหนดี {year}

{1 paragraph summary — for AEO}

## {N} อันดับ {product_category} แนะนำ

### 1. 🥇 {product} — ดีที่สุดโดยรวม
### 2. 🥈 {product} — คุ้มค่าที่สุด
### 3. 🥉 {product} — premium ที่สุด
...

## ตารางเปรียบเทียบทั้ง {N} ตัว
| อันดับ | สินค้า | ราคา | คะแนน | เหมาะกับ |
|---|---|---|---|---|

## FAQ
```

---

## 8. Schema Markup Templates

### Product Page JSON-LD

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{title_seo}",
  "image": ["{image_url}"],
  "description": "{description — first 200 chars}",
  "brand": {
    "@type": "Brand",
    "name": "{brand}"
  },
  "offers": {
    "@type": "Offer",
    "url": "{affiliate_url}",
    "priceCurrency": "THB",
    "price": "{price}",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "Shopee Thailand"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{rating}",
    "reviewCount": "{sold_count}"
  }
}
```

### Article Page JSON-LD

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "image": "{featured_image}",
  "author": {
    "@type": "Organization",
    "name": "PETDEALS"
  },
  "datePublished": "{published_at}",
  "dateModified": "{updated_at}",
  "publisher": {
    "@type": "Organization",
    "name": "PETDEALS",
    "logo": {
      "@type": "ImageObject",
      "url": "https://petzdeals.com/logo.png"
    }
  }
}
```

### FAQ Schema (on article pages)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{question}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{answer}"
      }
    }
  ]
}
```

---

## 9. Daily Operations Schedule

| Time (GMT+7) | What | Worker/Oracle |
|---|---|---|
| 02:00 | Product sync — fetch new products from Shopee API | CF Worker (product-sync) |
| 03:00 | Image pipeline — fetch + optimize + upload to R2 | CF Worker (image-fetch) |
| 04:00 | Price/stock sync — update existing products | CF Worker (product-sync) |
| 05:00 | AI content — generate SEO titles + descriptions for new products | CF Worker or Oracle (Writer) |
| 08:00 | Publish — release scheduled products + trigger rebuild | CF Worker (scheduler) |
| 08:30 | Index — submit new URLs to Google Indexing API + IndexNow | CF Worker (indexing) |
| 09:00 | Monitor — check build success, page count, errors | Admin Oracle |

---

## 10. API Rate Limits & Quotas

| API | Limit | Our Daily Usage | Buffer |
|---|---|---|---|
| Shopee productOfferV2 | ~100 req/min | ~2,000 req (02:00-04:00) | 85% headroom |
| Shopee generateShortLink | ~100 req/min | ~500 req (new products only) | 95% headroom |
| Google Indexing API | 200 publish/day | 10-20 new URLs/day | 90% headroom |
| Google Indexing API | 600 total/day | ~50 total/day | 91% headroom |
| CF Pages builds | 500/month | 30-60/month | 88% headroom |
| CF R2 Class A ops | 1M/month free | ~10K/month | 99% headroom |
| CF R2 storage | 10GB free | ~2-5GB | 50-75% headroom |
| CF Workers requests | 100K/day free | ~5K/day | 95% headroom |

### Rate Limit Handling

```typescript
// Exponential backoff on Shopee error 10030
async function shopeeRequest(query, retries = 3) {
  for (let i = 0; i < retries; i++) {
    const res = await fetch(SHOPEE_API_URL, { ... });
    if (res.status === 429 || res.error_code === 10030) {
      await sleep(Math.pow(2, i) * 1000); // 1s, 2s, 4s
      continue;
    }
    return res;
  }
  throw new Error('Rate limit exceeded after retries');
}
```

---

## 11. Update Strategy — What Gets Updated When

| Data | Frequency | Trigger | Action |
|---|---|---|---|
| New products | Daily 02:00 | Cron | Search API → filter → enrich → schedule |
| Prices | Daily 04:00 | Cron | Check all published → update if changed |
| Stock status | Daily 04:00 | Cron | out_of_stock → hide, back_in_stock → show |
| Images | On new product | Pipeline | Fetch → optimize → R2 |
| Affiliate links | On new product | Pipeline | generateShortLink → store |
| SEO titles | On new product | AI pipeline | Rewrite → store |
| Descriptions | On new product | AI pipeline | Generate → store |
| Articles | 1/day (scheduled) | Cron 08:00 | Publish from scheduled queue |
| Sitemap | On every build | Astro build | Auto-regenerate |
| Google index | After publish | Cron 08:30 | Submit new URLs |

---

## Oracle Responsibilities

| Oracle | What They Own | When |
|---|---|---|
| **Data** | Shopee API client, product sync worker, image pipeline, DB schema | Phase 1-2 |
| **Dev** | Astro project, components, layouts, schema markup, SSG | Phase 1, 3 |
| **BotDev** | Affiliate link gen, content scheduler, auto-rebuild trigger | Phase 1, 4 |
| **Designer** | Brand identity, dark theme, product cards, responsive UI | Phase 0-1 |
| **Admin** | CF Pages/R2/Workers, DNS, GTM, GA4, Search Console, cron | Phase 1, 3 |
| **Writer** | Product description templates, articles, SEO titles style guide | Phase 2-3 |
| **Researcher** | Keyword research, content calendar, competitor monitoring | Phase 2-3 |
| **QA** | Schema validation, mobile test, speed test, affiliate link test | Phase 5 |
| **DocCon** | Content quality audit, SEO checklist compliance | Phase 5 |
