<template>
  <div class="spinner" :style="colorStyles">
    <div class="spinner_wrapper" v-show="$store.getters.loading">
      <div class="spinner_inner one"></div>
      <div class="spinner_inner two"></div>
      <div class="spinner_inner three"></div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'Spinner',
  props: {
    primary: {
      type: String,
      default: '#EFEFFA',
    },
    secondary: {
      type: String,
      default: '#EFEFFA',
    },
    tertiary: {
      type: String,
      default: '#EFEFFA',
    },
  },
  data() {
    return {};
  },
  computed: {
    colorStyles() {
      return `--primary: ${this.primary}; --secondary: ${this.secondary}; --tertiary: ${this.tertiary}`;
    },
  },
};
</script>
<style lang="scss" scoped>
.spinner{
  position: relative;
  &_wrapper{
    position: absolute;
    top: calc(50% - 32px);
    left: calc(50% - 32px);
    width: 64px;
    height: 64px;
    margin: 0 auto;
    border-radius: 50%;
    perspective: 800px;
  }
  &_inner {
    position: absolute;
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    &.one{
      left: 0%;
      top: 0%;
      animation: rotate-one 1s linear infinite;
      border-bottom: 3px solid var(--primary);
    }
    &.two{
      right: 0%;
      top: 0%;
      animation: rotate-two 1s linear infinite;
      border-right: 3px solid var(--secondary);
    }
    &.three{
      right: 0%;
      bottom: 0%;
      animation: rotate-three 1s linear infinite;
      border-top: 3px solid var(--tertiary);
    }
  }
}

@keyframes rotate-one {
  0% {
    transform: rotateX(35deg) rotateY(-45deg) rotateZ(0deg);
  }
  100% {
    transform: rotateX(35deg) rotateY(-45deg) rotateZ(360deg);
  }
}
@keyframes rotate-two {
  0% {
    transform: rotateX(50deg) rotateY(10deg) rotateZ(0deg);
  }
  100% {
    transform: rotateX(50deg) rotateY(10deg) rotateZ(360deg);
  }
}
@keyframes rotate-three {
  0% {
    transform: rotateX(35deg) rotateY(55deg) rotateZ(0deg);
  }
  100% {
    transform: rotateX(35deg) rotateY(55deg) rotateZ(360deg);
  }
}
</style>
