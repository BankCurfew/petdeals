# SOP: Promo & Campaign Tracking — เช็คทุกวัน เซตล่วงหน้า

> ทุกวันต้องเช็คว่า Shopee มีโปรอะไร แล้วเตรียม content + banner ล่วงหน้า
> โปรมาแล้วไม่พร้อม = เสีย traffic = เสียเงิน

## Daily Check (09:00 ทุกวัน — Data Oracle)

```
1. เปิด shopee.co.th → ดู banner หน้าแรก → มีแคมเปญอะไร?
2. เช็ค shopee.co.th/campaigns → โปรที่กำลังจะมา
3. เช็ค Flash Sale → สินค้า pet ลดราคาวันนี้?
4. เช็ค Shopee Mall → brand day อะไรวันนี้?
5. เช็ค voucher ใหม่ → platform voucher + shop voucher
6. เช็ค Shopee Affiliate dashboard → bonus campaign?
```

**Output**: รายงานให้ BoB ทุกเช้า — โปรอะไร, สินค้าไหนลด, voucher อะไรใช้ได้

## Campaign Calendar (เซตล่วงหน้า)

| วันที่ | Campaign | เตรียมล่วงหน้า |
|---|---|---|
| ทุกเดือน 25-1 | Payday Sale | 3 วันก่อน: banner + บทความ "ดีล payday" |
| 7 ก.ค. | **7.7 Mega Sale** | **ตอนนี้**: banner + บทความ + product list |
| 8 ส.ค. | 8.8 Sale | 2 สัปดาห์ก่อน |
| 9 ก.ย. | 9.9 Sale | 2 สัปดาห์ก่อน |
| 10 ต.ค. | 10.10 Sale | 2 สัปดาห์ก่อน |
| 11 พ.ย. | 11.11 Mega Sale | 1 เดือนก่อน (ใหญ่มาก) |
| 12 ธ.ค. | 12.12 Year-End | 1 เดือนก่อน |
| ทุกวัน | Flash Sale | เช็คเช้า+เที่ยง+เย็น |
| สุ่ม | Brand Day (Royal Canin, Hill's) | ดู Shopee calendar |

## เตรียม Content ล่วงหน้าสำหรับแต่ละ Campaign

### ก่อนแคมเปญ 2 สัปดาห์:

**1. บทความ Niche Deal (Writer)**
```markdown
H1: ดีลอุปกรณ์สัตว์เลี้ยง 7.7 — ทาสแมวต้องเตรียมตัว!

H2: 💬 น้องดีลสรุป 7.7 ปีนี้มีอะไรบ้าง
(สรุปแคมเปญ, วันที่, voucher code)

H2: 🐱 อาหารแมวที่ลดหนัก 7.7
(list สินค้า + ราคาปกติ vs ราคา 7.7 + affiliate link)

H2: 🐕 อุปกรณ์สุนัขดีลเด็ด
(list สินค้า)

H2: 📌 วิธีใช้ voucher ให้คุ้มที่สุด
(stack voucher guide)

H2: ⏰ Flash Sale เวลาไหนบ้าง
(schedule)

H2: คำถามที่พบบ่อย 7.7
(FAQ schema)
```

**2. Hero Banner (Designer)**
- Banner หลัก: "7.7 ดีลสัตว์เลี้ยง ลดสูงสุด XX%"
- Brand: teal + coral (ไม่ใช่ Shopee orange)
- Mascot น้องดีล ถือป้าย sale
- Countdown timer ถ้าทำได้

**3. Product List (Data)**
- Scrape สินค้า pet ที่ลดราคาหนักช่วง campaign
- ราคาก่อน vs ราคาหลังลด
- % discount
- Affiliate links

**4. Dev Implementation**
- Hero banner swap (campaign banner แทน default)
- Deal badge บน product cards ("ดีล 7.7" badge)
- Landing page: /deals/7-7/ (SEO: "ดีลสัตว์เลี้ยง 7.7")
- Countdown timer component

### หลังแคมเปญ:
- เปลี่ยน banner กลับ default
- อัพเดทราคาปกติ
- เก็บบทความ deal ไว้ (SEO value ยังอยู่)
- สรุปผล: traffic + clicks + commission จากแคมเปญ

## Daily Flash Deal Check (3 รอบ/วัน — Data)

| เวลา | ทำอะไร |
|---|---|
| 09:00 | เช็ค flash deal 12:00 → ถ้ามี pet product → scrape + post |
| 12:00 | เช็ค flash deal 18:00 → ถ้ามี pet product → scrape + post |
| 17:00 | เช็ค flash deal 00:00 → ถ้ามี pet product → scrape + post |

## Voucher Tracking

ทุกวันเช็ค:
```
1. Platform voucher: ลดกี่บาท? ขั้นต่ำเท่าไหร่?
2. Shop voucher: ร้านไหนมี voucher? (เฉพาะ pet shops)
3. Coins cashback: กี่ % คืน?
4. Free shipping: ขั้นต่ำเท่าไหร่?
5. Bundle deal: ซื้อ X แถม Y?
```

แสดงบนเว็บ: "🏷️ ใช้โค้ด PETLOVE ลด 50 บาท (ขั้นต่ำ 300)"

## Maw Loop Setup

```bash
maw loop add '{
  "id":"petdeals-promo-check",
  "oracle":"data",
  "tmux":"09-data:0",
  "schedule":"0 9 * * *",
  "prompt":"[petdeals] เช็ค Shopee โปรโมชั่นวันนี้: แคมเปญ, flash deal, voucher, brand day → report BoB",
  "requireIdle":true,
  "enabled":true,
  "description":"Daily Shopee promo check"
}'
```

## ห้ามพลาด

- **7.7 อีก 8 วัน** — ต้องมี banner + บทความ + deal list พร้อมก่อน
- Flash deal หมดเร็ว — ต้องเช็ค+post ทันที
- Voucher เปลี่ยนทุกวัน — ต้อง update
- Brand day ไม่แจ้งล่วงหน้า — ต้องเช็คทุกเช้า
- **โปรมาแล้วไม่พร้อม = เสีย traffic = เสียเงิน**
