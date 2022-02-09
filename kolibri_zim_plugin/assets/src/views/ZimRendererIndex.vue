<template>

  <CoreFullscreen
    ref="zimRenderer"
    class="zim-renderer"
    :style="{ width: iframeWidth }"
    @changeFullscreen="isInFullscreen = $event"
  >
    <div
      ref="fullscreenHeader"
      class="fullscreen-header"
      :style="{
        backgroundColor: this.$themePalette.grey.v_100,
        color: this.$themeTokens.text
      }"
    >
      <nav class="zim-actions">
        <KButton
          class="zim-search-button"
          :primary="false"
          appearance="flat-button"
          aria-controls="zim-container"
          :text="searchText"
          :style="navSearchButtonStyle"
          icon="search"
          @click="onNavSearchClick"
        />
        <KButton
          class="zim-random-article-button"
          :primary="false"
          appearance="flat-button"
          :title="randomArticleText"
          @click="onNavRandomArticleClickDebounced"
        >
          <ShuffleIcon slot="icon" />
        </KButton>
        <ZimBreadcrumbsMenu
          :currentPathIsEnabled="isSearching"
          @activate="onNavBreadcrumbActivate"
        />
      </nav>

      <KButton
        class="fullscreen-button"
        :primary="false"
        appearance="flat-button"
        :icon="isInFullscreen ? 'fullscreen_exit' : 'fullscreen'"
        :text="fullscreenText"
        @click="$refs.zimRenderer.toggleFullscreen()"
      />
    </div>
    <div class="main-container" :style="mainContainerStyle">
      <div
        ref="zimSearchOverlay"
        class="zim-search-overlay"
        :hidden="!isSearching"
        @click="onZimSearchOverlayClick($event)"
      >
        <ZimSearchView
          ref="zimSearchView"
          :zimFilename="zimFilename"
          @activate="onZimSearchViewActivate"
          @cancel="onZimSearchViewCancel"
        />
      </div>
      <ZimContentView
        ref="zimContentView"
        class="zim-content-view"
        :zimFilename="zimFilename"
        @articleReady="onZimContentViewArticleReady"
      />
    </div>
  </CoreFullscreen>

</template>


