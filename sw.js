// OSWeb service worker: precache the shell so the desktop loads offline. Bump VERSION on every release.
const VERSION = 'osweb-v2';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'vendor/tailwind.css', 'vendor/fa/css/all.min.css',
  'vendor/fa/webfonts/fa-solid-900.woff2', 'vendor/fa/webfonts/fa-regular-400.woff2', 'vendor/fa/webfonts/fa-brands-400.woff2',
  'vendor/wallpapers/sequoia.svg', 'vendor/wallpapers/sequoia-dark.svg', 'vendor/wallpapers/sonoma.svg', 'vendor/wallpapers/ventura.svg',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); return res; }).catch(() => caches.match('index.html'))));
});
