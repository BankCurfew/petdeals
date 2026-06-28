# PETDEALS — SEO Content Style Guide

> วิธีเขียน content ให้ติด top Google + Google AI Overview
> ใช้ร่วมกับ CONTENT-GUIDELINES.md และ SYSTEM-DESIGN.md

## 1. Hook Writing — First 40-60 Words = ตัวตัดสิน

Google AI Overview ดึง content จากย่อหน้าแรก → ต้องตอบคำถามทันที

### Product Page Hook Template
```
{product_name} จาก {brand} เป็น{type}สำหรับ{animal}ที่ {key_benefit}
ราคาเริ่มต้น ฿{price} คะแนน ⭐{rating} จากผู้ซื้อกว่า {sold_count} คน
เหมาะกับ{target_audience} ที่ต้องการ{need}
```

**ตัวอย่าง:**
> อาหารแมว Royal Canin Indoor 2kg เป็นอาหารเม็ดสำหรับแมวเลี้ยงในบ้านอายุ 1 ปีขึ้นไป ช่วยลดกลิ่นอึและควบคุมน้ำหนัก ราคาเริ่มต้น ฿459 คะแนน ⭐4.7 จากผู้ซื้อกว่า 1,500 คน เหมาะกับทาสแมวที่เลี้ยงน้องในคอนโดหรือบ้านที่ไม่ค่อยได้ออกกำลังกาย

### Article Hook Template
```
{direct_answer_to_query} — {supporting_fact_with_number}
ในบทความนี้เราเปรียบเทียบ {N} ตัวเลือกยอดนิยม พร้อมตารางเปรียบเทียบราคา คุณสมบัติ
และรีวิวจากผู้ใช้จริง เพื่อช่วยคุณเลือก{product}ที่เหมาะกับน้อง{animal}ของคุณ
```

## 2. Page Structure

### Product Page
```
H1: {SEO title — 60 chars max}
├── Hook paragraph (40-60 words)
├── Product image gallery
├── Price + discount + CTA "ดูราคาใน Shopee"
├── H2: จุดเด่นของ {product}
│   └── 3-5 bullet points
├── H2: ข้อมูลจำเพาะ
│   └── Specs table
├── H2: เหมาะกับใคร / ไม่เหมาะกับใคร
├── H2: สินค้าที่คล้ายกัน (4 cards)
├── H2: คำถามที่พบบ่อย (FAQ 3-5 ข้อ)
└── CTA: "เช็คราคาล่าสุดที่ Shopee →"
```

### Article Page
```
H1: {keyword-rich title — question format}
├── Hook (40-60 words direct answer — AEO target)
├── Table of Contents
├── H2: sections (question format, answer block 40-60 words each)
├── H2: ตารางเปรียบเทียบ (HTML table)
├── H2: สรุป — ควรเลือกตัวไหน?
├── H2: คำถามที่พบบ่อย (FAQ 5-7 ข้อ)
└── CTA section with product links
```

### Content Length
- Product pages: 300-500 words
- Articles: 1,500-2,000 words
- Category pages: 200-300 words intro + product grid

## 3. Tone & Branding

**Voice:** "เพื่อนที่รู้เรื่องสัตว์เลี้ยง" — ไม่ใช่ร้านขายของ

| Do | Don't |
|---|---|
| "อาหารตัวนี้เหมาะกับน้องแมวที่..." | "ซื้อเลย! ลดราคา! ด่วน!" |
| "จากประสบการณ์ ถ้าน้องเป็นแมวในบ้าน..." | "สินค้าขายดีอันดับ 1!!!" |
| "ข้อควรระวัง: แมวบางตัวอาจไม่ชอบ..." | ไม่พูดถึงข้อเสียเลย |
| ใช้ "น้องแมว/น้องหมา" (warm) | ใช้ "สัตว์เลี้ยง" ทุกที่ (cold) |

**Thai language:**
- คำลงท้าย: "ค่ะ/ครับ" ใน FAQ, "นะ/นะคะ" ใน recommendations
- Casual but trustworthy
- Emoji: 🐱🐕 ใน headings OK, ไม่ใช้ใน body text
- ตัวเลข: ฿459, 4.7 คะแนน (ไม่ใช่ตัวหนังสือ)

## 4. SEO Writing Rules

### Keyword Placement (mandatory)
1. **Title tag** — primary keyword first
2. **H1** — match title, one per page
3. **First 100 words** — primary keyword naturally
4. **H2s** — secondary keywords / question format
5. **Image alt text** — `"อาหารแมว Royal Canin Indoor 2kg ถุง"`
6. **URL slug** — English: `/cat-food/royal-canin-indoor-2kg`
7. **Meta description** — 150 chars Thai, include CTA

### Keyword Density: 1-2% max (natural)

### LSI Keywords for Pet Niche
สัตว์เลี้ยง, อาหารเม็ด, อาหารเปียก, บำรุงขน, ลดกลิ่น, โปรตีนสูง, ไม่เค็ม, ดีต่อไต, วิตามิน, ทาสแมว, คนรักหมา

### Internal Linking
- Article → 5-8 product page links
- Product → 2-3 related articles
- Product → 4 similar products
- Category → all products + 2-3 articles

### Meta Description Formula
```
{product/topic} — {benefit} ราคาเริ่ม ฿{price} ⭐{rating} | เปรียบเทียบ+รีวิวจริง {year} ✓ {CTA}
```

## 5. AEO Optimization

**40-60 word answer blocks** after every H2 — self-contained, extractable.

**FAQ schema (JSON-LD) — 5-7 questions per page:**
```json
{
  "@type": "Question",
  "name": "อาหารแมวยี่ห้อไหนดีที่สุด 2026",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "อาหารแมวที่ดีที่สุดในปี 2026 ขึ้นอยู่กับความต้องการ: Royal Canin Indoor สำหรับแมวในบ้าน..."
  }
}
```

**Comparison tables = HTML `<table>` ไม่ใช่ image** — AI extracts structured data

## 6. CTA Text Options

| Context | Thai CTA |
|---|---|
| Product main | ดูราคาล่าสุดใน Shopee → |
| Product secondary | เช็คโปรโมชั่น Shopee |
| In-article | ดูรายละเอียดเพิ่มเติม → |
| Comparison winner | เช็คราคา {brand} ใน Shopee → |
| Deal | รับส่วนลด {X}% ที่ Shopee → |
| Category | ดู{category}ทั้งหมด ({N} รายการ) |
