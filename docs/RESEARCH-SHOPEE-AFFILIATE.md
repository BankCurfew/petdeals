# Deep Research: Shopee Affiliate Custom Links — วิธีการ เหตุผล และแนวปฏิบัติ

> Research date: 2026-06-29 | Source: 15+ sources cross-referenced

---

## 1. How Shopee Affiliate Link Tracking Works (ระบบ tracking ทำงานยังไง)

### Attribution Model: CPS (Cost-Per-Sale)

Shopee ใช้ระบบ **Cost-Per-Sale** — จ่าย commission เมื่อมีการซื้อจริงเท่านั้น ไม่ใช่ click

### Cookie Window: **7 วัน**

เมื่อ user คลิก affiliate link, Shopee จะตั้ง tracking cookie ที่อยู่ **7 วัน**:
- คลิกวันจันทร์ → ซื้อวันอาทิตย์ = ได้ commission ✅
- คลิกวันจันทร์ → ซื้อวันจันทร์ถัดไป = ไม่ได้ ❌ (เกิน 7 วัน)

### Tracking Parameters (ถูก Shopee ใส่อัตโนมัติ)

เมื่อ user คลิก affiliate link, Shopee จะ append parameter เหล่านี้ให้อัตโนมัติ:

| Parameter | Value | Source |
|---|---|---|
| `uls_trackid` | Auto-generated | Shopee auto |
| `utm_source` | `an_{affiliate_id}` (e.g. `an_15312860014`) | Your affiliate ID |
| `utm_medium` | `affiliates` | Fixed |
| `utm_content` | Values from your `sub_id` | Your tracking data |
| `utm_campaign` | `-` (default) | Shopee auto |
| `utm_term` | Auto-generated | Shopee auto |

### Direct vs Indirect Orders (สำคัญมาก — เริ่ม 2 ม.ค. 2026)

| Type | คำอธิบาย | Commission Rate |
|---|---|---|
| **Direct Order** | User คลิก link ร้าน A → ซื้อของจากร้าน A | 100% of commission rate |
| **Indirect Order** | User คลิก link ร้าน A → ซื้อของจากร้าน B | **30%** of the commission rate |

ก่อนหน้านี้ (ก่อน 2 ม.ค. 2026) ได้ commission เฉพาะ Direct Order เท่านั้น — ตอนนี้ Indirect ก็ได้ด้วย ทำให้ content ที่กว้าง (เช่น blog เปรียบเทียบ) มีโอกาสได้ commission มากขึ้น

---

## 2. Custom Link vs UTM-Constructed URLs (ทำไมต้องใช้ Custom Link)

### ❌ UTM-Constructed (สิ่งที่เราทำก่อนหน้า)

```
https://shopee.co.th/product-i.12345.67890?utm_source=an_15312860014&utm_medium=affiliates&utm_campaign=petdeals
```

**ปัญหา:**
- UTM parameters เป็นแค่ **tracking ฝั่ง GA4** — ไม่ได้ trigger Shopee affiliate attribution
- Shopee ต้องการ link ที่ผ่านระบบ redirect ของตัวเอง (`s.shopee.co.th/an_redir`)
- ถ้าไม่ผ่านระบบ Shopee → cookie ไม่ถูกตั้ง → ไม่มี attribution → **ไม่ได้ commission**

### ✅ Custom Link (วิธีที่ถูกต้อง)

```
https://s.shopee.co.th/an_redir?origin_link={encoded_shopee_url}&affiliate_id=15312860014&sub_id=petdeals-product-royalcanin
```

**ทำไมถูก:**
- ผ่าน Shopee redirect server → ตั้ง attribution cookie
- `affiliate_id` ถูก register ในระบบ Shopee
- Commission ถูก track และ attribute ให้ account เรา
- Sub_id ช่วย track ว่า link ไหนมาจากไหน

### Short Link (from Custom Link tool)

เมื่อใช้ Custom Link tool ใน affiliate portal, Shopee จะ generate **short link** เช่น:
```
https://shope.ee/XXXXXXXXX
```
Short link นี้ redirect ไปยัง full affiliate URL ที่มี tracking parameters ครบ

---

## 3. Commission Rates (อัตรา commission)

### Shopee Commission (Base Rate — จาก Shopee)

