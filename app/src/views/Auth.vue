<template>
  <article class="auth page">
    <div class="auth_wrapper">
      <div class="auth_title centered">Авторизация</div>
      <form class="auth_form" @submit.prevent="login">
        <input type="email" autofocus="on"
          required placeholder="E-mail" v-model="authForm.email" class="input_wide">
        <input type="password" required
          placeholder="Пароль" v-model="authForm.password" class="input_wide">
        <button type="submit" class="btn btn_submit">Войти</button>
      </form>
    </div>
  </article>
</template>
<script>
export default {
  name: 'Auth',
  data() {
    return {
      authForm: {
        email: null,
        password: null,
      },
    };
  },
  methods: {
    login() {
      this.$store.dispatch('login', { data: this.authForm })
        .then(() => this.$router.push('/'));
    },
  },
};
</script>
<style lang="scss" scoped>
.auth{
  &_wrapper{
    color: $white;
    max-width: 400px;
    margin: 0 auto;
  }
  &_title{
    font-size: 24px;
    font-weight: 600;
    text-align: center;
  }
  &_form{
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 12px;
  }
}
</style>
