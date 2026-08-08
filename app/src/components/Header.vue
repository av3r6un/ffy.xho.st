<template>
  <div class="header">
    <div class="header_logo">
      <div class="logo" v-show="$route.name !== 'home'">
        <router-link class="base_link" to="/">
          <img src="/img/logo-small.svg" alt="logo" class="base_image">
        </router-link>
      </div>
    </div>
    <div class="header_navbar">
      <div class="header_navbar-item">
        <div class="language" @click="moveToNextLang">
          <span class="lang">{{ currentLang }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { setLocale } from '../services/i18n.service';

export default {
  name: 'Header',
  data() {
    return {};
  },
  methods: {
    moveToNextLang() {
      let langIndex = this.$i18n.availableLocales
        .findIndex((l) => l === this.currentLang.toLowerCase());
      if (langIndex < (this.$i18n.availableLocales.length - 1)) {
        langIndex += 1;
      } else if (langIndex === (this.$i18n.availableLocales.length - 1)) {
        langIndex = 0;
      }
      setLocale(this.$i18n.availableLocales[langIndex]);
    },
  },
  computed: {
    currentLang() {
      return this.$i18n.locale.split('-')[0].toUpperCase();
    },
  },
};
</script>
<style lang="scss" scoped>
.header{
  padding: 30px;
  display: flex;
  justify-content: space-between;
  &_logo{
    display: flex;
    .logo{
      height: 30px;
    }
  }
  &_navbar{
    &-item{
      .language{
        cursor: pointer;
      }
    }
  }
}
</style>
