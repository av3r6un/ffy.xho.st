<template>
  <div class="chapters">
    <div class="chapters_title" @click="toggleChapters">
      <span class="title">
        {{ $t('chapters.title') }}
      </span>
      <Icon :name="`chevron-${state ? 'up' : 'down'}`" />
    </div>
    <div class="chapters_wrapper" v-show="state">
      <div class="chapters_chapter" v-for="(ch, idx) in chapters" :key="idx"
        @click="$emit('seek', ch.start_time)">
        <div class="chapters_chapter-time">
          <span class="accent">{{ normalTime(ch.start_time) }}</span>
        </div>
        <div class="chapters_chapter-title">{{ ch.title }}</div>
      </div>
    </div>
  </div>
</template>
<script>
import Icon from './ui/Icon.vue';

export default {
  name: 'Chapters',
  components: { Icon },
  emits: ['seek'],
  props: {
    chapters: {
      type: Array,
      required: false,
    },
  },
  data() {
    return {
      state: true,
    };
  },
  methods: {
    normalTime(secs) {
      const minutes = Math.floor(secs / 60);
      const seconds = Math.round(secs % 60);
      return `${minutes.toFixed().padStart(2, '0')}:${seconds.toFixed().padStart(2, '0')}`;
    },
    toggleChapters() {
      this.state = !this.state;
    },
  },
};
</script>
<style lang="scss" scoped>
.chapters{
  display: flex;
  gap: 10px;
  flex-direction: column;
  &_title{
    font-size: 24px;
    margin-left: 15px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  &_wrapper{
    padding: 10px;
    border: 1px solid rgba($white, .05);
    border-radius: $border;
    max-height: 375px;
    overflow-y: auto;
    overscroll-behavior-y: none;
  }
  &_chapter{
    display: flex;
    align-items: center;
    padding: 10px 5px;
    gap: 15px;
    border: 1px solid transparent;
    border-radius: $border-sm;
    cursor: pointer;
    &:hover{
      border-color: rgba($cyan, .05);
      background: rgba($white, .05);
    }
    &-time{
      width: 50px;
      text-align: right;
    }
  }
}
</style>
