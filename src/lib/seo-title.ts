const SPAM_WORDS = [
  'สินค้าพร้อมส่ง', 'พร้อมส่งจากไทย', 'มีให้เลือกหลายสี', 'มีให้เลือกหลายขนาด',
  'ประกันคุณภาพ', 'สินค้าขายดี', 'จัดส่งเร็ว', 'ราคาโรงงาน', 'ลดกระหน่ำ',
  'ราคาพิเศษ', 'ส่งจากไทย', 'สินค้าใหม่', 'ของแท้100%', '100%ของแท้',
  'แท้100%', '100%แท้', 'BEST SELLER', 'Flash Sale', 'HOT SALE',
  'พร้อมส่ง', 'ราคาถูก', 'ลดราคา', 'คุณภาพดี', 'ส่งฟรี',
  'ของแท้', 'ขายดี', 'ยอดนิยม', 'ลดสุดๆ', 'มาใหม่',
  'ส่งไว', 'ส่งด่วน', 'SALE', 'HOT', 'NEW',
];

const EMOJI_RE = /[\p{Emoji_Presentation}\p{Extended_Pictographic}‍️]/gu;
const BRACKET_RE = /[\[（【(][^\]）】)]*[\]）】)]/g;
const SKU_RE = /\b[A-Z]{1,4}[-_]?\d{3,}\b/gi;
const SPECIAL_RE = /[★☆●◆▶►▪▸✅❌!]{2,}/g;

const spamRegexes = SPAM_WORDS
  .sort((a, b) => b.length - a.length)
  .map(w => new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'));

export function cleanProductName(raw: string): string {
  let s = raw;
  s = s.replace(EMOJI_RE, '');
  s = s.replace(BRACKET_RE, '');
  for (const re of spamRegexes) s = s.replace(re, '');
  s = s.replace(SKU_RE, '');
  s = s.replace(SPECIAL_RE, '');
  s = s.replace(/^[\s\-—!.,;:/]+|[\s\-—!.,;:/]+$/g, '');
  s = s.replace(/\s+/g, ' ').trim();
  return s || raw.replace(/\s+/g, ' ').trim();
}

function smartTruncate(text: string, max: number): string {
  if (text.length <= max) return text;
  const cut = text.substring(0, max);
  const lastSpace = cut.lastIndexOf(' ');
  if (lastSpace > max * 0.5) return cut.substring(0, lastSpace);
  return cut;
}

const PAGE_TITLE_MAX = 46;

function htmlExtraChars(s: string): number {
  return (s.match(/&/g) || []).length * 4
    + (s.match(/</g) || []).length * 3
    + (s.match(/>/g) || []).length * 3
    + (s.match(/'/g) || []).length * 4
    + (s.match(/"/g) || []).length * 5;
}

export function buildPageTitle(raw: string, category: string, curated?: string): string {
  if (curated) return curated;

  const cleaned = cleanProductName(raw);
  const effMax = PAGE_TITLE_MAX - htmlExtraChars(cleaned) - htmlExtraChars(category);
  const withCat = `${cleaned} — ${category}`;
  if (withCat.length <= effMax) return withCat;

  const catSuffix = ` — ${category}`;
  const nameMax = effMax - catSuffix.length;
  if (nameMax >= 12) return smartTruncate(cleaned, nameMax) + catSuffix;

  return smartTruncate(cleaned, effMax);
}

export function deduplicateTitles(
  products: { slug: string; title: string; category: string; seoTitle?: string; brand?: string; shopName?: string }[],
): Map<string, string> {
  const result = new Map<string, string>();
  const seen = new Map<string, string[]>();

  for (const p of products) {
    const t = buildPageTitle(p.title, p.category || 'สัตว์เลี้ยง', p.seoTitle);
    result.set(p.slug, t);
    if (!seen.has(t)) seen.set(t, []);
    seen.get(t)!.push(p.slug);
  }

  for (const [title, slugs] of seen) {
    if (slugs.length <= 1) continue;
    for (const slug of slugs) {
      const p = products.find(x => x.slug === slug);
      if (!p) continue;
      if (p.seoTitle) continue;
      const variant = p.brand || p.shopName || `#${slug.slice(-6)}`;
      const varSuffix = ` ${variant}`;
      const nameMax = PAGE_TITLE_MAX - htmlExtraChars(cleanProductName(p.title)) - htmlExtraChars(variant) - varSuffix.length;
      const truncName = smartTruncate(cleanProductName(p.title), Math.max(10, nameMax));
      result.set(slug, `${truncName}${varSuffix}`);
    }
  }

  // Second pass: remaining collisions use slug suffix for guaranteed uniqueness
  const seen2 = new Map<string, string[]>();
  for (const [slug, title] of result) {
    if (!seen2.has(title)) seen2.set(title, []);
    seen2.get(title)!.push(slug);
  }
  for (const [title, slugs] of seen2) {
    if (slugs.length <= 1) continue;
    for (let i = 1; i < slugs.length; i++) {
      const slug = slugs[i];
      const p = products.find(x => x.slug === slug);
      if (p?.seoTitle) continue;
      const tag = `#${slug.slice(-6)}`;
      const nameMax = PAGE_TITLE_MAX - tag.length;
      result.set(slug, smartTruncate(title.replace(/ \| PetzDeals$/, ''), Math.max(10, nameMax)) + tag);
    }
  }

  return result;
}
