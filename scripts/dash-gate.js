#!/usr/bin/env node
/**
 * Dash Gate — build-time check that no published content contains an
 * em-dash (—), en-dash (–), or double-hyphen (--) used as punctuation.
 * Ported from wealth-bank/scripts/dash-gate.js. HARD-FAIL blocks deploy.
 * Spec: T142 (Bob order, wealth-bank#89) — fleet-wide rule, gate applies
 * to any publish path with a build to hang it on. petdeals has one.
 *
 * Scope note: only src/content/blog is scanned — the one hand-authored
 * editorial collection (no `draft` field in the schema, so all files
 * here are live). data/products.json (1063 scraped Shopee listings,
 * refreshed by scripts/scrape-offers.py) is explicitly OUT of scope:
 * it contains 219 em/en-dash hits in seller-provided title/description
 * text, but that's third-party marketplace copy re-fetched on every
 * scrape, not authored editorial voice. Gating it would hard-fail the
 * build on data we don't write and can't durably clean. Flagged to Bob
 * rather than silently gated or silently ignored — see wealth-bank#89.
 *
 * False-positive guards: markdown link targets (the `(...)` in
 * `[text](...)`) and code spans/fences are stripped before scanning,
 * because auto-generated heading anchors can legitimately contain "--"
 * when a heading has a punctuation collision (e.g. "+" or ":" removed
 * during slugify leaves two adjacent spaces -> two hyphens). Neither is
 * prose punctuation, so neither should trip the ban.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const EM_DASH = '—';
const EN_DASH = '–';

const THAI_DASH_REPAIR_DOC = '~/.oracle/conduct/T142-thai-dash-repair.md';

/**
 * Thai-script detection for the failure message (T142 conduct addendum,
 * 2026-08-24). A dash-ban hit in Thai copy is repaired differently from a
 * Latin one: delete the dash, keep the space, and if the dash carried
 * contrast, carry it with an explicit connective (แต่ / ยกเว้น). The conduct
 * doc explains the repair; this returns a pointer to it when the offending
 * snippet contains Thai script, else '' (Latin hits need no special rule).
 * Thai Unicode block: U+0E00–U+0E7F.
 */
export function thaiRepairPointer(snippet) {
  if (/[\u0E00-\u0E7F]/.test(snippet || '')) {
    return `\n     ↳ Thai-script hit: repair per ${THAI_DASH_REPAIR_DOC} (delete dash keep space; if contrast, carry with แต่/ยกเว้น)`;
  }
  return '';
}

const CONTENT_DIRS = [
  { dir: 'src/content/blog', type: 'blog' },
];

