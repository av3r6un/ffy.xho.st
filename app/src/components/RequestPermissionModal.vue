<template>
  <div class="request_permission-modal">
    <BaseModal v-model="state" class="rpm">
      <RequestPermission
        :label="$t('notifications.permission.title')"
        :caption="$t('notifications.permission.description')"
        :action="$t('notifications.permission.allow')"
        @update:permission="handlePermissionUpdate"
        @permission-requested="syncSubscription($event, true)"
      />
      <Button icon="apple-shortcuts" text="actions.make_shortcut" classes="accent"
        :disabled="!pushReady" @click="makeShortcut" />
    </BaseModal>
  </div>
</template>
<script>
import BaseModal from './layout/BaseModal.vue';
import Button from './ui/Button.vue';
import RequestPermission from './ui/RequestPermission.vue';
import PushSubscriptionService from '../services/push.service';
import ShortcutService from '../services/shortcut.service';

export default {
  name: 'RPM',
  components: { BaseModal, RequestPermission, Button },
  emits: ['update:modelValue'],
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      permission: Notification.permission,
      pushReady: false,
    };
  },
  computed: {
    state: {
      get() { return this.modelValue; },
      set(val) { this.$emit('update:modelValue', val); },
    },
  },
  methods: {
    handlePermissionUpdate(permission, source) {
      const testMode = source === 'mounted' ? 'development' : null;
      return this.syncSubscription(permission, testMode);
    },
    async syncSubscription(permission, testMode = null) {
      this.permission = permission;
      this.pushReady = false;
      if (permission !== 'granted') return;

      try {
        const subscription = await PushSubscriptionService.subscribe();
        this.pushReady = true;
        const sendTest = testMode === true
          || (testMode === 'development'
            && await PushSubscriptionService.isBackendDebugEnabled());
        if (sendTest) await PushSubscriptionService.sendTest(subscription);
      } catch (error) {
        console.error('Unable to register push subscription', error);
      }
    },
    async makeShortcut() {
      try {
        await ShortcutService.copyTokenAndInstall();
      } catch (error) {
        console.error('Unable to create Shortcut token', error);
        // eslint-disable-next-line no-alert
        window.alert(error?.response?.data?.data?.message || error.message);
      }
    },
  },
};
</script>
<style lang="scss">
.request_permission-modal{
  .rpm .modal_content{
    padding-top: 64px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
}
</style>
