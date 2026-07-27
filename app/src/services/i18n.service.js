import { createI18n } from 'vue-i18n';
import russianRule from '../utils/pluralization';
import en from '../locales/en.yaml';
import ru from '../locales/ru.yaml';

const numberFormats = {
  'en-US': {
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
  'ru-RU': {
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
  'en-US': {
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
  'ru-RU': {
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

export default createI18n({
  legacy: false,
  fallbackLocale: 'en',
  pluralizationRules: {
    ru: russianRule,
  },
  messages: { en, ru },
  numberFormats,
  datetimeFormats,
});
