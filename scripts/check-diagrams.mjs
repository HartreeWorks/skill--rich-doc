#!/usr/bin/env node
// Parse every ```mermaid fence in a Markdown file, so a diagram that won't draw
// is caught before the reader opens the doc.
//
//   node check-diagrams.mjs <doc.md>
//
// Needs the `mermaid` and `jsdom` packages. It looks for them in the folder named
// by $RICH_DOC_NODE_MODULES (a folder whose node_modules holds both), then in the
// current folder. Exit 0: every diagram parses. Exit 1: at least one fails.
// Exit 2: the packages weren't found, so nothing was checked.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const doc = process.argv[2];
if (!doc) {
  console.error("usage: node check-diagrams.mjs <doc.md>");
  process.exit(2);
}

const bases = [process.env.RICH_DOC_NODE_MODULES, process.cwd()].filter(Boolean);
let req = null;
for (const base of bases) {
  try {
    const r = createRequire(path.join(path.resolve(base), "package.json"));
    r.resolve("mermaid");
    r.resolve("jsdom");
    req = r;
    break;
  } catch {}
}
if (!req) {
  console.log("Skipped: mermaid and jsdom not found. Set RICH_DOC_NODE_MODULES to a folder that has them installed.");
  process.exit(2);
}

const { JSDOM } = req("jsdom");
const dom = new JSDOM("<!doctype html><body></body>");
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.DOMParser = dom.window.DOMParser;
globalThis.Element = dom.window.Element;
const { default: mermaid } = await import(req.resolve("mermaid"));
mermaid.initialize({ startOnLoad: false });

const md = fs.readFileSync(doc, "utf8");
const blocks = [...md.matchAll(/```mermaid\n([\s\S]*?)```/g)].map((m) => m[1]);
let failed = 0;
for (const [i, block] of blocks.entries()) {
  try {
    await mermaid.parse(block);
    console.log(`diagram ${i + 1}: ok`);
  } catch (e) {
    failed += 1;
    const msg = String(e?.message ?? e).split("\n").slice(0, 3).join(" | ");
    console.log(`diagram ${i + 1}: FAILS: ${msg}`);
  }
}
if (!blocks.length) console.log("No Mermaid diagrams.");
process.exit(failed ? 1 : 0);
