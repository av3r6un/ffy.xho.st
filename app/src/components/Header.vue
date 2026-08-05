<template>
  <div class="header">
    <div class="header_logo">
      <div class="logo">
        <router-link class="base_link" to="/">
          <img src="/img/logo-small.svg" alt="logo" class="base_image">
        </router-link>
      </div>
    </div>
    <div class="header_navbar"></div>
  </div>
</template>
<script>
export default {
  name: 'Header',
  data() {
    return {};
  },
};
</script>
<style lang="scss" scoped>
.header{
  padding: 10px 30px;
  &_logo{
    display: flex;
    .logo{
      height: 30px;
    }
  }
}
</style>
