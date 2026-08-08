<template>
  <article class="index page">
    <div class="index_logo">FF<span class="accent">YouTube</span></div>
    <div class="index_about">
      <div class="index_caption">{{ $t('index.caption') }}</div>
      <div class="index_action">{{ $t('index.action') }}</div>
    </div>
    <div class="index_form">
      <IndexForm />
    </div>
    <div class="index_tip">
      <Icon name="share-icon" class="accent" />
      {{ $t('index.tip') }}
    </div>
    <Button @click="openModal" icon="apple-shortcuts"
      text="actions.make_shortcut" classes="accent" v-if="runsAsPWA" />
    <RequestPermissionModal v-model="rpmModalState" v-if="runsAsPWA" />
  </article>
</template>

<script>
import IndexForm from '../components/IndexForm.vue';
import Icon from '../components/ui/Icon.vue';
import Button from '../components/ui/Button.vue';
import RequestPermissionModal from '../components/RequestPermissionModal.vue';
import isPWA from '../utils/validations';

export default {
  name: 'Index',
  components: {
    IndexForm,
    Icon,
    RequestPermissionModal,
    Button,
  },
  data() {
    return {
      rpmModalState: false,
    };
  },
  methods: {
    openModal() {
      this.rpmModalState = true;
    },
  },
  computed: {
    runsAsPWA() {
      return isPWA();
    },
  },
};
</script>
<style lang="scss" scoped>
.index{
  max-width: 540px;
  margin: 0 auto;
  height: calc(100dvh - 80px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 60px;
  @media (max-width: 450px) {
    padding: 40px 20px;
  }
  &_logo{
    font-size: 64px;
    text-align: center;
  }
  &_about{
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 20px;
  }
  &_caption{
    font-size: 36px;
    font-weight: 400;
  }
  &_action{
    font-size: 24px;
    font-weight: 100;
  }
  &_tip{
    display: flex;
    align-items: center;
    gap: 15px;
    justify-content: center;
    color: rgba($white, .6);
    font-weight: 100;
  }
  &_form{
    width: 100%;
  }
}
</style>
