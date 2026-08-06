<template>
  <div
    class="pull-refresh"
    :class="{ ready: isReady, refreshing }"
    :style="indicatorStyle"
    role="status"
    aria-live="polite">
    <span class="pull-refresh_icon" aria-hidden="true"></span>
    <span class="pull-refresh_text">{{ statusText }}</span>
  </div>
</template>

<script>
const REFRESH_THRESHOLD = 64;
const MAX_PULL_DISTANCE = 88;

export default {
  name: 'PullRefresh',
  data() {
    return {
      startX: 0,
      startY: 0,
      pullDistance: 0,
      isPulling: false,
      refreshing: false,
      refreshTimer: null,
    };
  },
  computed: {
    isReady() {
      return this.pullDistance >= REFRESH_THRESHOLD;
    },
    indicatorStyle() {
      return {
        opacity: this.pullDistance > 0 ? 1 : 0,
        transform: `translate3d(-50%, ${this.pullDistance - 56}px, 0)`,
      };
    },
    statusText() {
      if (this.refreshing) return this.$t('pull_refresh.refreshing');
      return this.isReady
        ? this.$t('pull_refresh.release')
        : this.$t('pull_refresh.pull');
    },
  },
  methods: {
    isAtTop() {
      return (document.scrollingElement?.scrollTop ?? window.scrollY) <= 0;
    },
    handleTouchStart(event) {
      if (this.refreshing || event.touches.length !== 1 || !this.isAtTop()) return;
      this.startX = event.touches[0].clientX;
      this.startY = event.touches[0].clientY;
      this.isPulling = true;
    },
    handleTouchMove(event) {
      if (!this.isPulling || event.touches.length !== 1) return;

      const deltaX = event.touches[0].clientX - this.startX;
      const deltaY = event.touches[0].clientY - this.startY;
      if (Math.abs(deltaX) > Math.abs(deltaY) || deltaY <= 0 || !this.isAtTop()) {
        this.reset();
        return;
      }

      if (event.cancelable) event.preventDefault();
      this.pullDistance = Math.min(deltaY * 0.5, MAX_PULL_DISTANCE);
    },
    handleTouchEnd() {
      if (!this.isPulling) return;
      if (!this.isReady) {
        this.reset();
        return;
      }

      this.isPulling = false;
      this.refreshing = true;
      this.pullDistance = REFRESH_THRESHOLD;
      this.refreshTimer = window.setTimeout(() => window.location.reload(), 150);
    },
    reset() {
      this.isPulling = false;
      this.pullDistance = 0;
    },
  },
  mounted() {
    window.addEventListener('touchstart', this.handleTouchStart, { passive: true });
    window.addEventListener('touchmove', this.handleTouchMove, { passive: false });
    window.addEventListener('touchend', this.handleTouchEnd, { passive: true });
    window.addEventListener('touchcancel', this.reset, { passive: true });
  },
  beforeUnmount() {
    window.removeEventListener('touchstart', this.handleTouchStart);
    window.removeEventListener('touchmove', this.handleTouchMove);
    window.removeEventListener('touchend', this.handleTouchEnd);
    window.removeEventListener('touchcancel', this.reset);
    window.clearTimeout(this.refreshTimer);
  },
};
</script>

<style lang="scss" scoped>
.pull-refresh{
  position: fixed;
  top: max(8px, env(safe-area-inset-top));
  left: 50%;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border: 1px solid rgba($white, .12);
  border-radius: 999px;
  background: rgba($black, .92);
  box-shadow: 0 8px 24px rgba(0, 0, 0, .24);
  color: $white;
  font-size: 13px;
  pointer-events: none;
  transition: opacity .18s ease, transform .18s ease;
  will-change: opacity, transform;

  &_icon{
    width: 9px;
    height: 9px;
    border-right: 2px solid $cyan;
    border-bottom: 2px solid $cyan;
    transform: translateY(-2px) rotate(45deg);
    transition: transform .18s ease;
  }

  &.ready &_icon{
    transform: translateY(2px) rotate(225deg);
  }

  &.refreshing &_icon{
    width: 12px;
    height: 12px;
    border: 2px solid rgba($cyan, .25);
    border-top-color: $cyan;
    border-radius: 50%;
    animation: pull-refresh-spin .7s linear infinite;
  }
}

@keyframes pull-refresh-spin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .pull-refresh,
  .pull-refresh_icon{
    transition: none;
  }
}
</style>
