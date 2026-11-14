'use strict';

const CACHE_NAME = 'astra-site-shell-v6';
const PRECACHE_URLS = [
  './',
  './index.html',
  './dashboard/',
  './dashboard/index.html',
  './dashboard/app.js',
  './output/demo-report.json',
  './data/nasa/osd569-cbc.json'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function (cache) { return cache.addAll(PRECACHE_URLS); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(keys
          .filter(function (key) {
            return (key.indexOf('astra-site-shell-') === 0 ||
              key.indexOf('astra-dashboard-shell-') === 0) && key !== CACHE_NAME;
          })
          .map(function (key) { return caches.delete(key); }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (event) {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    caches.match(request).then(function (cached) {
      if (cached) return cached;
      return fetch(request).then(function (response) {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(request, copy);
          });
        }
        return response;
      }).catch(function () {
        if (request.mode === 'navigate') {
          const fallback = url.pathname.indexOf('/dashboard') >= 0
            ? './dashboard/index.html'
            : './index.html';
          return caches.match(fallback);
        }
        return new Response('This ASTRA resource is not available offline.', {
          status: 503,
          headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
      });
    })
  );
});