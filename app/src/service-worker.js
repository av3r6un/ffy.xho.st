/* eslint-env serviceworker */

import { cleanupOutdatedCaches, createHandlerBoundToURL, precacheAndRoute } from 'workbox-precaching';
import { NavigationRoute, registerRoute } from 'workbox-routing';

const DEFAULT_NOTIFICATION = {
  title: 'MediaVault',
  body: 'Open the app to see the update.',
  url: '/#/',
};

precacheAndRoute(self.__WB_MANIFEST);
cleanupOutdatedCaches();

registerRoute(new NavigationRoute(
  createHandlerBoundToURL('/index.html'),
  {
    denylist: [
      /^\/api\//,
      /^\/auth\//,
      /^\/health(?:\/|$)/,
      /^\/proxy\//,
      /^\/shortcut\//,
    ],
  },
));

function readPushPayload(event) {
  if (!event.data) return DEFAULT_NOTIFICATION;
  try {
    return { ...DEFAULT_NOTIFICATION, ...event.data.json() };
  } catch (error) {
    return { ...DEFAULT_NOTIFICATION, body: event.data.text() };
  }
}

function getInternalUrl(value) {
  const url = new URL(value || DEFAULT_NOTIFICATION.url, self.location.origin);
  return url.origin === self.location.origin
    ? url.href
    : new URL(DEFAULT_NOTIFICATION.url, self.location.origin).href;
}

self.addEventListener('push', (event) => {
  const payload = readPushPayload(event);
  const url = getInternalUrl(payload.url);
  const options = {
    body: payload.body,
    icon: payload.icon || '/img/icons/android-chrome-192x192.png',
    badge: payload.badge || '/img/icons/msapplication-icon-144x144.png',
    tag: payload.tag || 'mediavault-update',
    data: { url, ...(payload.data || {}) },
  };

  if (payload.lang) options.lang = payload.lang;
  event.waitUntil(self.registration.showNotification(payload.title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = getInternalUrl(event.notification.data?.url);

  event.waitUntil(self.clients.matchAll({
    type: 'window',
    includeUncontrolled: true,
  }).then(async (windowClients) => {
    const currentClient = windowClients.find(
      (client) => new URL(client.url).origin === self.location.origin,
    );

    if (currentClient) {
      if (currentClient.url !== targetUrl && 'navigate' in currentClient) {
        await currentClient.navigate(targetUrl);
      }
      return currentClient.focus();
    }

    return self.clients.openWindow(targetUrl);
  }));
});
