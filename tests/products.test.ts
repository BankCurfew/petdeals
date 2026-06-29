import { describe, test, expect } from "bun:test";
import productsData from "../data/products.json";
import { readFileSync, readdirSync, existsSync } from "fs";
import { join } from "path";

const DIST = join(import.meta.dir, "../dist");

const productPages = existsSync(join(DIST, "products"))
  ? readdirSync(join(DIST, "products"))
      .filter((d) => existsSync(join(DIST, "products", d, "index.html")))
      .map((d) => ({
        slug: d,
        html: readFileSync(join(DIST, "products", d, "index.html"), "utf-8"),
      }))
  : [];

const blogPages = existsSync(join(DIST, "blog"))
  ? readdirSync(join(DIST, "blog"))
      .filter((d) => d !== "index.html" && existsSync(join(DIST, "blog", d, "index.html")))
      .map((d) => ({
        slug: d,
        html: readFileSync(join(DIST, "blog", d, "index.html"), "utf-8"),
      }))
  : [];

// === 1. Zero Leak — no '0' displayed as content ===
describe("Zero Leak — no stray '0' in rendered HTML", () => {
  test("no product page renders bare '0' after price", () => {
    for (const page of productPages) {
      const priceZeroLeak = page.html.match(/฿[\d,]+<\/span>0/g);
      expect(priceZeroLeak).toBeNull();
    }
  });

  test("no product page shows 'ขายแล้ว 0' as standalone zero", () => {
    for (const page of productPages) {
      const zeroSold = page.html.match(/ขายแล้ว\s*0[^0-9kK+]/g);
      expect(zeroSold).toBeNull();
    }
  });

  test("no product page shows rating '0.0'", () => {
    for (const page of productPages) {
      expect(page.html).not.toMatch(/★\s*0\.0/);
    }
  });

  test("homepage has no bare '0' after price spans", () => {
    const index = readFileSync(join(DIST, "index.html"), "utf-8");
    const leaks = index.match(/฿[\d,]+<\/span>0/g);
    expect(leaks).toBeNull();
  });
});

// === 2. Blog Readability ===
describe("Blog Readability — Designer spec compliance", () => {
  test("blog articles use blog-article class (17px/2.0 line-height)", () => {
    for (const page of blogPages) {
      expect(page.html).toContain("blog-article");
    }
  });

  test("blog article container ≤ 720px max-width", () => {
    for (const page of blogPages) {
      const hasMaxWidth = page.html.includes("max-w-[700px]") || page.html.includes("max-width:700px") || page.html.includes("max-width: 700px");
      expect(hasMaxWidth).toBe(true);
    }
  });

  test("blog CSS has font-size ≥ 16px for body text", () => {
    for (const page of blogPages) {
      const hasFontSize = page.html.includes("font-size:17px") || page.html.includes("font-size: 17px");
      expect(hasFontSize).toBe(true);
    }
  });

  test("blog CSS has line-height ≥ 1.8 for Thai readability", () => {
    for (const page of blogPages) {
      const hasLineHeight = page.html.includes("line-height:2") || page.html.includes("line-height: 2");
      expect(hasLineHeight).toBe(true);
    }
  });
});

// === 3. H1/H2/H3 Hierarchy ===
describe("Heading Hierarchy — every article", () => {
  test("every blog article has exactly one H1", () => {
    for (const page of blogPages) {
      const h1Count = (page.html.match(/<h1[^>]*>/g) || []).length;
      expect(h1Count).toBe(1);
    }
  });

  test("every blog article has at least 3 H2 sections", () => {
    for (const page of blogPages) {
      const h2Count = (page.html.match(/<h2[^>]*>/g) || []).length;
      expect(h2Count).toBeGreaterThanOrEqual(3);
    }
  });

  test("every product page has exactly one H1", () => {
    for (const page of productPages) {
      const h1Count = (page.html.match(/<h1[^>]*>/g) || []).length;
      expect(h1Count).toBe(1);
    }
  });

  test("every product page has at least 4 H2 sections", () => {
    for (const page of productPages) {
      const h2Count = (page.html.match(/<h2[^>]*>/g) || []).length;
      expect(h2Count).toBeGreaterThanOrEqual(4);
    }
  });
});

// === 4. Search Function ===
describe("Search — data attributes for client-side filtering", () => {
  test("homepage has search input", () => {
    const index = readFileSync(join(DIST, "index.html"), "utf-8");
    expect(index).toContain('id="site-search"');
  });

  test("products have data-product-name for search matching", () => {
    const index = readFileSync(join(DIST, "index.html"), "utf-8");
    const names = index.match(/data-product-name="[^"]+"/g) || [];
    expect(names.length).toBeGreaterThan(0);
  });

  test("search would find 'Kaniva' — at least 1 product has Kaniva in name", () => {
    const hasKaniva = productsData.some((p: any) =>
      p.title.toLowerCase().includes("kaniva")
    );
    expect(hasKaniva).toBe(true);
  });

  test("search can find products by brand name (Kaniva)", () => {
    const has = productsData.some((p: any) =>
      p.title.toLowerCase().includes("kaniva") || (p.brand || "").toLowerCase().includes("kaniva")
    );
    expect(has).toBe(true);
  });
});

