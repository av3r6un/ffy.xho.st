<template>
  <div class="file_info">
    <div class="file_info-item uploaded">
      <div class="file_info-title">{{ $t('info.uploaded') }}</div>
      <div class="file_info-caption">{{ $d(localValue.uploaded * 1000, 'short') }}</div>
    </div>
    <div class="file_info-item lang" v-if="localValue.language">
      <div class="file_info-title">{{ $t('info.lang') }}</div>
      <div class="file_info-caption">{{ language }}</div>
    </div>
    <div class="file_info-item size" v-if="localValue.fileSize">
      <div class="file_info-title">{{ $t('info.file_size') }}</div>
      <div class="file_info-caption">{{ localValue.fileSize || $t('info.file_not_selected')}}</div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'FileInfo',
  emits: ['update:modelValue'],
  props: {
    modelValue: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {};
  },
  computed: {
    localValue: {
      get() { return this.modelValue; },
      set(val) { this.$emit('update:modelValue', val); },
    },
    language() {
      return this.$te(`languages.${this.localValue.language}`)
        ? this.$t(`languages.${this.localValue.language}`)
        : this.localValue.language;
    },
  },
};
</script>
<style lang="scss" scoped>
.file_info{
  display: flex;
  align-items: center;
  gap: 20px;
  &-title{
    font-size: 16px;
    color: rgba($white, .6);
    @media (max-width: 450px) {
      font-size: 2.5vw;
    }
  }
  &-caption{
    font-size: 24px;
    @media (max-width: 450px) {
      font-size: 4.5vw;
    }
  }
  &-item{
    min-width: 200px;
  }
}
</style>
