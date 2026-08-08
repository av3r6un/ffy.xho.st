<template>
  <div class="modal" @keydown.esc="hide" v-if="visible" @click.self="hide">
    <div class="modal_content">
      <div class="modal_content-close">
        <Icon name="close" @click="hide"/>
      </div>
      <slot />
    </div>
  </div>
</template>
<script>
import Icon from '../ui/Icon.vue';

export default {
  name: 'BaseModal',
  components: { Icon },
  emits: ['update:modelValue'],
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    visible: {
      get() { return this.modelValue; },
      set(val) { this.$emit('update:modelValue', val); },
    },
  },
  methods: {
    hide() {
      this.visible = false;
    },
    show() {
      this.visible = true;
    },
  },
};
</script>
<style lang="scss">
.modal{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba($black, .5);
  &_content{
    border-radius: 24px;
    border: 1px solid $cyan;
    padding: 20px;
    position: relative;
    background: rgba($white, .05);
    backdrop-filter: blur(6px);
    &-close{
      position: absolute;
      top: 20px;
      right: 20px;
      cursor: pointer;
    }
  }
}
</style>
