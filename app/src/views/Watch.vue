<template>
  <article class="watch page">
    <div class="watch_wrapper" v-if="info">
      <div class="watch_player">
        <div class="player" id="player" ref="playerElement"></div>
        <div class="watch_chapters" v-if="info.chapters">
          <Chapters :chapters="info.chapters" @seek="seekPosition" />
        </div>
      </div>
      <WatchInfo
        :channel="info.channel"
        :title="info.title"
        :stats="gatherStats()"
        :fileInfo="fileInfo"
        :description="info.description"
        @action-requested="completeAction" />
    </div>
    <div class="watch_loading" v-else-if="!info && !error">
      <Loading show-phrases />
    </div>
    <div class="watch_error" v-else-if="error">
      <div class="watch_error-card">
        <span class="watch_error-code">Ошибка</span>
        <h1>Не удалось открыть видео</h1>
        <p>{{ error }}</p>
        <div class="watch_error-actions">
          <Button
            v-if="canRetry"
            text="Повторить"
            classes="accent"
            @click="retry" />
          <Button text="На главную" @click="goHome" />
        </div>
      </div>
    </div>
  </article>
</template>
<script>
import { Playerjs } from '../services/playerjs';
import Backend from '../services/backend.service';
import Chapters from '../components/Chapters.vue';
import WatchInfo from '../components/WatchInfo.vue';
import Loading from '../components/ui/Loading.vue';
import Button from '../components/ui/Button.vue';