<script>

  import urls from 'kolibri.urls';
  import { mapActions } from 'vuex';
  import CoreFullscreen from 'kolibri.coreVue.components.CoreFullscreen';

  import debounce from 'lodash/debounce';

  import ZimBreadcrumbsMenu from './ZimBreadcrumbsMenu';
  import ZimContentView from './ZimContentView';
  import ZimSearchView from './ZimSearchView';
  import ShuffleIcon from './ShuffleIcon';

  const defaultFullscreenHeaderHeight = '37px';

  export default {
    name: 'ZimRendererIndex',
    components: {
      CoreFullscreen,
      ZimSearchView,
      ZimContentView,
      ZimBreadcrumbsMenu,
      ShuffleIcon,
    },
    data() {
      return {
        isInFullscreen: false,
        isSearching: false,
        fullscreenHeaderHeight: defaultFullscreenHeaderHeight,
        resizeObserver: null,
      };
    },
    computed: {
      zimFilename() {
        const defaultFile = this.defaultFile;
        return `${defaultFile.checksum}.${defaultFile.extension}`;
      },
      iframeWidth() {
        return (this.options && this.options.width) || 'auto';
      },
      fullscreenText() {
        return this.isInFullscreen ? this.$tr('exitFullscreen') : this.$tr('enterFullscreen');
      },
      searchText() {
        return this.$tr('search');
      },
      randomArticleText() {
        return this.$tr('randomArticle');
      },
      navSearchButtonStyle() {
        if (this.isSearching) {
          return { backgroundColor: this.$themePalette.grey.v_300 };
        } else {
          return { backgroundColor: this.$themePalette.grey.v_200 };
        }
      },
      mainContainerStyle() {
        if (this.isInFullscreen) {
          return {
            position: 'absolute',
            top: this.fullscreenHeaderHeight,
            bottom: 0,
          };
        } else {
          return {};
        }
      },
      onNavRandomArticleClickDebounced() {
        return debounce(this.onNavRandomArticleClick, 500, { leading: true });
      },

      /* eslint-disable kolibri/vue-no-unused-properties */
      // Note: the default duration historically for HTML5 Apps has been 5 min,
      // so we can use the same for zim files
      // Based on:
      // https://github.com/learningequality/kolibri/blob/release-v0.15.x/kolibri/plugins/html5_viewer/assets/src/views/Html5AppRendererIndex.vue#L124-L126
      defaultDuration() {
        return 300;
      },
    },
    mounted() {
      this.initResizeObserver();
      this.$emit('startTracking');
      this.pollProgress();
    },
    beforeDestroy() {
      this.destroyResizeObserver();
      if (this.timeout) {
        clearTimeout(this.timeout);
      }
      this.$emit('stopTracking');
    },
    methods: {
      ...mapActions('zim', ['pushNavigationHistory', 'resetNavigationHistory']),
      initResizeObserver() {
        // It would be nice to polyfill ResizeObserver, but the default case
        // should work reasonably well in most situations.
        this.resizeObserver = new ResizeObserver(this.onFullscreenHeaderResize);
        this.resizeObserver.observe(this.$refs.fullscreenHeader);
        this.onFullscreenHeaderResize();
      },
      destroyResizeObserver() {
        if (this.resizeObserver) this.resizeObserver.disconnect();
      },
      onFullscreenHeaderResize() {
        this.fullscreenHeaderHeight = this.$refs.fullscreenHeader.offsetHeight + 'px';
      },
      recordProgress() {
        this.$emit('updateProgress', this.durationBasedProgress);
        this.pollProgress();
      },
      pollProgress() {
        this.timeout = setTimeout(() => {
          this.recordProgress();
        }, 15000);
      },
      onNavSearchClick() {
        this.isSearching = true;
        this.$nextTick(() => {
          this.$refs.zimSearchView.focus();
        });
      },
      onNavRandomArticleClick() {
        this.isSearching = false;
        const random_article_url = urls.zim_random_article(this.zimFilename);
        // FIXME: Instead, use the random article API to get an zim path, then
        //        this.$router.push({ query: { zimPath } });
        this.$refs.zimContentView.navigateToUrl(random_article_url);
      },
      onNavBreadcrumbActivate(breadcrumb) {
        this.isSearching = false;
        this.$router.push({ query: { zimPath: breadcrumb.path } });
      },
      onZimSearchViewActivate({ path }) {
        this.isSearching = false;
        this.resetNavigationHistory();
        this.$router.push({ query: { zimPath: path } });
      },
      onZimSearchViewCancel() {
        this.isSearching = false;
      },
      onZimSearchOverlayClick(event) {
        if (event.target === this.$refs.zimSearchOverlay) {
          this.isSearching = false;
        }
      },
      onZimContentViewArticleReady({ zimPath, redirectFrom, title }) {
        this.pushNavigationHistory({ path: zimPath, redirectFrom, title });
      },
    },
    $trs: {
      enterFullscreen: 'View Fullscreen',
      exitFullscreen: 'Exit Fullscreen',
      randomArticle: 'Random Article',
      search: 'Search',
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';
  @import '~kolibri-design-system/lib/keen/styles/md-colors';
  $ui-toolbar-height: 56px;

  .zim-renderer {
    position: relative;
    display: flex;
    flex-direction: column;
    height: calc(100vh - #{$ui-toolbar-height});
    background: #ffffff;

    .fullscreen-header {
      flex-grow: 0;
      flex-shrink: 0;
    }

    .main-container {
      flex-grow: 1;
    }
  }

  .fullscreen-header {
    text-align: right;
  }

  /deep/ .fullscreen-header .button {
    border-radius: 0;

    .prop-icon + .link-text {
      margin-left: 0.25em;
    }
  }

  /deep/ .fullscreen-button .prop-icon {
    // From .fs-icon rule in Html5AppRendererIndex
    position: relative;
    top: 8px;
    width: 24px;
    height: 24px;
  }

  .zim-actions {
    display: block;
    float: left;

    .button {
      text-transform: none;
    }

    .zim-random-article-button {
      min-width: 36px;
      padding: 0 8px;
    }
  }

  .main-container {
    @extend %momentum-scroll;

    position: relative;
    width: 100%;
    overflow: hidden;
    background-color: #ffffff;
  }

  .zim-search-overlay {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.8);

    .zim-search {
      position: relative;
      width: 100%;
      max-height: 100%;
      overflow: auto;
      color: $md-grey-900;
      background-color: $md-grey-200;
      border-bottom: 2px solid $md-grey-400;
    }
  }

  .zim-content-view {
    z-index: 1;
    height: 100%;
  }

</style>
