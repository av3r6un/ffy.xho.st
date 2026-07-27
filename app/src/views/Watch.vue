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
      <Loading />
    </div>
  </article>
</template>
<script>
import { Playerjs } from '../services/playerjs';
import Backend from '../services/backend.service';
import Chapters from '../components/Chapters.vue';
import WatchInfo from '../components/WatchInfo.vue';
import Loading from '../components/ui/Loading.vue';

export default {
  name: 'Watch',
  components: { Chapters, WatchInfo, Loading },
  data() {
    return {
      backend: new Backend(),
      videoId: null,
      info: null,
      stats: null,
      selectedFormat: null,
      player: null,
      error: null,
    };
  },
  methods: {
    async fetchVideo() {
      this.$store.commit('setLoading', true);
      try {
        this.info = await this.backend.get(`/v/${this.$route.query.v}`);
        await this.$nextTick();
        this.initPlayer();
      } catch (err) {
        this.error = err;
      } finally {
        this.$store.commit('setLoading', false);
      }
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

      this.$refs.playerElement.removeEventListener(
        'quality',
        this.handleQualityChange,
      );
      this.$refs.playerElement.addEventListener(
        'quality',
        this.handleQualityChange,
      );
      this.player = new Playerjs({
        id: 'player',
        file: formats.map((f) => `[${f.note}-${f.id}]/proxy/manifest/${this.videoId}/${f.id}.mpd`).join(','),
        title: this.info.fulltitle,
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
      // eslint-disable-next-line
      const [_, formatId] = event.info.split('-');
      const format = this.info.formats.find((f) => f.id === formatId);
      this.selectedFormat = format ?? null;
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
      return this.selectedFormat
        ? this.selectedFormat.filesize
        : null;
    },
  },
  mounted() {
    this.videoId = this.$route.query.v;
    this.fetchVideo();
  },
  beforeUnmount() {
    this.$refs.playerElement?.removeEventListener(
      'quality',
      this.handleQualityChange,
    );
  },
};
</script>
<style lang="scss" scoped>
.watch {
  padding: 10px 20px;
  &_player{
    display: flex;
    align-items: flex-start;
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
}
</style>
