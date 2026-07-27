<template>
  <div class="badge">
    <div class="badge_avatar">
      {{ channel.name[0] }}
    </div>
    <div class="badge_info">
      <div class="badge_info-channel">
        <a :href="channel.uploader_url" class="base_link" target="_blank"
          v-if="channel.verified">
          @{{ channel.name }}
        </a>
        <span class="channel_name" v-else>@{{ channel.name }}</span>
      </div>
      <div class="badge_info-subs">
        {{ $t(
          'channel.subscribers',
          { n: $n(channel.followers, 'compact') },
          channel.followers
        ) }}
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'Badge',
  props: {
    channel: {
      type: Object,
      required: true,
    },
  },
};
</script>
<style lang="scss" scoped>
.badge{
  display: flex;
  align-items: center;
  gap: 20px;
  @media (max-width: 450px) {
    gap: 8px;
  }
  &_avatar{
    background: $cyan;
    border-radius: 50%;
    width: 56px;
    height: 56px;
    font-size: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  &_info{
    display: flex;
    flex-direction: column;
    gap: 5px;
    &-channel{
      font-size: 32px;
      line-height: 30px;
      font-weight: 700;
      @media (max-width: 680px) {
        font-size: 3vw;
        line-height: 1;
      }
      @media (max-width: 450px) {
        font-size: 16px;
      }
    }
    &-subs{
      font-size: 16px;
      line-height: 12px;
      font-weight: 200;
      color: rgba($white, .6);
      @media (max-width: 680px) {
        font-size: 2vw;
      }
      @media (max-width: 450px) {
        font-size: 13px;
      }
    }
  }
}
</style>
