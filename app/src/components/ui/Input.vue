<template>
  <div class="input">
    <input
      v-model="localValue"
      :type="type"
      :placeholder="placeholder"
      :required="required"
      :autocomplete="defAutocomplete"
      :autofocus="autofocus"
      @change="$emit('change')"
      class="input_wide"
    >
  </div>
</template>
<script>
export default {
  name: 'Input',
  emits: ['update:modelValue', 'change'],
  props: {
    modelValue: {
      required: true,
    },
    type: {
      type: String,
      default: 'text',
    },
    placeholder: {
      type: String,
      default: 'Введите текст',
    },
    required: {
      type: Boolean,
      default: false,
    },
    autocomplete: {
      type: Boolean,
      default: false,
    },
    autofocus: {
      type: Boolean,
      default: false,
    },
    icon: {
      type: String,
      required: false,
    },
  },
  data() {
    return {};
  },
  computed: {
    defAutocomplete() {
      return this.autocomplete ? 'on' : 'off';
    },
    localValue: {
      get() { return this.modelValue; },
      set(val) { this.$emit('update:modelValue', val); },
    },
  },
};
</script>
<style lang="scss" scoped>
.input{
  border-radius: $border-sm;
  padding: 0 12px;
  background: rgba($white, .2);
  &.accent{
    background: transparent;
    border: 1px solid rgba($cyan, .2);
  }
  &_wide{
    width: 100%;
    outline: none;
    border: none;
    height: 35px;
    border-radius: inherit;
    background: none;
    color: $white;
    &::placeholder{
      font-family: $font;
      font-size: 15px;
      color: rgba($white, .7);
    }
    &:focus{
      &::placeholder{
        visibility: hidden;
      }
    }
  }
}
</style>
