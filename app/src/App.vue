<template>
  <Header v-show="$route.name !== 'home'" />
  <router-view/>
</template>

<script>
import Header from './components/Header.vue';

export default {
  name: 'App',
  components: { Header },
};
</script>

<style lang="scss"></style>