| Channel | Top KOL | KOL | KOC | Affiliate (เรา) |
|---|---|---|---|---|
| Shopee Live | 10% (cap $5+) | — | — | — |
| Social Media | 7% (cap $5+) | 6% (cap $5) | 6% (cap $5) | **5% (cap $5)** |
| Shopee Video | 5% (cap $5+) | — | — | — |
| Non-XTRA | up to 4% (cap $5+) | 3% (cap $5) | 3% (cap $5) | **2% (cap $5)** |

**เราเป็น "Affiliate" tier** → base rate ประมาณ **2-5%** (cap ฿175 ≈ $5 per order)

### Brand Commission / CommissionsXTRA (เพิ่มจาก seller)

- Seller กำหนดเอง → สูงสุด **40%** ไม่มี cap
- Indirect CommissionsXTRA: สูงสุด **12%** (= 30% ของ rate ที่ seller ตั้ง)
- **Total potential**: Shopee 5% + Brand 40% = **45-50%** ต่อ order (กรณีดีที่สุด)

### Pet Supplies Category — Estimated Rate

Shopee ไม่ได้ publish rate แยกรายหมวดสำหรับ Thailand โดยเฉพาะ แต่จากข้อมูลทั้งหมด:
- **Base rate สำหรับ pet supplies: ~2-5%** (อยู่ในกลุ่ม general merchandise)
- **ถ้า seller มี CommissionsXTRA: +5-40%** เพิ่ม
- Pet supplies เป็น high-potential niche ใน Thailand market

### Commission Cap

| Tier | Cap per order |
|---|---|
| Affiliate (เรา) | ฿175 (~$5) per order (Shopee commission) |
| KOL/KOC | ฿175 ($5) |
| Top KOL | ฿175+ ($5+) uncapped |
| CommissionsXTRA | **Uncapped** |

---

## 4. Attribution Window Details (รายละเอียด cookie window)

| Parameter | Value |
|---|---|
| **Cookie duration** | 7 days |
| **Attribution model** | Last-click (ถ้า user คลิก affiliate อื่นก่อน แล้วคลิกของเราทีหลัง → commission เป็นของเรา) |
| **Indirect orders** | ✅ ได้ commission (30% of rate) ตั้งแต่ 2 ม.ค. 2026 |
| **Cancellations/refunds** | ❌ ไม่ได้ commission |
| **Invalid activity** | ❌ Shopee อาจ reject commission ถ้าตรวจพบ fraud |
| **Multi-device** | ❌ cookie ผูกกับ device/browser เดียว |

---

## 5. Best Practices for Affiliate Link Optimization

### Content Strategy

1. **เขียน content กว้าง** ที่กระตุ้นให้ user browse หลายร้าน — indirect orders ได้ commission ด้วย
2. **ใส่ CTA ชัดเจน** — "เช็คราคาให้เจ้านาย" ดีกว่า "คลิกที่นี่"
3. **เปรียบเทียบสินค้า** ในบทความรีวิว — user คลิกหลาย link = โอกาส conversion สูง
4. **เน้น CommissionsXTRA products** — commission สูงกว่า base rate มาก

### Link Placement

5. **ใส่ link ใน context** — อย่า dump link เปล่า ต้องมีเหตุผลให้คลิก
6. **Multiple CTAs per page** — ไม่ใช่แค่ท้ายบทความ ใส่ระหว่างทางด้วย
7. **ใช้ Sub_id track ทุก position** — รู้ว่า link ตรงไหนใน page ได้ click มากสุด

### Technical

8. **ใช้ Custom Link / Product Feed เท่านั้น** — ห้ามสร้าง UTM link เอง
9. **ตั้ง Sub_id ทุก link** — เพื่อ track performance ใน Conversion Report
10. **Refresh links weekly** — link อาจ expire หรือ product หมด stock

---

## 6. Product Feed CSV (รายละเอียด)

### Feed Information

| Property | Value |
|---|---|
| **Name** | Product Feed All Global Category |
| **Size** | Up to 1,000,000 products per CSV file |
| **Update frequency** | Daily (~07:43) |
| **Format** | CSV (may be gzip compressed) |
| **Filter** | stock > 0, itemsold > 0, rating > 1, new items only |

### CSV Columns (from API/feed documentation)

| Column | Description |
|---|---|
| `itemId` | Shopee item ID |
| `shopId` | Shopee shop ID |
| `name` | Product title |
| `offerLink` | Full affiliate link with tracking |
| `shortLink` | Short affiliate link (if generated) |
| `commissionRate` | Base commission % |
| `commission` | Commission amount |
| `sales` | Total sales count |
| `rating` | Product rating |
| `discountPct` | Current discount percentage |
| `periodStartTime` | Offer start |
| `periodEndTime` | Offer end |
| `price` | Current price |
| `image` | Product image URL |
| `category` | Product category |

