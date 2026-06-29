import { describe, test, expect } from "bun:test";
import productsData from "../data/products.json";
import { readFileSync, readdirSync, existsSync } from "fs";
import { join } from "path";

const DIST = join(import.meta.dir, "../dist");

describe("Product Data Integrity", () => {
  test("all products have a slug", () => {
    for (const p of productsData) {
      expect(p.slug).toBeTruthy();
    }
  });

  test("all products have non-zero price", () => {
    for (const p of productsData) {
      const price = parseInt(String(p.price).replace(/[^0-9]/g, ""));
      expect(price).toBeGreaterThan(0);
    }
  });

  test("no product displays price as 0", () => {
    for (const p of productsData) {
      expect(p.price).not.toBe("฿0");
      expect(p.price).not.toBe("0");
      expect(p.price).not.toBe("");
    }
  });

  test("all products have at least one image", () => {
    for (const p of productsData) {
      expect(p.images).toBeDefined();
      expect(p.images.length).toBeGreaterThan(0);
      expect(p.images[0]).toMatch(/^https?:\/\//);
    }
  });

  test("all products have an affiliate URL with utm_source", () => {
    for (const p of productsData) {
      const url = p.affiliateUrl || p.url;
      expect(url).toBeTruthy();
      expect(url).toContain("utm_source=");
    }
  });

  test("all products have a title", () => {
    for (const p of productsData) {
      expect(p.title).toBeTruthy();
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

  test("sold counts don't contain '0' as display value", () => {
    for (const p of productsData) {
      if (p.sold !== undefined && p.sold !== "") {
        expect(p.sold).not.toBe("0");
      }
    }
  });

  test("all products have a category", () => {
    const validCategories = ["อาหารแมว", "อาหารเปียก", "ขนมแมว", "ทรายแมว", "สุนัข"];
    for (const p of productsData) {
      if (p.category) {
        expect(validCategories).toContain(p.category);
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

  test("all filter selects all products", () => {
    const all = productsData.filter((p: any) => p.slug);
    expect(all.length).toBe(productsData.length);
  });

  test("category filter returns correct subset", () => {
    for (const cat of categories) {
      const filtered = productsData.filter((p: any) => p.category === cat);
      for (const p of filtered) {
        expect(p.category).toBe(cat);
      }
    }
  });
});

describe("Built Pages — Schema Markup", () => {
  const productPages = existsSync(join(DIST, "products"))
    ? readdirSync(join(DIST, "products"))
        .filter((d) => existsSync(join(DIST, "products", d, "index.html")))
        .map((d) => ({
          slug: d,
          html: readFileSync(join(DIST, "products", d, "index.html"), "utf-8"),
        }))
    : [];

  test("all product pages have Product JSON-LD schema", () => {
    expect(productPages.length).toBeGreaterThan(0);
    for (const page of productPages) {
      expect(page.html).toContain('"@type":"Product"');
    }
  });

  test("all product pages have exactly one H1", () => {
    for (const page of productPages) {
      const h1Count = (page.html.match(/<h1[^>]*>/g) || []).length;
      expect(h1Count).toBe(1);
    }
  });

  test("all product pages have GTM container", () => {
    for (const page of productPages) {
      expect(page.html).toContain("GTM-MXZC4NXN");
    }
  });

  test("all product pages have GA4 tag", () => {
    for (const page of productPages) {
      expect(page.html).toContain("G-3TCK9V54XS");
    }
  });

  test("all product pages have affiliate_click event", () => {
    for (const page of productPages) {
      expect(page.html).toContain("affiliate_click");
    }
  });

  test("no product page has Shopee in CTA text", () => {
    for (const page of productPages) {
      expect(page.html).not.toContain("ซื้อเลยที่ Shopee");
      expect(page.html).not.toContain("ดูราคา Shopee");
    }
  });
});

describe("Built Pages — Sitemap & SEO", () => {
  test("sitemap-index.xml exists", () => {
    expect(existsSync(join(DIST, "sitemap-index.xml"))).toBe(true);
  });

  test("sitemap-0.xml has all product URLs", () => {
    const sitemap = readFileSync(join(DIST, "sitemap-0.xml"), "utf-8");
    const urls = sitemap.match(/<loc>(.*?)<\/loc>/g) || [];
    const productUrls = urls.filter((u) => u.includes("/products/"));
    expect(productUrls.length).toBe(productsData.length);
  });

  test("robots.txt exists and references sitemap", () => {
    const robots = readFileSync(join(DIST, "robots.txt"), "utf-8");
    expect(robots).toContain("Sitemap:");
    expect(robots).toContain("petzdeals.com");
  });
});
