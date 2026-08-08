import api from './axios.service';

function urlBase64ToUint8Array(value) {
  const padding = '='.repeat((4 - (value.length % 4)) % 4);
  const base64 = (value + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = window.atob(base64);
  return Uint8Array.from([...raw].map((char) => char.charCodeAt(0)));
}

class PushSubscriptionService {
  static isSupported() {
    return 'Notification' in window
      && 'serviceWorker' in navigator
      && 'PushManager' in window;
  }

  static async subscribe() {
    if (!this.isSupported()) {
      throw new Error('Push notifications are not supported.');
    }
    if (Notification.permission !== 'granted') {
      throw new Error('Notification permission has not been granted.');
    }

    const registration = await navigator.serviceWorker.ready;
    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
      const response = await api.get('/push/vapid-public-key');
      const publicKey = response.data?.body?.public_key;
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicKey),
      });
    }

    await api.post('/push/subscriptions', subscription.toJSON());
    return subscription;
  }

  static async isBackendDebugEnabled() {
    const response = await api.get('/push/config');
    return response.data?.body?.debug === true;
  }

  static async unsubscribe() {
    if (!this.isSupported()) return false;

    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    if (!subscription) return false;

    await api.delete('/push/subscriptions', {
      data: { endpoint: subscription.endpoint },
    });
    return subscription.unsubscribe();
  }

  static async sendTest(subscription) {
    const response = await api.post('/push/test', {
      endpoint: subscription.endpoint,
    });
    return response.data?.body;
  }
}

export default PushSubscriptionService;
