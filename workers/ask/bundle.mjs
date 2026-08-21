// Flatten the worker's three modules into one pasteable file.
//
// WHY THIS EXISTS. Deploying with wrangler needs a terminal, a Node install and a working
// local checkout. That is a fine ask for a laptop and a poor one for a Chromebook.
// Cloudflare's dashboard creates a Worker from a single pasted file, so this produces exactly
// that: bundled.js, one module, no imports, byte for byte the same logic.
//
// WHY IT IS GENERATED AND NOT HAND ASSEMBLED. A hand copied version drifts from the modules
// the tests run against, and the first sign of the drift would be a reader getting an answer
// the guard no longer checks. This runs from the same files the tests import, and it FAILS
// LOUDLY on a name collision rather than letting one definition silently win. That is not
// theoretical: in JavaScript a later function declaration simply replaces an earlier one of
// the same name, with no error anywhere.
//
// Run: node workers/ask/bundle.mjs

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));

// Dependency order. checks.js and retriever.js depend on nothing, retrieve.js depends on
// retriever.js, answer.js depends on both of those and on checks.js, worker.js depends on
// answer.js.
const MODULES = ["checks.js", "retriever.js", "retrieve.js", "answer.js", "worker.js"];

// Renames applied to a module's own top level declarations before it is appended, so two
// modules may each keep the name that reads best in their own file.
const RENAME = {};

const IMPORT_RE = /^\s*import\s[^;]*?from\s*["']\.\/[^"']+["'];?\s*$/gm;

// A BARE RE-EXPORT GOES THE SAME WAY AN IMPORT DOES, and for the same reason: it exists to
// join two files that are about to become one. retriever.js is generated for two consumers, a
// page that needs plain function declarations and a worker that needs them exported, so it
// carries `export { ... };` at the end. Left in the bundle it would re-export a retriever's
// internals from a Worker module, which is harmless and is also a promise nobody made.
// `export default` is NOT touched: that one is the Worker's entry point.
const REEXPORT_RE = /^\s*export\s*\{[^}]*\}\s*;?\s*$/gm;

function topLevelNames(src) {
  const names = new Set();
  const re = /^export\s+(?:async\s+)?(function|const|let|var|class)\s+([A-Za-z_$][\w$]*)/gm;
  const re2 = /^(?:async\s+)?(function|const|let|var|class)\s+([A-Za-z_$][\w$]*)/gm;
  for (const m of src.matchAll(re)) names.add(m[2]);
  for (const m of src.matchAll(re2)) names.add(m[2]);
  return names;
}

function renameIdent(src, from, to) {
  // Word boundaries only, and never after a dot, so obj.verify is left alone.
  return src.replace(new RegExp(`(?<!\\.)\\b${from}\\b`, "g"), to);
}

const seen = new Map();
const parts = [];
const collisions = [];

for (const file of MODULES) {
  let src = readFileSync(join(HERE, file), "utf8");
  src = src.replace(IMPORT_RE, "").replace(REEXPORT_RE, "");

  for (const [from, to] of Object.entries(RENAME[file] || {})) {
    src = renameIdent(src, from, to);
  }

  for (const name of topLevelNames(src)) {
    if (seen.has(name)) collisions.push(`${name}: ${seen.get(name)} and ${file}`);
    else seen.set(name, file);
  }

  parts.push(`// ${"=".repeat(74)}\n// ${file}\n// ${"=".repeat(74)}\n\n${src.trim()}\n`);
}

if (collisions.length) {
  console.error("name collisions, add them to RENAME rather than shipping this:");
  for (const c of collisions) console.error("  " + c);
  process.exit(1);
}

const header = `// GENERATED FILE. Do not edit.
//
// The ask worker's three modules flattened into one, so it can be deployed by pasting into
// the Cloudflare dashboard without a terminal. Regenerate with:
//
//   node workers/ask/bundle.mjs
//
// Edit the modules instead. \`node workers/ask/bundle.mjs --check\` goes red when this file is
// not what they produce, and workers/ask/test.js runs it, so a stale paste-file cannot pass CI.

`;

const out = join(HERE, "bundled.js");
const built = header + parts.join("\n");

// --check, WHICH IS THE HALF THAT WAS MISSING. bundled.js is what actually gets deployed, by
// being pasted into a dashboard, and until now nothing anywhere compared it to the modules the
// tests run against. A stale one would ship the previous design while every test passed
// against the current one, which is the exact failure this file was written to prevent and the
// only one it could not catch.
if (process.argv.includes("--check")) {
  let onDisk = "";
  try { onDisk = readFileSync(out, "utf8"); } catch { /* absent counts as stale */ }
  if (onDisk !== built) {
    console.error("bundled.js is not what the modules produce. Run: node workers/ask/bundle.mjs");
    process.exit(1);
  }
  console.log(`bundled.js is current  (${MODULES.length} modules, ${seen.size} names)`);
  process.exit(0);
}

writeFileSync(out, built);
console.log(`bundled.js  <-  ${MODULES.join(", ")}  ` +
            `(${seen.size} top level names, no collisions)`);