// === 5. FAQ Schema ===
describe("FAQ Schema — every product page", () => {
  test("all product pages have FAQ JSON-LD schema", () => {
    for (const page of productPages) {
      expect(page.html).toContain("FAQPage");
    }
  });

  test("all product pages have Product JSON-LD schema", () => {
    for (const page of productPages) {
      expect(page.html).toContain('"@type":"Product"');
    }
  });
});

// === 6. Affiliate Links — no double ? ===
describe("Affiliate Links — format validation", () => {
  test("no affiliate URL has double question mark", () => {
    for (const p of productsData) {
      const url = p.affiliateUrl || p.url || "";
      const doubleQ = url.match(/\?\?/g);
      expect(doubleQ).toBeNull();
    }
  });

  test("all products have affiliate URL with utm_source", () => {
    for (const p of productsData) {
      const url = p.affiliateUrl || p.url;
      expect(url).toBeTruthy();
      expect(url).toContain("utm_source=");
    }
  });
});

// === 7. Images — no placeholders ===
describe("Images — real URLs, no placeholders", () => {
  test("all products have real image URLs (not placeholder)", () => {
    for (const p of productsData) {
      expect(p.images.length).toBeGreaterThan(0);
      expect(p.images[0]).toMatch(/^https?:\/\//);
      expect(p.images[0]).not.toContain("placehold");
      expect(p.images[0]).not.toContain("placeholder");
    }
  });
});

// === 8. CTA — no Shopee mention ===
describe("CTA — no Shopee branding", () => {
  test("no product page CTA mentions Shopee", () => {
    for (const page of productPages) {
      expect(page.html).not.toContain("ซื้อเลยที่ Shopee");
      expect(page.html).not.toContain("ดูราคา Shopee");
      expect(page.html).not.toContain("ดูราคาใน Shopee");
    }
  });

  test("homepage CTA does not mention Shopee", () => {
    const index = readFileSync(join(DIST, "index.html"), "utf-8");
    expect(index).not.toContain("ซื้อเลยที่ Shopee");
    expect(index).not.toContain("ดูราคา Shopee");
  });
});

// === 9. Discount — original > sale price ===
describe("Discount — price consistency", () => {
  test("when priceMax exists, it must be ≥ price", () => {
    for (const p of productsData) {
      if (p.priceMax) {
        const price = parseInt(String(p.price).replace(/[^0-9]/g, "")) || 0;
        const max = parseInt(String(p.priceMax).replace(/[^0-9]/g, "")) || 0;
        if (max > 0) {
          expect(max).toBeGreaterThanOrEqual(price);
        }
      }
    }
  });

  test("all products have non-zero price", () => {
    for (const p of productsData) {
      const price = parseInt(String(p.price).replace(/[^0-9]/g, ""));
      expect(price).toBeGreaterThan(0);
    }
  });
});

// === 10. Blog Article Word Count ≥ 300 ===
describe("Blog Content — minimum word count", () => {
  test("every blog article has ≥ 300 words of content", () => {
    for (const page of blogPages) {
      const textOnly = page.html
        .replace(/<script[^>]*>[\s\S]*?<\/script>/g, "")
        .replace(/<style[^>]*>[\s\S]*?<\/style>/g, "")
        .replace(/<[^>]+>/g, " ")
        .replace(/\s+/g, " ")
        .trim();
      const wordCount = textOnly.split(/\s+/).length;
      expect(wordCount).toBeGreaterThanOrEqual(300);
    }
  });
});

// === Original tests: Data, Filter, Sitemap ===
describe("Product Data Integrity", () => {
  test("all products have a slug", () => {
    for (const p of productsData) {
      expect(p.slug).toBeTruthy();
    }
  });

  test("all products have a title longer than 5 chars", () => {
    for (const p of productsData) {
      expect(p.title.length).toBeGreaterThan(5);
    }
  });

  test("ratings are either empty or valid numbers 1-5", () => {
    for (const p of productsData) {
      if (p.rating && p.rating !== "") {
        const r = parseFloat(p.rating);
        expect(r).toBeGreaterThanOrEqual(1);
        expect(r).toBeLessThanOrEqual(5);
      }
    }
  });

  test("all products have a valid category", () => {
    const valid = ["อาหารแมว", "อาหารเปียก", "ขนมแมว", "ทรายแมว", "สุนัข"];
    for (const p of productsData) {
      if (p.category) {
        expect(valid).toContain(p.category);
      }
    }
  });
});

describe("Category Filter Logic", () => {
  const categories = ["อาหารแมว", "อาหารเปียก", "ขนมแมว", "ทรายแมว", "สุนัข"];

  test("every category has at least one product", () => {
    for (const cat of categories) {
      const count = productsData.filter((p: any) => p.category === cat).length;
      expect(count).toBeGreaterThan(0);
    }
  });
});

describe("Sitemap & SEO", () => {
  test("sitemap has all product URLs", () => {
    const sitemap = readFileSync(join(DIST, "sitemap-0.xml"), "utf-8");
    const urls = sitemap.match(/<loc>(.*?)<\/loc>/g) || [];
    const productUrls = urls.filter((u) => u.includes("/products/"));
    expect(productUrls.length).toBe(productsData.length);
  });

  test("robots.txt references sitemap", () => {
    const robots = readFileSync(join(DIST, "robots.txt"), "utf-8");
    expect(robots).toContain("Sitemap:");
  });

  test("all pages have GTM + GA4", () => {
    for (const page of productPages) {
      expect(page.html).toContain("GTM-MXZC4NXN");
      expect(page.html).toContain("G-3TCK9V54XS");
    }
  });
});
