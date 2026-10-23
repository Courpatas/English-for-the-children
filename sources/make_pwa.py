"""Construit la version installable (PWA) : index.html, manifest, service worker, icônes.

Usage (depuis la racine du dépôt) :
    python3 sources/gen.py sources/app_fragment.html
    python3 sources/make_pwa.py sources/app_fragment.html
"""
import sys, os, re, json
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frag = open(sys.argv[1], encoding="utf-8").read()
VERSION = sys.argv[2] if len(sys.argv) > 2 else "v1"

# 1. retire l'en-tête propre à la plateforme de publication (titre, polices distantes)
frag = re.sub(r"<title>.*?</title>\s*", "", frag, count=1, flags=re.S)
frag = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\s*', "", frag, count=1)
frag = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", frag)
frag = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>\s*', "", frag)

fonts = """
@font-face{font-family:'Lilita One';font-style:normal;font-weight:400;font-display:swap;src:url(fonts/lilita-one-latin-400-normal.woff2) format('woff2')}
""" + "".join(
    "@font-face{font-family:'Outfit';font-style:normal;font-weight:%d;font-display:swap;src:url(fonts/outfit-latin-%d-normal.woff2) format('woff2')}\n" % (w, w)
    for w in (400, 500, 600, 700))

extra_css = """
html{background:#061826;-webkit-text-size-adjust:100%;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;-webkit-tap-highlight-color:transparent;overscroll-behavior-y:none}
button,.opt,.tile,.mi{touch-action:manipulation;-webkit-user-select:none;user-select:none}
input{-webkit-appearance:none;appearance:none}
"""
# injecte les polices et le CSS mobile au début de la première balise <style>
frag = frag.replace("<style>", "<style>" + fonts + extra_css, 1)

# 2. enregistrement du service worker
sw_reg = """
<script>
if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}
</script>
"""

head = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Word Rider</title>
<meta name="theme-color" content="#061826">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Word Rider">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" href="icons/icon-192.png">
</head>
<body>
"""
out = head + frag + sw_reg + "\n</body>\n</html>\n"
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)

# 3. manifeste
manifest = {
    "name": "Word Rider",
    "short_name": "Word Rider",
    "description": "1 328 mots d'anglais pour la 3ème, en exercices interactifs.",
    "lang": "fr",
    "start_url": "./index.html",
    "scope": "./",
    "display": "standalone",
    "orientation": "any",
    "background_color": "#061826",
    "theme_color": "#061826",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
json.dump(manifest, open(os.path.join(ROOT, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 4. icônes : deux vagues (turquoise et corail) sur fond bleu lagon
def icon(size, pad):
    S = size * 4
    im = Image.new("RGB", (S, S), "#061826")
    d = ImageDraw.Draw(im)
    import math
    p = int(S * pad)
    w = S - 2 * p
    def wave(y0, color, th):
        pts = []
        for i in range(0, 201):
            x = p + w * i / 200
            y = y0 + math.sin(i / 200 * math.pi * 4) * w * 0.07
            pts.append((x, y))
        d.line(pts, fill=color, width=th, joint="curve")
        r = th // 2
        for x, y in (pts[0], pts[-1]):
            d.ellipse((x - r, y - r, x + r, y + r), fill=color)
    th = int(S * 0.085)
    wave(S * 0.40, "#19d3c5", th)
    wave(S * 0.62, "#ff6a4d", th)
    # soleil
    r = int(S * 0.075)
    cx, cy = int(S * 0.70), int(S * 0.22)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#ffd23f")
    return im.resize((size, size), Image.LANCZOS)

os.makedirs(os.path.join(ROOT, "icons"), exist_ok=True)
icon(180, 0.14).save(os.path.join(ROOT, "icons/apple-touch-icon.png"))
icon(192, 0.14).save(os.path.join(ROOT, "icons/icon-192.png"))
icon(512, 0.14).save(os.path.join(ROOT, "icons/icon-512.png"))
icon(512, 0.26).save(os.path.join(ROOT, "icons/icon-maskable-512.png"))

# 5. service worker : tout est mis en cache à la première visite
files = ["./", "index.html", "manifest.webmanifest",
         "icons/apple-touch-icon.png", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png"]
files += ["fonts/" + f for f in sorted(os.listdir(os.path.join(ROOT, "fonts")))]
sw = """/* Word Rider : cache hors ligne. Changer VERSION pour forcer une mise à jour. */
const VERSION = 'word-rider-%s';
const FILES = %s;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('word-rider-') && k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request, {ignoreSearch: true}).then(hit => {
      if (hit) return hit;
      return fetch(e.request).then(res => {
        if (res && res.ok && new URL(e.request.url).origin === location.origin) {
          const copy = res.clone();
          caches.open(VERSION).then(c => c.put(e.request, copy));
        }
        return res;
      }).catch(() => caches.match('index.html'));
    })
  );
});
""" % (VERSION, json.dumps(files, indent=2))
open(os.path.join(ROOT, "sw.js"), "w", encoding="utf-8").write(sw)
print("OK", len(out), "octets, cache de", len(files), "fichiers")
