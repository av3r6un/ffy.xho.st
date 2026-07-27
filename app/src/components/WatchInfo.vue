<template>
  <article class="info">
    <div class="info_title">{{ title }}</div>
    <div class="info_section">
      <Badge :channel="channel" />
      <div class="info_section-actions">
        <Button text="actions.share" clases="share"
          icon="share" @click="$emit('actionRequested')" />
        <Button text="actions.download" clases="download"
          icon="download" @click="$emit('actionRequsted')" />
      </div>
    </div>
    <div class="info_section bordered">
      <Stats v-model="localStats" />
      <FileInfo v-model="localFiles" />
      <p class="description" v-if="description">
        {{ description }}
      </p>
    </div>
  </article>
</template>
<script>
import Badge from './ui/Badge.vue';
import Button from './ui/Button.vue';
import FileInfo from './ui/FileInfo.vue';
import Stats from './ui/Stats.vue';

export default {
  name: 'WatchInfo',
  emits: ['actionRequested'],
  components: {
    Button,
    Badge,
    Stats,
    FileInfo,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    channel: {
      type: Object,
      required: true,
    },
    stats: {
      type: Array[Object],
      required: true,
    },
    fileInfo: {
      type: Object,
      required: true,
    },
    description: {
      type: String,
      required: false,
    },
  },
  data() {
    return {};
  },
  computed: {
    localStats: {
      get() { return this.stats; },
    },
    localFiles: {
      get() { return this.fileInfo; },
    },
  },
};
</script>
<style lang="scss" scoped>
.info{
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-top: 30px;
  &_title{
    font-size: 32px;
    font-weight: 600;
    @media (max-width: 680px) {
      font-size: 4vw;
    }
  }
  &_section{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    &-actions{
      display: flex;
      gap: 20px;
      @media (max-width: 450px) {
        gap: 8px;
      }
    }
    &.bordered{
      flex-direction: column;
      align-items: flex-start;
      border: 1px solid rgba($white, .1);
      border-radius: $border-lg;
      padding: 12px;
    }
  }
  .description {
    white-space: pre-wrap;
    font-size: 12px;
    font-weight: 500;
  }
}
</style>
