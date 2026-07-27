<template>
  <div class="stats">
    <div class="stats-stat" v-for="(stat, idx) in localValue" :key="idx">
      <Icon :name="stat.icon" class="accent" />
      <span class="count" v-if="stat.icon !== 'clock'">
        {{ $n(stat.count, 'compact') }}
      </span>
      <span class="count" v-else>
        {{ normalTime(stat.count) }}
      </span>
    </div>
  </div>
</template>
<script>
import Icon from './Icon.vue';

export default {
  name: 'Stats',
  emits: ['update:modelValue'],
  components: { Icon },
  props: {
    modelValue: {
      type: Array[Object],
      required: true,
    },
  },
  data() {
    return {};
  },
  methods: {
    normalTime(secs) {
      const hours = secs / 3600;
      const minutes = secs / 60;
      const seconds = secs % 60;
      return hours >= 1
        ? `${hours.toFixed().padStart(2, '0')}:${minutes.toFixed().padStart(2, '0')}:${seconds.toFixed().padStart(2, '0')}`
        : `${minutes.toFixed().padStart(2, '0')}:${seconds.toFixed().padStart(2, '0')}`;
    },
  },
  computed: {
    localValue: {
      get() { return this.modelValue; },
      set(val) { this.$emit('update:modelValue', val); },
    },
  },
};
</script>
<style lang="scss" scoped>
.stats{
  display: flex;
  align-items: center;
  gap: 10px;
  &-stat{
    display: flex;
    align-items: center;
    gap: 5px;
  }
}
</style>
