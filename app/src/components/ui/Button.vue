<template>
  <div class="button" :class="classes" @click="$emit(eventToEmit)">
    <Icon :name="icon" v-if="icon"/>
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
  emits: ['click', 'submit'],
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
  },
  computed: {
    eventToEmit() {
      return this.type === 'submit' ? 'submit' : 'click';
    },
  },
};
</script>
<style lang="scss" scoped>
.button{
  border-radius: 32px;
  border: 1px solid rgba($white, .1);
  padding: 12px 24px;
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
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