export default {
  name: 'Watch',
  components: {
    Chapters, WatchInfo, Loading, Button,
  },
  data() {
    return {
      backend: new Backend(),
      sessionUid: null,
      videoId: null,
      playbackToken: null,
      info: null,
      stats: null,
      selectedFormat: null,
      player: null,
      proxyObserver: null,
      error: null,
      canRetry: false,
      retryTimer: null,
    };
  },
  methods: {
    async fetchVideo() {
      this.$store.commit('setLoading', true);
      try {
        const videoSession = await this.backend.get(`/sessions/${this.sessionUid}`);
        if (videoSession.status === 'pending') {
          this.retryTimer = window.setTimeout(this.fetchVideo, 1500);
          return;
        }
        if (videoSession.status === 'failed') {
          this.error = videoSession.error_message || 'Не удалось подготовить видео.';
          this.canRetry = false;
          return;
        }
        this.info = videoSession.metadata;
        this.videoId = videoSession.video_id;
        this.playbackToken = videoSession.playback_token;
        await this.$nextTick();
        this.initPlayer();
      } catch (err) {
        this.error = this.backend.msg || err?.message || 'Не удалось получить данные сессии.';
        this.canRetry = true;
      } finally {
        this.$store.commit('setLoading', false);
      }
    },
    retry() {
      this.error = null;
      this.canRetry = false;
      this.fetchVideo();
    },
    goHome() {
      this.$router.push('/');
    },
    initPlayer() {
      if (!window.MediaSource && window.ManagedMediaSource) {
        window.MediaSource = window.ManagedMediaSource;
      }

      const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
      const safariFormats = this.info.formats.filter(
        (format) => /^avc[13]/i.test(format.codec || ''),
      );
      const formats = isSafari && safariFormats.length
        ? safariFormats
        : this.info.formats;
      const playbackToken = encodeURIComponent(this.playbackToken);

      this.$refs.playerElement.removeEventListener(
        'quality',
        this.handleQualityChange,
      );
      this.$refs.playerElement.addEventListener(
        'quality',
        this.handleQualityChange,
      );
      this.observeProxyRequests();
      this.player = new Playerjs({
        id: 'player',
        file: formats.map((f) => `[${this.formatLabel(f)}]/proxy/manifest/${this.videoId}/${f.id}.mpd?token=${playbackToken}`).join(','),
        title: this.info.title,
        poster: this.info.thumbnail,
      });
    },
    gatherStats() {
      const arr = [];
      arr.push({ icon: 'favourite', count: this.info.likes });
      arr.push({ icon: 'views', count: this.info.views });
      arr.push({ icon: 'clock', count: this.info.duration });
      return arr;
    },
    seekPosition(seconds) {
      this.player.api('seek', seconds);
    },
    handleQualityChange(event) {
      const quality = event?.info ?? event?.detail ?? this.player?.api('quality');
      this.selectFormat(quality);
    },
    formatLabel(format) {
      return `${format.note}-${format.id}`;
    },
    selectFormat(value) {
      if (value === undefined || value === null || !this.info?.formats) return;
      const selected = String(value);
      const format = this.info.formats.find(
        (item) => item.id === selected || this.formatLabel(item) === selected,
      );
      if (format) this.selectedFormat = format;
    },
    observeProxyRequests() {
      if (!window.PerformanceObserver || this.proxyObserver) return;
      this.proxyObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => this.handleProxyRequest(entry.name));
      });
      try {
        this.proxyObserver.observe({ type: 'resource', buffered: true });
      } catch (err) {
        this.proxyObserver.observe({ entryTypes: ['resource'] });
      }
    },
    handleProxyRequest(requestUrl) {
      let pathname;
      try {
        pathname = new URL(requestUrl, window.location.href).pathname;
      } catch (err) {
        return;
      }

      const parts = pathname.split('/').filter(Boolean);
      if (parts[0] !== 'proxy' || parts[2] !== this.videoId) return;

      if (parts[1] === 'manifest' && parts[3]?.endsWith('.mpd')) {
        this.selectFormat(decodeURIComponent(parts[3].slice(0, -4)));
      } else if (parts[1] === 'video' && parts[3]) {
        this.selectFormat(decodeURIComponent(parts[3]));
      }
    },
    completeAction() {},
  },
  computed: {
    fileInfo() {
      return {
        uploaded: this.info.uploaded,
        fileSize: this.selectedFormatSize,
        language: this.info.language,
      };
    },
    selectedFormatSize() {
      const bytes = Number(this.selectedFormat?.filesize);
      if (!Number.isFinite(bytes) || bytes <= 0) return null;
      const megabytes = bytes / (1024 ** 2);
      return `${megabytes.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 1,
      })} MB`;
    },
  },
  mounted() {
    this.sessionUid = this.$route.query.session;
    if (!this.sessionUid) {
      this.$router.replace('/');
      return;
    }
    this.fetchVideo();
  },
  beforeUnmount() {
    if (this.retryTimer) window.clearTimeout(this.retryTimer);
    this.$refs.playerElement?.removeEventListener(
      'quality',
      this.handleQualityChange,
    );
    this.proxyObserver?.disconnect();
    this.proxyObserver = null;
  },
};
</script>
<style lang="scss" scoped>
.watch {
  padding: 10px 20px;
  &_player{
    display: flex;
    align-items: flex-end;
    width: 100%;
    gap: 20px;
    @media (max-width: 680px) {
      flex-direction: column;
    }
    .player{
      flex: 1;
      @media (max-width: 680px) {
        width: 100%;
        flex: auto;
      }
    }
  }
  &_chapters{
    width: 35%;
    align-self: flex-start;
    @media (max-width: 680px) {
      width: 100%;
    }
  }
  &_loading{
    min-height: 100dvh;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  &_error{
    min-height: calc(100dvh - 20px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  &_error-card{
    width: min(100%, 520px);
    padding: 32px;
    border: 1px solid rgba($white, .1);
    border-radius: 20px;
    background: rgba($white, .04);
    text-align: center;
    h1{
      margin: 10px 0;
      font-size: clamp(24px, 5vw, 36px);
    }
    p{
      margin: 0;
      color: rgba($white, .7);
      line-height: 1.5;
      overflow-wrap: anywhere;
    }
  }
  &_error-code{
    color: $cyan;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: .12em;
  }
  &_error-actions{
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 24px;
    @media (max-width: 490px) {
      flex-direction: column;
    }
  }
}
</style>
