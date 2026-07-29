// Blog Template - Service Worker (Stale-While-Revalidate for dynamic content)
const STATIC_CACHE = 'fil-static-v1';
const DYNAMIC_CACHE = 'fil-dynamic-v1';

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(STATIC_CACHE).then(cache => {
      return cache.addAll(['/', '/index.html', '/manifest.json']).catch(() => {});
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== STATIC_CACHE && k !== DYNAMIC_CACHE).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;

  // Static assets: Cache First
  if (url.pathname.match(/\.(css|js|svg|png|jpg|jpeg|gif|webp|woff2?)$/)) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        const fetched = fetch(e.request).then(res => {
          if (res.ok) { const c = res.clone(); caches.open(STATIC_CACHE).then(cache => cache.put(e.request, c)); }
          return res;
        }).catch(() => cached);
        return cached || fetched;
      })
    );
    return;
  }

  // HTML & API: Network First with cache fallback
  e.respondWith(
    fetch(e.request).then(res => {
      if (res.ok) { const c = res.clone(); caches.open(DYNAMIC_CACHE).then(cache => cache.put(e.request, c)); }
      return res;
    }).catch(() => caches.match(e.request))
  );
});

self.addEventListener('message', (e) => { if (e.data?.type === 'SKIP_WAITING') self.skipWaiting(); });