/* global self */

function readPayload(event) {
  if (!event.data) return {};
  try {
    return event.data.json();
  } catch (error) {
    return { body: event.data.text() };
  }
}

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
  const payload = readPayload(event);
  const title = payload.title || 'MediaVault';
  const options = {
    body: payload.body || '',
    icon: payload.icon || '/img/icons/android-chrome-192x192.png',
    badge: payload.badge || '/img/icons/android-chrome-192x192.png',
    tag: payload.tag,
    lang: payload.lang,
    data: {
      ...payload.data,
      url: payload.url || '/',
    },
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const requestedUrl = new URL(event.notification.data?.url || '/', self.location.origin);
  const targetUrl = requestedUrl.origin === self.location.origin
    ? requestedUrl.href
    : self.location.origin;

  event.waitUntil((async () => {
    const clients = await self.clients.matchAll({
      type: 'window',
      includeUncontrolled: true,
    });
    const client = clients[0];
    if (client) {
      await client.navigate(targetUrl);
      return client.focus();
    }
    return self.clients.openWindow(targetUrl);
  })());
});
