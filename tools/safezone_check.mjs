// Headless safe-zone scan of a built composition. Called by tools/safezone.py.
//   node tools/safezone_check.mjs <public-dir> <zones-json> <duration> <step> <chrome-path>
// Prints one JSON line: {samples, violations:[{key, zone, severity, from, to, rect}]}

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import puppeteer from "puppeteer-core";

const [, , pubDir, zonesJson, durStr, stepStr, chromePath] = process.argv;
const zones = JSON.parse(zonesJson);
const dur = parseFloat(durStr);
const step = parseFloat(stepStr);

const MIME = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".png": "image/png",
  ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml", ".ttf": "font/ttf",
  ".otf": "font/otf", ".woff2": "font/woff2", ".woff": "font/woff", ".webp": "image/webp" };

// Static server; media is refused -- the check only needs layout, not pixels.
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  if (p === "/") p = "/index.html";
  const f = path.join(pubDir, p);
  if (/\.(mp4|webm|mov|wav|mp3|m4a)$/i.test(f) || !f.startsWith(path.resolve(pubDir))) {
    res.writeHead(404); res.end(); return;
  }
  fs.readFile(f, (err, data) => {
    if (err) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { "Content-Type": MIME[path.extname(f).toLowerCase()] || "application/octet-stream" });
    res.end(data);
  });
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const port = server.address().port;

const browser = await puppeteer.launch({ executablePath: chromePath, headless: true,
  args: ["--no-sandbox", "--disable-gpu", "--mute-audio"] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
  await page.evaluateOnNewDocument(() => { window.__timelines = {}; });
  await page.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: "load", timeout: 120000 });
  await page.evaluate(() => document.fonts.ready);

  const hits = await page.evaluate((zones, dur, step) => {
    const tl = window.__timelines.main;
    if (!tl) throw new Error("no window.__timelines.main");
    const W = 1080, H = 1920;
    const clips = [...document.querySelectorAll("[data-start]")]
      .filter((e) => e.id !== "root" && !["VIDEO", "AUDIO"].includes(e.tagName));
    const roots = ["#over", "#behind", "#under", "#panel"].map((s) => document.querySelector(s)).filter(Boolean);
    const SKIP = /(^|\s)(flood|dots|rays|tile|scan|spd|cf|pkt|ic)(\s|$)/;
    const BOX = /(^|\s)(stk|stk2|crd|card|btn|chip|chip2|badge|bub|note|pola|av|coin|phone|stamp)(\s|$)/;
    const SHAPES = new Set(["path", "circle", "rect", "line", "polyline", "polygon", "ellipse"]);
    const cls = (e) => (typeof e.className === "string" ? e.className : e.className?.baseVal || "");

    const cands = [];
    for (const r of roots) for (const e of r.querySelectorAll("*")) {
      const tag = e.tagName.toLowerCase();
      if (SKIP.test(cls(e)) || e.id === "flash" || tag === "svg" || tag === "video") continue;
      const isText = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
      const isBox = BOX.test(cls(e));
      const isMedia = tag === "img" || (SHAPES.has(tag) && e.closest("svg") && !e.closest(".ic"));
      if (isText || isBox || isMedia) cands.push({ e, isText, isBox });
    }

    const visible = (e) => {
      let op = 1;
      for (let a = e; a && a !== document.documentElement; a = a.parentElement) {
        const cs = getComputedStyle(a);
        if (cs.display === "none" || cs.visibility === "hidden") return false;
        op *= parseFloat(cs.opacity);
        if (op < 0.05) return false;
      }
      return true;
    };
    const rectOf = (c) => {
      if (c.isText && !c.isBox) {
        const rg = document.createRange(); rg.selectNodeContents(c.e);
        const r = rg.getBoundingClientRect(); if (r.width && r.height) return r;
      }
      return c.e.getBoundingClientRect();
    };
    const keyOf = (e) => {
      const own = e.id ? `#${e.id}` : "";
      const anc = e.parentElement?.closest("[id]");
      const txt = [...e.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(" ").slice(0, 24);
      const src = e.tagName === "IMG" ? (e.getAttribute("src") || "").split("/").pop() : "";
      return [own || (anc ? `#${anc.id} > ${e.tagName.toLowerCase()}` : e.tagName.toLowerCase()), src, txt && `"${txt}"`]
        .filter(Boolean).join(" ");
    };

    const out = [];
    let n = 0;
    for (let t = 0; t <= dur + 1e-6; t += step, n++) {
      for (const c of clips) {
        const s = parseFloat(c.dataset.start || "0"), d = parseFloat(c.dataset.duration || "0");
        c.style.visibility = t >= s && t < s + d ? "" : "hidden";
      }
      tl.seek(t, false);
      for (const c of cands) {
        if (!visible(c.e)) continue;
        const r = rectOf(c);
        const area = r.width * r.height;
        if (!area || area > 0.5 * W * H) continue;
        if (r.right < 0 || r.bottom < 0 || r.left > W || r.top > H) continue;
        for (const [zone, [x0, y0, x1, y1]] of Object.entries(zones)) {
          const ow = Math.min(r.right, x1) - Math.max(r.left, x0);
          const oh = Math.min(r.bottom, y1) - Math.max(r.top, y0);
          if (ow <= 0 || oh <= 0) continue;
          const ov = ow * oh;
          if (ov < Math.max(900, 0.12 * area)) continue;
          out.push({ t: +t.toFixed(2), key: keyOf(c.e), zone, severity: c.isText || c.isBox ? "error" : "warning",
            rect: [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)] });
        }
      }
    }
    return { samples: n, hits: out };
  }, zones, dur, step);

  // Keep only what stays in a zone for 2+ consecutive samples (>= 2*step).
  const groups = new Map();
  for (const h of hits.hits) {
    const k = `${h.key}|${h.zone}`;
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(h);
  }
  const violations = [];
  for (const list of groups.values()) {
    let run = [list[0]];
    const flush = () => {
      if (run.length >= 2) violations.push({ key: run[0].key, zone: run[0].zone, severity: run[0].severity,
        from: run[0].t, to: run[run.length - 1].t, rect: run[Math.floor(run.length / 2)].rect });
    };
    for (let i = 1; i < list.length; i++) {
      if (list[i].t - list[i - 1].t <= step * 1.5 + 1e-6) run.push(list[i]);
      else { flush(); run = [list[i]]; }
    }
    flush();
  }
  violations.sort((a, b) => a.from - b.from);
  console.log(JSON.stringify({ samples: hits.samples, violations }));
} finally {
  await browser.close();
  server.close();
}
