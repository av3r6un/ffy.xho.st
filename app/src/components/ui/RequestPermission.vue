<template>
  <div class="request">
    <div class="request_info">
      <div class="request_info-label">{{ label }}</div>
      <div class="request_info-caption">{{ caption }}</div>
    </div>
    <div class="request_action" @click="requestPermission">
      <Button :text="action" class="accent small"
        :disabled="permission === 'granted'" />
    </div>
  </div>
</template>
<script>
import Button from './Button.vue';

export default {
  name: 'ReqPermission',
  components: { Button },
  emits: ['update:permission', 'permission-requested'],
  props: {
    label: {
      type: String,
      required: true,
    },
    action: {
      type: String,
      required: true,
    },
    caption: {
      type: String,
      required: false,
    },
  },
  data() {
    return {
      permission: Notification.permission,
    };
  },
  mounted() {
    this.$emit('update:permission', this.permission, 'mounted');
    document.addEventListener('visibilitychange', this.syncPermission);
  },
  beforeUnmount() {
    document.removeEventListener('visibilitychange', this.syncPermission);
  },
  methods: {
    async requestPermission() {
      if (this.permission === 'granted') return;
      this.permission = await Notification.requestPermission();
      this.$emit('permission-requested', this.permission);
    },
    syncPermission() {
      if (document.visibilityState === 'visible') {
        this.permission = Notification.permission;
        this.$emit('update:permission', this.permission, 'visibilitychange');
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.request{
  display: flex;
  align-items: center;
  gap: 30px;
  &_info{
    display: flex;
    flex-direction: column;
    gap: 3px;
    &-label{
      color: $white;
      line-height: 14px;
    }
    &-caption{
      font-size: 12px;
      font-weight: 300;
      color: rgba($white, .8);
    }
  }
}
</style>
