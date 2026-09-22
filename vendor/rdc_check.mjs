// dtdskills scorer primitive: rdc check (rules C1-C16) on candidate text.
// Usage: node rdc_check.mjs <candidate-SKILL.md> <live-skill-dir> [repo-root]
// Prints one JSON document on the last stdout line; exit 0 = valid.
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const [candPath, baseDir, repoRoot] = process.argv.slice(2);
if (!candPath || !baseDir) {
  console.log(JSON.stringify({ ok: false, errors: 1, detail: 'usage: rdc_check.mjs <candidate> <baseDir> [repoRoot]' }));
  process.exit(2);
}
const root = repoRoot || process.env.RDC_LIB || dirname(fileURLToPath(import.meta.url));
let lib;
try {
  lib = await import(pathToFileURL(join(root, 'lib', 'dtd.mjs')).href);
} catch (e) {
  console.log(JSON.stringify({ ok: false, errors: 1, detail: `lib load failed: ${e.message}` }));
  process.exit(2);
}
try {
  const text = readFileSync(candPath, 'utf8');
  const r = lib.resolveFile(text, baseDir);
  if (!r.hasDoctype) {
    console.log(JSON.stringify({ ok: true, plain: true, errors: 0 }));
    process.exit(0);
  }
  const report = lib.check(r.text, { includes: r.includes });
  const findings = (report.findings || []).slice(0, 20).map((f) => ({
    level: f.level, code: f.code, msg: String(f.msg || '').slice(0, 200),
  }));
  console.log(JSON.stringify({
    ok: !!report.ok, errors: report.errors || 0, findings, stats: report.stats || {},
  }));
  process.exit(report.ok ? 0 : 1);
} catch (e) {
  console.log(JSON.stringify({ ok: false, errors: 1, detail: `check crashed: ${e.message}` }));
  process.exit(2);
}
