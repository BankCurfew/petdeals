# PETDEALS — Brand Guide

> Visual identity and design system for petzdeals.com.
> All components must follow this guide for brand consistency.

---

## Brand Identity

**Name**: PETZDEALS
**Tagline**: รวมดีลอุปกรณ์สัตว์เลี้ยง ราคาดี มีรีวิว
**Voice**: "เพื่อนที่รู้เรื่องสัตว์เลี้ยง" — warm, helpful, trustworthy (not sales-y)
**Theme**: White / Clean (NOT dark)

---

## Colors

| Token | Hex | Usage |
|---|---|---|
| Background | `#FFFFFF` | Page background |
| Surface | `#F9FAFB` | Card background, sections |
| Surface Alt | `#F3F4F6` | Category grid background |
| **Primary** | `#F97316` | **CTA buttons, price badges, active states (Shopee orange)** |
| Primary Light | `#FFF7ED` | Hover background, selected states |
| Secondary | `#10B981` | Success, in-stock, discount badges |
| Accent Coral | `#FB7185` | Sale badges, hearts, wishlist |
| Accent Blue | `#60A5FA` | Links, info badges |
| Text Primary | `#1F2937` | Headings, product names |
| Text Secondary | `#6B7280` | Descriptions, metadata |
| Text Muted | `#9CA3AF` | Placeholders |
| Border | `#E5E7EB` | Card borders, dividers |
| Danger | `#EF4444` | Out of stock, errors, price drop badges |

### Tailwind Config

```js
colors: {
  pet: {
    50: '#FFF7ED',
    100: '#FFEDD5',
    500: '#F97316',
    600: '#EA580C',
    700: '#C2410C',
  }
},
fontFamily: {
  sans: ['Sarabun', 'Inter', 'system-ui', 'sans-serif'],
}
```

---

## Typography

```css
font-family: 'Sarabun', 'Inter', system-ui, sans-serif;
```

| Element | Weight | Size | Color |
|---|---|---|---|
| Page title (H1) | 700 | 28px | Text Primary |
| Section heading (H2) | 700 | 22px | Text Primary |
| Product name | 600 | 16px | Text Primary |
| Price | 700 | 20px | Primary (orange) |
| Original price | 400 | 14px, line-through | Text Muted |
| Discount badge | 700 | 12px | White on Danger |
| Category label | 600 | 14px | Text Secondary |
| Body / description | 400 | 14px | Text Secondary |
| CTA button text | 600 | 14px | White on Primary |

---

## Product Card

```
┌─────────────────────────┐
│  ┌─────────────────────┐│
│  │                     ││
│  │    PRODUCT IMAGE    ││  ← 1:1 aspect ratio, rounded-lg
│  │                     ││
│  │  [-30%]        [♡]  ││  ← discount top-left, heart top-right
│  └─────────────────────┘│
│                         │
│  🐱 อาหารแมว             │  ← category chip (small, muted)
│  Royal Canin Indoor     │  ← product name (600, 2 lines max)
│  Adult 2kg              │
│                         │
│  ⭐ 4.8 (2.3K sold)     │  ← rating + sales count
│                         │
│  ฿599  ฿̶8̶5̶9̶            │  ← price (orange) + original (strikethrough)
│                         │
│  [ 🛒 ดูราคาใน Shopee ]  │  ← CTA button (orange pill, full-width)
└─────────────────────────┘
```

| Property | Value |
|---|---|
| Border | 1px `#E5E7EB`, rounded-xl (12px) |
| Shadow (default) | `0 1px 3px rgba(0,0,0,0.06)` |
| Shadow (hover) | `0 4px 12px rgba(0,0,0,0.1)` |
| Hover effect | translateY(-2px) + shadow increase |
| Image | Lazy-load, WebP from R2, fallback placeholder |
| Mobile grid | 2 columns, 8px gap |
| Desktop grid | 4 columns, 16px gap |

---

## Category Grid

```
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  🐕    │ │  🐱    │ │  🐰    │ │  🐟    │
│  สุนัข  │ │  แมว   │ │  กระต่าย│ │  ปลา   │
│ 234 ชิ้น│ │ 189 ชิ้น│ │  56 ชิ้น │ │  78 ชิ้น │
└────────┘ └────────┘ └────────┘ └────────┘
```

- Rounded-2xl, Surface background
- Emoji icon (32px) + Thai label + product count
- Hover: Primary Light bg + border Primary

---

## Header / Navigation

```
┌──────────────────────────────────────────────────┐
│ 🐾 PetzDeals    [ค้นหาสินค้า...]    🛒 ≡        │
│                                                  │
│ [สุนัข] [แมว] [กระต่าย] [ปลา] [นก] [สัตว์เลี้ยง]  │
└──────────────────────────────────────────────────┘
```

- Clean white bg, subtle bottom border (`#E5E7EB`)
- Logo: paw icon + "PetzDeals" in Primary (orange)
- Search bar: rounded-full, border, search icon
- Category pills: horizontal scroll on mobile
- Mobile: hamburger menu + search icon

---

## CTA Button

```css
.btn-primary {
  background: #F97316;
  color: white;
  border-radius: 9999px;
  padding: 10px 24px;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-primary:hover {
  background: #EA580C;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(249,115,22,0.3);
}
```

| Context | Text |
|---|---|
| Product main CTA | ดูราคาล่าสุดใน Shopee → |
| Secondary | เช็คโปรโมชั่น Shopee |
| In-article | ดูรายละเอียดเพิ่มเติม → |
| Comparison winner | เช็คราคา {brand} ใน Shopee → |
| Deal | รับส่วนลด {X}% ที่ Shopee → |
| Category | ดู{category}ทั้งหมด ({N} รายการ) |

---

## Responsive

| Breakpoint | Width | Grid | Notes |
|---|---|---|---|
| Mobile | < 640px | 2-col products | Sticky category pills, bottom search |
| Tablet | 640-1024px | 3-col products | Sidebar categories |
| Desktop | > 1024px | 4-col products | Full sidebar + search |

Min touch target: 44px

---

## WCAG Accessibility

| Combination | Ratio | Pass? |
|---|---|---|
| Orange `#F97316` on white | 3.0:1 | Large text/buttons only |
| Orange `#EA580C` on white | 3.9:1 | Borderline |
| Text Primary `#1F2937` on white | 14.7:1 | ✅ |
| Text Secondary `#6B7280` on white | 5.0:1 | ✅ |

Body text: always `#1F2937` or `#6B7280`, never orange.

---

## Page Templates

| Page | Template | Content |
|---|---|---|
| Homepage | `index.astro` | Hero, best sellers, categories, deals, articles |
| Product detail | `products/[slug].astro` | Gallery, price, CTA, specs, FAQ, related |
| Category listing | `categories/[slug].astro` | Filters, product grid, pagination, sidebar |
| Article | `articles/[slug].astro` | TOC, content, product links, FAQ schema |
| Search | `search.astro` | Input, results grid |
| Deals | `deals.astro` | Price-drop products |
