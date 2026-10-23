/* Word Rider : cache hors ligne. Changer VERSION pour forcer une mise à jour. */
const VERSION = 'word-rider-v2';
const FILES = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "icons/apple-touch-icon.png",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/icon-maskable-512.png",
  "fonts/lilita-one-latin-400-normal.woff2",
  "fonts/outfit-latin-400-normal.woff2",
  "fonts/outfit-latin-500-normal.woff2",
  "fonts/outfit-latin-600-normal.woff2",
  "fonts/outfit-latin-700-normal.woff2"
];

/* Réponse sans indicateur de redirection (Safari refuse de servir une page redirigée). */
async function clean(res) {
  if (!res.redirected) return res;
  const body = await res.blob();
  return new Response(body, {status: res.status, statusText: res.statusText, headers: res.headers});
}

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const cache = await caches.open(VERSION);
    /* chaque fichier séparément : un échec ne bloque pas tout le reste */
    await Promise.all(FILES.map(async f => {
      try {
        const res = await fetch(new Request(f, {cache: 'reload'}));
        if (res && res.ok) await cache.put(new Request(f), await clean(res));
      } catch (err) {}
    }));
    /* la page d'accueil doit être là, sinon on réessaiera à la prochaine visite */
    if (!(await cache.match('index.html'))) throw new Error('index.html non mis en cache');
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith('word-rider-') && k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const opts = {ignoreSearch: true, ignoreVary: true};
  e.respondWith((async () => {
    const hit = await caches.match(req, opts);
    if (hit) return hit;
    /* ouverture de l'appli (adresse du dossier, index.html, lancement depuis l'écran d'accueil) */
    if (req.mode === 'navigate') {
      try { return await fetch(req); }
      catch (err) { const home = await caches.match('index.html', opts); if (home) return home; throw err; }
    }
    try {
      const res = await fetch(req);
      if (res && res.ok && new URL(req.url).origin === location.origin) {
        const cache = await caches.open(VERSION);
        cache.put(req, (await clean(res.clone())));
      }
      return res;
    } catch (err) {
      return Response.error();
    }
  })());
});