### How to Use for PetzDeals

1. Download CSV จาก Product Feed page
2. Match products โดยใช้ `shopId` + `itemId` (มีอยู่แล้วใน products.json)
3. Extract `offerLink` หรือ `shortLink` column
4. Update `data/products.json` field `affiliateUrl`

---

## 7. CommissionsXTRA — คืออะไร ทำยังไง

### What It Is

CommissionsXTRA คือ **commission เพิ่มเติม** ที่ **seller กำหนดเอง** บนราคา base ของ Shopee — เช่น seller ตั้ง 25% XTRA → affiliate ได้ Shopee base (2-5%) + XTRA (25%) = **27-30%** ต่อ order

### How to Access

ใน affiliate portal → **Offer** → **Commissions XTRA** (ถ้า account tier ถึง)

**Account ของเรา** ยังเข้า CommissionsXTRA ไม่ได้ — แสดงว่าต้องมี performance threshold (น่าจะต้องมี order history ระดับหนึ่ง)

### How to Promote XTRA Products

- ดูจาก **Product Offer** page → filter for products with XTRA commission
- ดูจาก **Product Feed CSV** → column `commissionRate` สูงกว่าปกติ = มี XTRA
- เลือก products ที่มี XTRA commission สูง มาใส่ใน "ดีลแนะนำ" sections

---

## 8. Sub_IDs — Tracking Parameters

### Structure

```
Sub_id format: {segment1}-{segment2}-{segment3}-{segment4}-{segment5}
```

สูงสุด **5 Sub_ids** ต่อ link (Sub_id1 ถึง Sub_id5)

### Recommended Schema for PetzDeals

| Sub_id | Purpose | Example Values |
|---|---|---|
| `Sub_id1` | Source | `petdeals` |
| `Sub_id2` | Page type | `product`, `blog`, `deal`, `homepage` |
| `Sub_id3` | Content slug | `royalcanin-4kg`, `7-7-voucher-guide` |
| `Sub_id4` | Position | `hero`, `card`, `cta`, `inline`, `sidebar` |
| `Sub_id5` | Date/campaign | `20260707`, `77sale` |

### How to Use

1. **Set Sub_ids** เมื่อ generate link ผ่าน Custom Link tool
2. **ดู performance** ใน affiliate portal → Report → Click Report → filter by Sub_id
3. **Conversion Report** → ดูว่า Sub_id ไหนมี conversion สูงสุด

### Example

```
Sub_id1: petdeals
Sub_id2: blog
Sub_id3: 7-7-mega-sale
Sub_id4: cta-button
Sub_id5: 20260707
```

Combined: `petdeals-blog-7-7-mega-sale-cta-button-20260707`

---

## 9. Open API (GraphQL)

### Availability

| Requirement | Status |
|---|---|
| **Minimum orders** | 1,000+ orders to apply |
| **Our status** | ❌ ยังไม่ถึง (0 orders currently) |
| **Protocol** | GraphQL over HTTP POST |
| **Endpoint (TH)** | `https://open-api.affiliate.shopee.co.th/graphql` (estimated from pattern) |

### API Capabilities (from Brazil/SG documentation)

| Query | Description |
|---|---|
| `productOfferV2` | Search products by keyword/category with commission rates |
| `shopOfferV2` | Search shops with commission offers |
| `generateShortLink` | Generate single affiliate short link |
| `generateBatchShortLink` | Generate up to N short links with Sub_id template |
| `conversionReport` | Pull conversion data |
| `clickReport` | Pull click data |
| `datafeedDownload` | Download product feed CSV |

### Batch Short Link Generation (API)

```graphql
mutation {
  generateBatchShortLink(
    input: {
      originUrl: "https://shopee.co.th/product-i.12345.67890"
      subIdsTemplate: "petdeals-{{shopId}}-{{itemId}}-{{date}}"
    }
  ) {
    shortLink
  }
}
```

Available template tokens: `{{date}}`, `{{shopId}}`, `{{itemId}}`, `{{keyword}}`

### Roadmap

เมื่อ PetzDeals ถึง 1,000 orders → apply for Open API → automate ทุกอย่าง:
- Batch generate affiliate links สำหรับ 110+ products ทีเดียว
- Auto-sync commission rates
- Auto-update product data (price, stock, rating)
- Real-time conversion tracking

---

