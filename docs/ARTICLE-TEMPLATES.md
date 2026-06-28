# Article Templates — PETDEALS

> Every product MUST have article content (แบงค์ ordered).

## Per-Product Article

Every product page links to a mini-article (150-300 words) covering:

```markdown
## {product_name} — รีวิวและข้อมูลครบ

{hook: 40-60 words direct answer — AEO target}

### จุดเด่น
- {benefit_1}
- {benefit_2}
- {benefit_3}

### เหมาะสำหรับ
{target audience — which pets, which owners}

### ข้อควรระวัง
{caution — builds trust}

### ข้อมูลจำเพาะ
| รายละเอียด | ค่า |
|---|---|
| แบรนด์ | {brand} |
| ขนาด | {size/weight} |
| ส่วนผสมหลัก | {ingredients} |
| เหมาะกับ | {animal type + age} |

### คำถามที่พบบ่อย
**Q: {question}?**
A: {answer}

[เช็คราคาล่าสุดที่ Shopee →](affiliate_link)
```

## Category Buying Guide (1,500-2,000 words)

```markdown
# วิธีเลือก{category} — คู่มือฉบับสมบูรณ์ {year}

{hook: direct answer in 40-60 words}

## สารบัญ

## {category}คืออะไร

## ปัจจัยที่ต้องดูก่อนซื้อ
### 1. {factor}
### 2. {factor}

## {N} {category} แนะนำ {year}
### 1. 🥇 {product} — ดีที่สุดโดยรวม
[เช็คราคา Shopee →](link)

## ตารางเปรียบเทียบ
| สินค้า | ราคา | คะแนน | เหมาะกับ |
|---|---|---|---|

## คำถามที่พบบ่อย (FAQ schema)
**Q: {question}?**
A: {answer}
```

## Brand Comparison (1,000-1,500 words)

```markdown
# เปรียบเทียบ {A} vs {B} vs {C} — {year}

{verdict in 40-60 words}

## ตารางเปรียบเทียบ
| | {A} | {B} | {C} |
|---|---|---|---|
| ราคา | | | |
| คะแนน | | | |
| จุดเด่น | | | |
| เหมาะกับ | | | |

## สรุป: ควรเลือกตัวไหน?
```

## Top-N Review (1,500-2,000 words)

```markdown
# รีวิว {N} {category} ยี่ห้อไหนดี {year}

{summary 40-60 words}

### 1. 🥇 {product} — ดีที่สุดโดยรวม
### 2. 🥈 {product} — คุ้มค่าที่สุด
### 3. 🥉 {product} — premium ที่สุด

## FAQ
```

## Internal Linking Rules

Every piece of content must link to other content on the site:

| From | To | How Many |
|---|---|---|
| Product page | Related articles | 2-3 links |
| Product page | Similar products (same category) | 4 cards |
| Product page | Brand page | 1 link |
| Article | Product pages (in-context mentions) | 5-8 links |
| Article | Related articles | 2-3 links |
| Article | Category page | 1 link (CTA) |
| Category page | All products | Full grid |
| Category page | Relevant articles | 2-3 sidebar links |

### Link Format

```html
<!-- In-article product mention -->
<a href="/อาหารแมว/royal-canin-indoor-2kg">อาหารแมว Royal Canin Indoor</a>

<!-- CTA to Shopee (affiliate) -->
<a href="{affiliate_url}" rel="nofollow sponsored" target="_blank">
  เช็คราคาล่าสุดที่ Shopee →
</a>

<!-- Related article -->
<a href="/บทความ/วิธีเลือกอาหารแมว-2026">วิธีเลือกอาหารแมว</a>
```

### Affiliate Link Attributes

All outbound Shopee links MUST have: `rel="nofollow sponsored"` and `target="_blank"`.
Internal links: no rel attribute, no target.

## Content by Category

| Category | Product Description Focus | Article Ideas |
|---|---|---|
| อาหารแมว | ส่วนผสม, โปรตีน, เหมาะกับแมวแบบไหน | "วิธีเลือกอาหารแมว", "Royal Canin vs Whiskas" |
| อาหารสุนัข | ขนาด/พันธุ์ที่เหมาะ, สารอาหาร | "อาหารสุนัขพันธุ์เล็ก vs ใหญ่" |
| ของเล่นแมว | วัสดุ, ความทนทาน, ออกกำลังกาย | "10 ของเล่นแมวยอดนิยม" |
| ทรายแมว | ชนิด (เบนโท/เต้าหู้/คริสตัล), ดูดกลิ่น | "เปรียบเทียบทรายแมว 5 ชนิด" |
| เครื่องให้อาหาร | ความจุ, ตั้งเวลา, WiFi | "รีวิวเครื่องให้อาหารอัตโนมัติ" |
| สายจูง | วัสดุ, ขนาด, harness vs collar | "วิธีเลือกสายจูงสุนัข" |

## Rules

1. NEVER copy from Shopee — all content must be unique
2. First paragraph = direct answer (AEO target)
3. Include comparison tables (HTML `<table>`, not images)
4. FAQ schema (JSON-LD) on every article
5. Internal link to product pages (5-8 per article)
6. Update prices with "ราคาเริ่มต้น" not exact (they change)
7. Tone: เพื่อนที่รู้เรื่องสัตว์เลี้ยง (warm, knowledgeable)
8. Every product MUST have article content (แบงค์ ordered)
9. `rel="nofollow sponsored"` on all Shopee affiliate links
10. dateModified in schema — update when prices/content change
