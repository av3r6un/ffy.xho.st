<template>
  <form class="form" @submit.prevent="parseLink">
    <Input type="text" v-model="indexLink" class="accent" required @change="parseLink" />
    <Button icon="clipboard" classes="accent small cube dark" @click="pasteClipboard" />
  </form>
</template>
<script>
import Input from './ui/Input.vue';
import Button from './ui/Button.vue';

export default {
  name: 'IndexForm',
  components: { Input, Button },
  data() {
    return {
      indexLink: '',
    };
  },
  methods: {
    getVideoId(value) {
      const VIDEO_ID_PATTERN = /^[A-Za-z0-9_-]{11}$/;
      try {
        const url = new URL(
          /^https?:\/\//i.test(value) ? value : `https://${value}`,
        );
        const host = url.hostname.replace(/^www\./, '');
        let videoId = null;

        if (host === 'youtu.be') {
          [videoId] = url.pathname.slice(1).split('/');
        } else if (host === 'youtube.com' || host.endsWith('.youtube.com')) {
          videoId = url.searchParams.get('v')
            || url.pathname.match(/^\/(?:shorts|live|embed)\/([^/]+)/)?.[1];
        }

        return VIDEO_ID_PATTERN.test(videoId) ? videoId : null;
      } catch {
        return null;
      }
    },
    parseLink() {
      const videoId = this.getVideoId(this.indexLink.trim());
      if (videoId) {
        this.$router.push({ path: '/watch', query: { v: videoId } });
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
