# /petdeals-add-product — Add new product (full SEO pipeline)

One command runs the entire 10-step SOP for adding a product to petzdeals.com.

## Usage
```
/petdeals-add-product "Royal Canin Indoor 2kg"        # Add specific product
/petdeals-add-product --url <shopee-url>               # Add from Shopee URL
/petdeals-add-product --category อาหารแมว --top 5      # Add top 5 from category
```

## What it does (10 steps — ALL mandatory)

1. **Research keywords** — Google "{product} รีวิว", autocomplete, People Also Ask, competitors
2. **CDP scrape** — Login Shopee → product page → real price, rating, sold, images, specs
3. **Write content** — 300+ words: H1/H2/H3, จุดเด่น, specs table, เหมาะกับใคร, ข้อควรระวัง, FAQ
4. **Thai slang** — ทาสแมว, เจ้านาย, น้องเหมียว, เช็คราคาให้เจ้านาย
5. **Editor verify** — price accuracy, specs correct, claims have evidence, no Shopee in CTA
6. **Build page** — Astro SSG with JSON-LD Product + FAQPage schema
7. **QA visual** — pw-cli screenshot, images load, prices correct, mobile responsive
8. **Deploy** — bun build + wrangler pages deploy
9. **Submit Google** — Indexing API + IndexNow
10. **Monitor** — GSC indexed? GA4 clicks? Shopee commission?

## Key Rules
- Content 300+ words minimum per product
- Use ทาสแมว/เจ้านาย slang
- CTA: "เช็คราคาล่าสุด" NOT "ดูราคา Shopee"
- Show "อัพเดทล่าสุด: DD/MM/YYYY"
- Real rating (not all 5.0) + real sold count
- Price: "ราคาเริ่มต้น ฿XXX"
- Compare with competitors (table)
- Include ข้อควรระวัง (honest cons = trust)
- FAQ section with schema

## See also
- `docs/SOP-ADD-PRODUCT.md` — full 10-step SOP
- `docs/SEO-AEO-RESEARCH-2026.md` — structure guide
- `docs/ARTICLE-TEMPLATES.md` — content templates
