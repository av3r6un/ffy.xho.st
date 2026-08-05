<template>
  <form class="form" @submit.prevent="parseLink">
    <Input type="text" v-model="indexLink" class="accent" required />
    <Button icon="clipboard" classes="accent small cube dark" @click="pasteClipboard" />
  </form>
</template>
<script>
import Input from './ui/Input.vue';
import Button from './ui/Button.vue';
import Backend from '../services/backend.service';

export default {
  name: 'IndexForm',
  components: { Input, Button },
  data() {
    return {
      backend: new Backend(),
      indexLink: '',
    };
  },
  methods: {
    async parseLink() {
      const videoUrl = this.indexLink.trim();
      if (!videoUrl) return;
      const videoSession = await this.backend.post('/sessions', {
        video_url: videoUrl,
      });
      if (videoSession?.uid) {
        this.$router.push({
          path: '/watch',
          query: { session: videoSession.uid },
        });
      }
    },
    async pasteClipboard() {
      this.indexLink = await navigator.clipboard.readText();
      this.parseLink();
    },
  },
};
</script>
<style lang="scss" scoped>
.form{
  display: flex;
  align-items: center;
  gap: 20px;
  width: 100%;
  .input{
    flex: 1;
  }
  &_buttons{
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  @media (max-width: 450px) {
    flex-direction: column;
    gap: 5px;
    .input{
      width: 100%;
    }
  }
}
</style>