function stripNonProse(text) {
  return text
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`[^`\n]*`/g, '')
    .replace(/\]\([^)]*\)/g, ']()')
    .replace(/^---\n[\s\S]*?\n---/m, '')
    .replace(/^---\s*$/gm, '')
    .replace(/--[a-zA-Z][\w-]*\s*:/g, '')
    .replace(/var\(--[\w-]*\)/g, '')
    .replace(/<!--[\s\S]*?-->/g, '');
}

export function scanContent(rawText) {
  const text = stripNonProse(rawText);
  const hits = [];
  const lines = text.split('\n');

  lines.forEach((line, idx) => {
    if (line.includes(EM_DASH)) {
      hits.push({ char: 'em-dash (—)', line: idx + 1, snippet: line.trim().slice(0, 80) });
    }
    if (line.includes(EN_DASH)) {
      hits.push({ char: 'en-dash (–)', line: idx + 1, snippet: line.trim().slice(0, 80) });
    }
    const doubleHyphenMatches = line.match(/(?<!-)--(?!-)/g);
    if (doubleHyphenMatches) {
      hits.push({ char: 'double-hyphen (--)', line: idx + 1, snippet: line.trim().slice(0, 80) });
    }
  });

  return hits;
}

function runSelfTest() {
  console.log('=== DASH GATE SELF-TEST (negative control) ===');
  const dirty = 'ตัวอย่างประโยค — มีอีเอ็มแดชแอบอยู่ตรงนี้';
  const dirtyHits = scanContent(dirty);
  console.log(`Input: ${JSON.stringify(dirty)}`);
  console.log(`Hits: ${JSON.stringify(dirtyHits)}`);
  if (dirtyHits.length === 0) {
    console.error('❌ SELF-TEST FAILED — scanner did not catch a known em-dash. The gate is broken, not the content.');
    process.exit(1);
  }
  console.log('✅ SELF-TEST PASSED — scanner correctly flags a known em-dash.\n');

  const clean = 'ตัวอย่างประโยค: ไม่มีเครื่องหมายต้องห้าม';
  const cleanHits = scanContent(clean);
  console.log(`Input: ${JSON.stringify(clean)}`);
  console.log(`Hits: ${JSON.stringify(cleanHits)}`);
  if (cleanHits.length !== 0) {
    console.error('❌ SELF-TEST FAILED — scanner flagged clean text with no banned characters.');
    process.exit(1);
  }
  console.log('✅ SELF-TEST PASSED — scanner does not false-positive on clean text.');

  // POSITIVE CONTROL for double-hyphen EXCLUSIONS (BoB #142, 2026-08-23):
  // exclusions can silently neuter the gate, so plant a real prose "--" AND
  // code/structural doubles, and assert the gate catches prose but not code.
  const proseDash = 'เริ่มจากคำถามของคุณ -- แล้วให้ตัวเลขตอบ';
  const codeDashes = ['---', '--ink: #0A0A0A', 'color: var(--red);', '<!-- comment -->'].join('\n');
  const proseHits = scanContent(proseDash);
  const codeHits = scanContent(codeDashes);
  if (proseHits.length === 0) {
    console.error('❌ POSITIVE CONTROL FAILED — gate no longer catches a REAL prose double-hyphen.');
    process.exit(1);
  }
  if (codeHits.length !== 0) {
    console.error('❌ POSITIVE CONTROL FAILED — gate still fires on code/structural double-hyphens.');
    process.exit(1);
  }
  console.log('✅ POSITIVE CONTROL PASSED — prose double-hyphen caught, code/structural excluded.');
  process.exit(0);
}

function main() {
  const ROOT = process.cwd();
  let errors = 0;
  let thaiHits = 0;
  let filesScanned = 0;
  let filesSkippedDraft = 0;

  for (const { dir, type } of CONTENT_DIRS) {
    const fullDir = path.join(ROOT, dir);
    if (!fs.existsSync(fullDir)) continue;

    const files = fs.readdirSync(fullDir).filter(f => f.endsWith('.md') || f.endsWith('.mdx'));

    for (const file of files) {
      const content = fs.readFileSync(path.join(fullDir, file), 'utf-8');
      const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
      if (fmMatch && /^draft:\s*true/m.test(fmMatch[1])) {
        filesSkippedDraft++;
        continue;
      }

      filesScanned++;
      const hits = scanContent(content);
      for (const hit of hits) {
        const pointer = thaiRepairPointer(hit.snippet);
        if (pointer) thaiHits++;
        console.error(`  ❌ FAIL [${type}] ${file}:${hit.line} — ${hit.char} → "${hit.snippet}"${pointer}`);
        errors++;
      }
    }
  }

  console.log('');
  console.log(`Scanned: ${filesScanned} published files (+ ${filesSkippedDraft} draft, skipped)`);
  if (errors > 0) {
    console.error(`🚫 DASH GATE FAILED — ${errors} banned-character hit(s) across published content`);
    console.error(`   Replace em-dash/en-dash/double-hyphen with a colon, comma, or period. T142.`);
    if (thaiHits > 0) {
      console.error(`   ↳ ${thaiHits} Thai-script hit(s): repair per ${THAI_DASH_REPAIR_DOC} (delete dash keep space; if contrast, carry with แต่/ยกเว้น).`);
    }
    process.exit(1);
  } else {
    console.log('✅ DASH GATE PASSED — no em-dash, en-dash, or double-hyphen in published content');
  }
}

const isMain = process.argv[1] === fileURLToPath(import.meta.url);
if (isMain) {
  if (process.argv.includes('--self-test')) {
    runSelfTest();
  } else {
    main();
  }
}
