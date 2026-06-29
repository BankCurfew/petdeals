# SOP: เพิ่มสินค้าใหม่ — ทำทุกขั้นตอน ห้ามข้าม

> ทุกครั้งที่เพิ่มสินค้าใหม่บน petzdeals.com ต้องทำครบ 10 ขั้นตอนนี้
> ถ้าข้ามขั้นตอนไหน = สินค้านั้นไม่มีค่า SEO = เสียเวลาฟรี

## ขั้นตอนที่ 1: Research คำค้นหา (Researcher)

ก่อนเพิ่มสินค้า ต้องรู้ว่าคนไทยค้นหาอะไรเกี่ยวกับสินค้านี้:

```
1. Search Google: "{ชื่อสินค้า} รีวิว", "{ชื่อสินค้า} ดีไหม"
2. ดู "People Also Ask" — คำถามที่คนถามบ่อย
3. ดู Google Suggest — พิมพ์ "{ชื่อสินค้า}" แล้วดู autocomplete
4. ดู competitors — ใครเขียนเรื่องนี้แล้ว? เขาใช้ H1/H2 อะไร?
5. จด keywords: primary (1), secondary (3-5), long-tail questions (5+)
```

**Output**: keyword list + competitor analysis → ส่งให้ Writer

## ขั้นตอนที่ 2: Scrape ข้อมูลจริง (Data)

```
1. CDP login Shopee → ไปหน้าสินค้า
2. Scrape: ชื่อเต็ม, ราคาจริง (ไม่ใช่ variant ถูกสุด), rating จริง, sold count จริง
3. Download รูปจริง (susercontent.com) — ไม่ใช่ placeholder
4. Scrape: specs, ส่วนผสม, น้ำหนัก, ขนาด
5. Scrape: shop name, shop rating, ship from
6. Generate affiliate link: {url}?utm_source=an_15312860014&utm_medium=affiliates
```

**Output**: product data (JSON) + images → ส่งให้ Writer + Dev

## ขั้นตอนที่ 3: เขียน Content (Writer)

ทุกสินค้าต้องมี content **300-500 คำขึ้นไป** ไม่ใช่แค่ชื่อ+ราคา:

```markdown
H1: {ชื่อสินค้า} — รีวิวจากทาสแมว {ปี}

(Hook 40-60 คำ — ตอบคำถามทันที เพื่อ AEO)

H2: จุดเด่นที่ทาสแมวต้องรู้
- {จุดเด่น 1}
- {จุดเด่น 2}
- {จุดเด่น 3}

H2: ข้อมูลจำเพาะ
| รายละเอียด | ค่า |
|---|---|
| แบรนด์ | {brand} |
| น้ำหนัก | {weight} |
| ส่วนผสมหลัก | {ingredients} |
| เหมาะกับ | {age/type} |
| ราคาเริ่มต้น | ฿{price} |

H2: เหมาะกับเจ้านายแบบไหน
(ใช้สแลง: ทาสแมว, เจ้านาย, น้องเหมียว)

H2: ข้อควรระวัง ⚠️
(ข้อเสีย — builds trust, Google ชอบ honest review)

H2: เปรียบเทียบกับ {competitor brand}
| | {this product} | {competitor} |
|---|---|---|

H2: คำถามที่พบบ่อย
Q: {keyword question from step 1}?
A: {answer 40-60 words}

(CTA: "เช็คราคาให้เจ้านาย →")
(อัพเดทล่าสุด: DD/MM/YYYY)
```

**ห้าม:**
- ❌ Copy จาก Shopee
- ❌ บอกว่าทุกอย่างดีหมด (ต้องมีข้อเสีย)
- ❌ Rating 5.0 ทุกตัว (ใช้ rating จริง)
- ❌ "ดูราคา Shopee" (ใช้ "เช็คราคาล่าสุด")

**Tone**: ทาสแมว เจ้านาย น้องเหมียว — เหมือนเพื่อนที่รู้เรื่องสัตว์เลี้ยง

