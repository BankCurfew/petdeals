# PETDEALS — Full Vision Spec (แบงค์ 29 มิ.ย.)

> ทุก oracle อ่าน — นี่คือ direction ครบทุกมิติ

## 1. Product Detail Pages — ทุกสินค้าต้องมี
- Specs จริง (ส่วนผสม, โปรตีน, แคลอรี่ จากฉลาก)
- Description จริง (จาก Shopee + เขียนเพิ่ม style น้องดีล)
- Reviews จริง (scrape จาก Shopee)
- Rating + sold count จริง (Apify data)
- Images + VDO จาก Shopee (ดึงมาทุกอย่าง)
- Template สวยงาม เหมือนกันทุกหน้า — branding ต้องดี

## 2. Content — บทความ style น้องดีล
- 3000+ words per category article
- Tone: "เด็ดมาอีกแล้วเจ้าทาส! จงกดซื้อให้ข้า เหมี๊ยว" / "ดะดะดะ ดีลลล!"
- H1/H2/H3 SEO structure + FAQ schema
- Keyword database (docs/KEYWORD-DATABASE.md)
- Real specs จากฉลากจริง (Researcher data)

## 3. Promotions — scrape + เขียน content
- Scrape โปรโมชั่น Shopee ทุกวัน (voucher, flash deal, campaign)
- **เฉพาะหมวดหมู่ pet** + **รวมทั้งหมดที่เกี่ยวกับเรา**
- เขียนบทความ **เทคนิคใช้โค้ด voucher ยังไงให้คุ้ม**
- เมื่อไหร่มีโปรอะไร วันไหนต่างๆ
- แยกเป็นบทความ: "วิธีใช้โค้ด Shopee ให้ได้ส่วนลดสูงสุด"
- **Hero banner** จากรูป Shopee promo จริง

## 4. Compare Table — ซื้อจากเราถูกที่สุด!
- ตารางเปรียบเทียบราคา: PetzDeals vs ร้านอื่น vs หน้าร้าน
- แต่ละสินค้า — "ซื้อผ่าน PetzDeals ถูกที่สุด!"
- ราคา Shopee vs Lazada vs ร้านสัตว์เลี้ยง
- + voucher code ลดเพิ่ม = ราคาสุดท้ายถูกกว่า

## 5. Images + Video
- ดึง VDO + Images จาก Shopee product ทุกตัว
- จัดไม่ให้รก — template สวยงามเหมือนกัน
- Image gallery + video player ใน product detail
- Branding ดี — คนจดจำ

## 6. Mobile Responsive + Branding
- เช็ค mobile responsive ทุกหน้า
- สี branding consistent: teal + coral + green CTA
- ไม่เหมือน Shopee
- น้องดีล mascot ทุกหน้า

## 7. Google Ecosystem
- GTM → GA4 → GSC เชื่อมกันหมด
- JSON-LD Product + FAQ + Article schema
- affiliate_click events tracking
- Sitemap submitted + indexed

## 8. Daily Operations (loops)
- petdeals-qa-daily (09:00) — visual QA
- petdeals-analytics (10:00) — GSC + GA4 + Shopee dashboard
- petdeals-content (09:00) — 1 article/day
- petdeals-promo-check (09:00) — Shopee promos
- petdeals-apify-scrape (02:00) — daily product update

## Oracle Assignments

| Oracle | Deliverable |
|---|---|
| **Data** | Apify scrape (products + details + reviews + promos + images + videos) |
| **Writer** | Articles 3000+ words น้องดีล voice + voucher technique articles |
| **Dev** | Product detail template + compare table + video player + mobile responsive |
| **Designer** | Hero banners + branding consistency + template design |
| **Researcher** | Keyword mapping + price comparison data + promo calendar |
| **Editor** | Content authority + brand voice + data accuracy |
| **QA** | Visual QA (pw-cli) + mobile + link verify |
