/**
 * SEO Gate — validates every built page has complete metadata.
 * Run after `astro build`: bun scripts/seo-gate.ts
 * Exits 1 if any page fails. Gates, not rules.
 */

import { readdirSync, readFileSync } from "fs";
import { join } from "path";

const DIST = join(import.meta.dir, "../dist");

interface Issue {
  page: string;
  missing: string[];
}

function findHtmlFiles(dir: string, base = ""): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const rel = base ? `${base}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      files.push(...findHtmlFiles(join(dir, entry.name), rel));
    } else if (entry.name === "index.html") {
      files.push(rel);
    }
  }
  return files;
}

function validate(filePath: string): string[] {
  const html = readFileSync(join(DIST, filePath), "utf-8");
  const missing: string[] = [];

  if (!/<title>[^<]+<\/title>/.test(html)) missing.push("title");
  if (!/name="description"\s+content="[^"]+"|content="[^"]+"\s+name="description"/.test(html)) missing.push("meta description");
  if (!/rel="canonical"\s+href="[^"]+"|href="[^"]+"\s+rel="canonical"/.test(html)) missing.push("canonical");
  if (!/property="og:title"\s+content="[^"]+"|content="[^"]+"\s+property="og:title"/.test(html)) missing.push("og:title");
  if (!/property="og:description"\s+content="[^"]+"|content="[^"]+"\s+property="og:description"/.test(html)) missing.push("og:description");
  if (!/property="og:image"\s+content="[^"]+"|content="[^"]+"\s+property="og:image"/.test(html)) missing.push("og:image");
  if (!/application\/ld\+json/.test(html)) missing.push("JSON-LD schema");

  return missing;
}

console.log("🔍 SEO Gate — validating all built pages...\n");

const files = findHtmlFiles(DIST);
const issues: Issue[] = [];
let passed = 0;

for (const file of files) {
  const missing = validate(file);
  if (missing.length > 0) {
    issues.push({ page: file, missing });
  } else {
    passed++;
  }
}

console.log(`  ✓ ${passed} pages passed`);

if (issues.length > 0) {
  console.log(`  ✗ ${issues.length} pages FAILED:\n`);
  for (const issue of issues.slice(0, 20)) {
    console.log(`    ${issue.page}`);
    for (const m of issue.missing) {
      console.log(`      ⚠ missing: ${m}`);
    }
  }
  if (issues.length > 20) {
    console.log(`    ... +${issues.length - 20} more`);
  }
  console.log(`\n❌ SEO Gate FAILED — ${issues.length} pages missing metadata`);
  process.exit(1);
} else {
  console.log(`\n✅ SEO Gate PASSED — all ${passed} pages have complete metadata`);
}
