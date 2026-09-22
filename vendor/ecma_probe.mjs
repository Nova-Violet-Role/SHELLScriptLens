// Probe pure functions of lib/dtd.mjs for ground-truth measurement.
// Usage: node ecma_probe.mjs <fn> <json-arg>
// Prints JSON {ok, out} or {ok:false, error}.
import { pathToFileURL, fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = process.env.RDC_LIB || dirname(fileURLToPath(import.meta.url));
const lib = await import(pathToFileURL(join(root, 'lib', 'dtd.mjs')).href);
const [fn, raw] = process.argv.slice(2);
const arg = JSON.parse(raw ?? 'null');
try {
  let out;
  if (fn === 'normalize') out = lib.normalize(arg);
  else if (fn === 'yamlScalar') out = lib.yamlScalar(arg);
  else if (fn === 'escapeRe') out = lib.escapeRe(arg);
  else if (fn === 'flattenConditionals') out = lib.flattenConditionals(arg);
  else if (fn === 'verifyFile') out = lib.verifyFile(arg);
  else if (fn === 'splitDoctype') {
    const d = lib.splitDoctype(arg);
    out = d ? { name: d.name } : null;
  } else if (fn === 'modelRefs') out = lib.modelRefs(arg);
  else if (fn === 'frontmatterFindings') out = lib.frontmatterFindings(arg);
  else throw new Error('unknown fn ' + fn);
  console.log(JSON.stringify({ ok: true, out }));
  process.exit(0);
} catch (e) {
  console.log(JSON.stringify({ ok: false, error: String(e && e.message || e).slice(0, 200) }));
  process.exit(1);
}
