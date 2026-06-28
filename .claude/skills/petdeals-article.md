# /petdeals-article — Generate SEO article from product data

AI-generate a full SEO article (review, comparison, or buying guide) using product data from the database. Articles link to product pages for internal linking.

## Usage
```
/petdeals-article "วิธีเลือกอาหารแมว"           # Generate buying guide
/petdeals-article --type review --category อาหารแมว  # Review top products in category
/petdeals-article --type comparison --products "Royal Canin,Whiskas,Me-O"  # Compare brands
/petdeals-article --schedule "2026-08-15"         # Schedule for future date
```

## Article Types

### 1. Buying Guide (คู่มือเลือกซื้อ)
- 1,500-2,000 words Thai
- Sections: intro (direct answer), factors to consider, top picks, comparison table, FAQ
- Links to 5-8 product pages
- FAQ schema for AEO

### 2. Product Review (รีวิวรวม)
- "รีวิว 10 {category} ยี่ห้อไหนดี {year}"
- Ranked list with pros/cons
- Comparison table
- Each item links to product page + affiliate CTA

### 3. Brand Comparison (เปรียบเทียบ)
- "{Brand A} vs {Brand B} vs {Brand C}"
- Side-by-side specs table
- Verdict by use case
- Links to each brand's product page

## What it does

1. **Query products** from Supabase matching the category/brands
2. **Gather data**: prices, ratings, specs, sold counts
3. **Research keywords**: check what related terms people search
4. **AI generate article** using template (see docs/SYSTEM-DESIGN.md §7)
5. **Add internal links** to product pages
6. **Add affiliate CTAs** to product affiliate URLs
7. **Generate meta**: title, description, keywords, slug
8. **Save to Supabase** articles table with status: 'scheduled'
9. **Report**: article title, word count, product links, scheduled date

## AEO Optimization Rules (built into every article)
- First paragraph = direct answer to the query (Google AI Overview extracts this)
- Specs in HTML tables (structured data AI engines prefer)
- FAQ section at bottom (FAQ schema)
- Comparison tables with clear headers
- dateModified updates when prices change

## Content Quality Rules
- NEVER copy product descriptions from Shopee
- Every article must have unique analysis/opinion
- Include "ข้อควรระวัง" (cautions) — builds trust
- Mention price ranges, not exact prices (they change)
- Link to product pages for exact prices
