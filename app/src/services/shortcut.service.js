import api from './axios.service';

class ShortcutService {
  static installUrl = 'https://www.icloud.com/shortcuts/6b8a026b063145d6955dc07875b9c41f';

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
