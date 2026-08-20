// Service worker: precached app shell, stale-while-revalidate for API calls
// and images. Bump VERSION on every deploy to invalidate old caches.

const VERSION = 'v1';
const SHELL_CACHE = `blc-shell-${VERSION}`;
const RUNTIME_CACHE = `blc-runtime-${VERSION}`;

const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './css/app.css',
  './js/app.js',
  './js/api.js',
  './js/config.js',
  './js/demo-data.js',
  './icons/icon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== SHELL_CACHE && k !== RUNTIME_CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  const isShell = url.origin === location.origin;
  const isApi = url.pathname.includes('/wp-json/');
  const isImage = request.destination === 'image';

  if (isShell && !isApi) {
    // Shell: cache-first (updates arrive via VERSION bump).
    event.respondWith(
      caches.match(request).then(hit => hit ?? fetch(request))
    );
    return;
  }

  if (isApi || isImage) {
    // Live data and media: try network, keep a copy, fall back to it offline.
    event.respondWith(
      caches.open(RUNTIME_CACHE).then(async (cache) => {
        try {
          const res = await fetch(request);
          if (res.ok) cache.put(request, res.clone());
          return res;
        } catch (err) {
          const hit = await cache.match(request);
          if (hit) return hit;
          throw err;
        }
      })
    );
  }
});
