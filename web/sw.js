// Offline support. App files: network first (so updates show up), falling back to the cache.
// Pyodide from the CDN: cache first (versioned URLs never change), so Python works offline after one load.
const VERSION = "leetling-v2";
const SHELL = [
  "./", "index.html", "css/app.css", "manifest.webmanifest", "vendor/preact-htm.mjs",
  "js/app.js", "js/dex.js", "js/store.js", "js/python.js", "js/editor.js", "js/text.js", "js/sync.js",
  "js/runner-worker.js", "js/judge.py", "data/problems.json", "data/problems-full.json", "data/runner.py",
  "icons/icon-192.png", "icons/apple-touch-icon.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== VERSION && k !== "pyodide").map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.hostname === "cdn.jsdelivr.net" && url.pathname.startsWith("/pyodide/")) {
    e.respondWith(caches.open("pyodide").then(async (c) => {
      const hit = await c.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok) c.put(req, res.clone());
      return res;
    }));
    return;
  }
  if (url.origin !== location.origin) return;
  e.respondWith(fetch(req).then((res) => {
    if (res.ok) caches.open(VERSION).then((c) => c.put(req, res.clone()));
    return res;
  }).catch(() => caches.match(req, { ignoreSearch: true }).then((hit) => hit || caches.match("index.html"))));
});
