import { createI18n } from 'vue-i18n';
import russianRule from '../utils';
import en from '../locales/en.yaml';
import ru from '../locales/ru.yaml';

const LOCALE_COOKIE = 'locale';
const LOCALE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365;
const supportedLocales = ['en', 'ru'];

function normalizeLocale(locale) {
  const normalized = String(locale || '').toLowerCase().split('-')[0];
  return supportedLocales.includes(normalized) ? normalized : null;
}

function readLocaleCookie() {
  const prefix = `${LOCALE_COOKIE}=`;
  const cookie = document.cookie
    .split(';')
    .map((part) => part.trim())
    .find((part) => part.startsWith(prefix));
  return cookie ? normalizeLocale(decodeURIComponent(cookie.slice(prefix.length))) : null;
}

function writeLocaleCookie(locale) {
  const secure = window.location.protocol === 'https:' ? '; Secure' : '';
  document.cookie = `${LOCALE_COOKIE}=${encodeURIComponent(locale)}`
    + `; Path=/; Max-Age=${LOCALE_COOKIE_MAX_AGE}; SameSite=Lax${secure}`;
}

const initialLocale = readLocaleCookie()
  || normalizeLocale(navigator.language)
  || 'en';

const numberFormats = {
  en: {
    currency: {
      style: 'currency',
      currency: 'USD',
      useGrouping: true,
      currencyDisplay: 'symbol',
    },
    decimal: {
      style: 'decimal',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    },
    compact: {
      notation: 'compact',
      compactDisplay: 'short',
      maximumFractionDigits: 1,
    },
  },
  ru: {
    currency: {
      style: 'currency',
      currency: 'RUB',
      useGrouping: true,
      currencyDisplay: 'symbol',
      symbol: '₽',
    },
    decimal: {
      style: 'decimal',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    },
    compact: {
      notation: 'compact',
      compactDisplay: 'short',
      maximumFractionDigits: 1,
    },
  },
};

const datetimeFormats = {
  en: {
    short: { year: 'numeric', month: 'short', day: 'numeric' },
    long: {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      weekday: 'short',
      hour: 'numeric',
      minute: 'numeric',
    },
  },
  ru: {
    short: { year: 'numeric', month: 'short', day: 'numeric' },
    long: {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      weekday: 'short',
      hour: 'numeric',
      minute: 'numeric',
    },
  },
};

const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'en',
  pluralizationRules: {
    ru: russianRule,
  },
  messages: { en, ru },
  numberFormats,
  datetimeFormats,
});

export function setLocale(locale) {
  const normalized = normalizeLocale(locale);
  if (!normalized) return false;

  i18n.global.locale.value = normalized;
  document.documentElement.lang = normalized;
  writeLocaleCookie(normalized);
  return true;
}

setLocale(initialLocale);

export default i18n;
