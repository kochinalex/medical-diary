// Simple service worker for PWA standalone installation
const CACHE_NAME = 'med-diary-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Pass-through to network for dynamic data
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
