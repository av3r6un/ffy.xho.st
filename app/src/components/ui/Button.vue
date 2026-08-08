<template>
  <div class="button" :class="[classes, { disabled }]" @click="$emit(eventToEmit)"
    :disabled="disabled" >
    <Icon :name="icon" v-if="icon" :class="{ dark: hasAccent }"/>
    <span class="text" :class="{ visible: !icon }" v-if="text">
      {{ $te(text) ? $t(text) : text }}
    </span>
  </div>
</template>
<script>
import Icon from './Icon.vue';

export default {
  name: 'Button',
  components: { Icon },
  emits: ['click', 'submit', 'void'],
  props: {
    text: {
      type: String,
      required: false,
    },
    icon: {
      type: String,
      required: false,
    },
    classes: {
      type: String,
      required: false,
    },
    type: {
      type: String,
      required: false,
    },
    content: {
      type: [String, Object],
      required: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    eventToEmit() {
      if (this.disabled) return 'void';
      return this.type === 'submit' ? 'submit' : 'click';
    },
    hasAccent() {
      return this.classes?.includes('accent');
    },
  },
};
</script>
<style lang="scss" scoped>
.button{
  user-select: none;
  border-radius: 32px;
  border: 1px solid rgba($white, .1);
  padding: 12px 24px;
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  &:disabled,
  &.disabled {
    background: rgba($cyan, .6) !important;
    cursor: not-allowed;
  }
  @media (max-width: 680px) {
    font-size: 2.3vw;
    padding: 8px 16px;
    width: 100%;
    justify-content: center;
  }
  &.accent{
    border-color: $cyan;
    background: $cyan;
    color: $black;
  }
  &.small{
    height: 35px;
    border-radius: $border-sm;
  }
  &.cube{
    width: 35px;
    padding: 0;
    margin-right: 10px;
  }
  .text{
    @media (max-width: 490px) {
      display: none;
      &.visible{
        display: block;
        font-size: 14px;
      }
    }
  }
}
</style>
