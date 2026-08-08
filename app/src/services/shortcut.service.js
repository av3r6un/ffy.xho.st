import api from './axios.service';

class ShortcutService {
  static installUrl = 'https://www.icloud.com/shortcuts/7f8d4c63522749b2986c24728c5014c0';

  static async issue(name = 'Apple Shortcut') {
    const response = await api.post('/shortcuts', { name });
    return response.data?.body;
  }

  static async copyTokenAndInstall() {
    const shortcut = await this.issue();
    if (!shortcut?.token) throw new Error('Shortcut token was not returned.');
    await navigator.clipboard.writeText(shortcut.token);
    window.location.assign(this.installUrl);
  }
}

export default ShortcutService;