## ขั้นตอนที่ 4: Editor ตรวจ Content Authority

```
1. ราคาตรงกับ Shopee จริง?
2. Specs ถูกต้อง? (ส่วนผสม น้ำหนัก)
3. Claims มีอ้างอิง? ("ดีที่สุด" ต้องมีหลักฐาน)
4. ชื่อแบรนด์สะกดถูก?
5. ไม่มี content ที่ copy มา?
6. Tone ถูกต้อง? (ทาสแมว/เจ้านาย)
7. CTA ไม่พูด Shopee?
```

## ขั้นตอนที่ 5: Dev สร้าง Page

```
1. สร้าง src/pages/products/{slug}.astro
2. ใส่ H1/H2/H3 structure จาก Writer content
3. JSON-LD Product + FAQPage schema
4. Image: real photo from susercontent.com + alt text SEO
5. CTA: green button "เช็คราคาล่าสุด →" (no Shopee)
6. "อัพเดทล่าสุด: DD/MM/YYYY"
7. Related products section
8. Breadcrumb: หน้าแรก > หมวดหมู่ > สินค้า
```

## ขั้นตอนที่ 6: QA Visual Check (pw-cli)

```bash
pw=~/.oracle/tools/pw-cli.sh
$pw open
$pw goto "https://petzdeals.com/products/{slug}"
$pw screenshot

# Check:
# 1. รูปสินค้าโหลด (ไม่ใช่ placeholder)
# 2. ราคาถูกต้อง
# 3. H1/H2/H3 structure ครบ
# 4. CTA button ทำงาน + ไม่พูด Shopee
# 5. Mobile responsive
# 6. Schema valid (Rich Results Test)
```

## ขั้นตอนที่ 7: Deploy

```bash
bun run build && wrangler pages deploy dist --project-name=petzdeals
```

## ขั้นตอนที่ 8: Submit to Google

```
1. Google Indexing API: submit new URL (max 200/day)
2. IndexNow: submit to Bing/Yandex
3. Verify in GSC: URL Inspection → Request Indexing
```

## ขั้นตอนที่ 9: Monitor

```
1. GSC: ดูว่า page indexed ไหม (1-7 วัน)
2. GA4: ดู views + affiliate_click events
3. Shopee dashboard: ดู commission จาก product นี้
```

## ขั้นตอนที่ 10: Update รายสัปดาห์

```
1. CDP re-scrape ราคา + stock
2. อัพเดท "อัพเดทล่าสุด" date
3. Rebuild + redeploy
```

---

## Checklist สรุป (ต้องครบทุกข้อ)

- [ ] Keyword research done
- [ ] Product data scraped (real price, real rating, real images)
- [ ] Content written (300+ words, H1/H2/H3, FAQ)
- [ ] Thai slang used (ทาสแมว, เจ้านาย)
- [ ] Editor approved (price, specs, claims verified)
- [ ] Page created with JSON-LD schema
- [ ] QA visual check passed (pw-cli screenshot)
- [ ] Deployed to production
- [ ] Submitted to Google
- [ ] Monitoring set up

**ข้ามขั้นตอนไหน = สินค้านั้นไม่มีค่า = เสียเวลา**

---

## Pre-Deploy Review Gate (MANDATORY — แบงค์ ordered)

**ทุก deploy ต้องผ่าน 3 ด่าน:**

| Gate | Reviewer | Checklist |
|---|---|---|
| **1. Editor** | Content accuracy | ราคาตรง, ข้อมูลจริง, brand voice น้องดีล, สแลงทาสแมว, SEO H1/H2/H3, CTA ไม่พูด Shopee |
| **2. QA** | Visual check | pw-cli screenshot, images load, prices correct, mobile responsive, playful elements visible |
| **3. Designer** | Brand consistency | Teal/coral colors, น้องดีล mascot, playful elements (paw prints, แมวเกาะขอบ), ไม่เหมือน Shopee |

**ไม่ผ่านแม้แต่ 1 ด่าน = ไม่ deploy = แก้แล้วส่ง review ใหม่**
