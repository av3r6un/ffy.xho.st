<template>
  <PullRefresh />
  <Header v-show="$route.name !== 'home'" />
  <Spinner />
  <router-view v-show="!$store.getters.loading" />
</template>

<script>
import Header from './components/Header.vue';
import PullRefresh from './components/PullRefresh.vue';
import Spinner from './components/ui/Spinner.vue';

export default {
  name: 'App',
  components: { Header, PullRefresh, Spinner },
};
</script>

<style lang="scss"></style>