## 10. Tips for Increasing Conversion Rate (เพิ่ม conversion)

### Content-Level

1. **เขียนรีวิวจริง ไม่ใช่แค่ list products** — user ต้องรู้สึกว่าได้ข้อมูลก่อนตัดสินใจ
2. **เปรียบเทียบ 3-5 products** ในบทความเดียว — user เลือกง่าย คลิกเร็ว
3. **ใส่ราคาจริง + update บ่อย** — ราคาเก่า = user ไม่ไว้ใจ
4. **ใช้ "น้องดีล" voice** — personality ทำให้ site แตกต่าง + memorable
5. **Season-based content** — 7.7, 9.9, 11.11, 12.12 = peak buying periods

### Technical

6. **Page speed matters** — mobile user ใน TH มี patience ต่ำ, >3s = bounce
7. **Mobile-first design** — 80%+ traffic มาจาก mobile
8. **Deeplink to product** — อย่า link ไปหน้า shop, link ตรงไปหน้า product
9. **ใช้ product images** — visual > text for click-through
10. **Track everything with Sub_ids** — รู้ว่าอะไร convert → ทำเพิ่ม

### Timing

11. **Push content ก่อน sale 3-7 วัน** — user collect vouchers ก่อน
12. **Email/notification วัน sale** — remind user ที่เคยอ่าน content
13. **Update prices ทันทีหลัง sale เริ่ม** — ราคาจริงช่วง sale = trust
14. **สร้าง urgency** — countdown timer, "Flash Sale 00:00", "ของหมดเร็ว"

---

## Summary Table

| Topic | Key Fact |
|---|---|
| **Cookie window** | 7 days |
| **Attribution** | Last-click |
| **Base commission (Affiliate tier)** | 2-5% (cap ฿175/order) |
| **CommissionsXTRA** | Up to 40% uncapped (seller sets) |
| **Indirect orders** | 30% of commission rate (new in 2026) |
| **Custom Link batch** | 5 URLs at a time |
| **Product Feed** | 1M products, daily update, CSV download |
| **Open API** | Needs 1,000+ orders |
| **Sub_ids** | 5 segments for tracking |
| **Our status** | Affiliate tier, 2 clicks, 0 orders |

---

## Sources

- [Shopee Affiliate Program: How to Join & Make Money in 2026](https://reacheffect.com/blog/shopee-affiliate-program/)
- [Commissions Structure (W.e.f. 2 January 2026)](https://help.shopee.sg/portal/10/article/191914-Commissions-Structure-(W.e.f.-2-January-2026))
- [Shopee Affiliate Marketing in 2026: What's New](https://www.bitbrowser.net/news/shopee-affiliate-marketing-2026)
- [Affiliate Link Generation | Shopee Help Center](https://help.shopee.sg/portal/10/article/191696-Affiliate-Link-Generation)
- [Affiliate Short Link Implementation Guide](https://help.shopee.sg/portal/10/article/171184-Affiliate-Short-Link-Implementation-Guide)
- [Short Link Implementation Guideline (MY)](https://help.shopee.com.my/portal/10/article/174050-[ENG]-Short-Link-Implementation-Guideline)
- [How To Generate Shopee Affiliate Link And Track Clicks](https://miuravisual.com/how-to-generate-shopee-affiliate-link/)
- [Shopee Affiliate Program FAQ](https://help.shopee.sg/portal/10/article/126383-Shopee-Affiliate-Program-FAQ)
- [Shopee Affiliate EPC & Commission Data](https://avidaffiliate.com/programs/shopee-co-th/)
- [Shopee Affiliate Commissions & Payments - UpPromote](https://uppromote.com/affiliate-directory/shopee/)
- [Shopee Commission Rate Analysis 2026](https://www.alibaba.com/product-insights/shopee-commission-rate-analysis-2026-latest-insights.html)
- [Shopee vs Lazada vs TikTok Shop Fees 2026](https://digitalinasia.com/shopee-lazada-tiktok-shop-fees-2026/)
- [Shopee Affiliate Products API - Apify](https://apify.com/viralanalyzer/shopee-affiliate-products)
- [Shopee Affiliate Tracking - wecantrack](https://wecantrack.com/shopee-integration/)
- [TH Shopee Affiliate Marketing Solution PDF](https://deo.shopeemobile.com/shopee/seller/seller_cms/c76ee0a25eaf088e29267a55ec8e9069/%5BExternal%5D%20TH%20Shopee%20Affiliate%20Marketing%20Solution.pdf)
