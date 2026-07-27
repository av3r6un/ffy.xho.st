<template>
  <div class="loading">
    <Spinner />
    <div class="loading_phrases" role="status" aria-live="polite">
      <Transition name="phrase" mode="out-in">
        <p class="loading_phrase" :key="currentPhraseIndex">
          {{ currentPhrase }}
        </p>
      </Transition>
    </div>
  </div>
</template>
<script>
import Spinner from './Spinner.vue';

export default {
  name: 'Loading',
  components: { Spinner },
  data() {
    return {
      currentPhraseIndex: 0,
      phraseInterval: null,
    };
  },
  computed: {
    loadingPhrases() {
      return this.$tm('loading').map((phrase) => this.$rt(phrase));
    },
    currentPhrase() {
      return this.loadingPhrases[this.currentPhraseIndex] ?? '';
    },
  },
  mounted() {
    this.phraseInterval = window.setInterval(() => {
      this.currentPhraseIndex = (
        this.currentPhraseIndex + 1
      ) % this.loadingPhrases.length;
    }, 1500);
  },
  beforeUnmount() {
    window.clearInterval(this.phraseInterval);
  },
};
</script>
<style lang="scss" scoped>
.loading{
  min-height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 28px;
  text-align: center;
  .spinner{
    width: 64px;
    height: 64px;
  }
  &_phrases{
    position: relative;
    width: min(100%, 460px);
    min-height: 24px;
    overflow: hidden;
  }
  &_phrase{
    margin: 0;
    color: rgba($white, .72);
    font-size: 16px;
    font-weight: 300;
    line-height: 24px;
  }
}

.phrase-enter-active,
.phrase-leave-active{
  transition: opacity .35s ease, transform .35s ease;
}
.phrase-enter-from{
  opacity: 0;
  transform: translateY(8px);
}
.phrase-leave-to{
  opacity: 0;
  transform: translateY(-8px);
}

@media (prefers-reduced-motion: reduce) {
  .phrase-enter-active,
  .phrase-leave-active{
    transition: none;
  }
}
</style>
