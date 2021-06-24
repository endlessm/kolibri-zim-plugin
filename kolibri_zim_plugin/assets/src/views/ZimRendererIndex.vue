<template>

  <CoreFullscreen
    ref="zimRenderer"
    class="zim-renderer"
    :style="{ height: contentRendererHeight, width: iframeWidth }"
    @changeFullscreen="isInFullscreen = $event"
  >
    <div
      ref="fullscreenHeader"
      class="fullscreen-header"
      :style="{ backgroundColor: this.$themePalette.grey.v_100 }"
    >
      <nav class="zim-actions">
        <KButton
          class="search-button"
          :primary="false"
          appearance="flat-button"
          aria-controls="zim-container"
          :text="searchText"
          :style="navSearchButtonStyle"
          icon="search"
          @click="onNavSearchClick"
        />
        <KButton
          class="random-article-button"
          :primary="false"
          appearance="flat-button"
          :title="randomArticleText"
          @click="onNavRandomArticleClickDebounced"
        >
          <ShuffleIcon slot="icon" />
        </KButton>
        <ZimBreadcrumbsMenu
          :breadcrumbs="breadcrumbs"
          :currentUrl="isSearching ? undefined : currentUrl"
          @activate="onNavBreadcrumbActivate"
        />
      </nav>

      <KButton
        class="fullscreen-button"
        :primary="false"
        appearance="flat-button"
        :icon="isInFullscreen ? 'fullscreen_exit' : 'fullscreen'"
        @click="$refs.zimRenderer.toggleFullscreen()"
      >
        {{ fullscreenText }}
      </KButton>
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
        :zimFilename="zimFilename"
        @onnavigate="onZimContentViewNavigate"
      />
    </div>
  </CoreFullscreen>

</template>


<script>

  import urls from 'kolibri.urls';
  import CoreFullscreen from 'kolibri.coreVue.components.CoreFullscreen';

  import debounce from 'lodash/debounce';

  import ZimBreadcrumbsMenu from './ZimBreadcrumbsMenu';
  import ZimContentView from './ZimContentView';
  import ZimSearchView from './ZimSearchView';
  import ShuffleIcon from './ShuffleIcon';

  const defaultContentHeight = '500px';
  const defaultFullscreenHeaderHeight = '37px';
  const pxStringAdd = (x, y) => parseInt(x, 10) + parseInt(y, 10) + 'px';

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
        currentUrl: undefined,
        zimNavigationHistory: new Array(),
        fullscreenHeaderHeight: defaultFullscreenHeaderHeight,
        resizeObserver: null,
      };
    },
    computed: {
      zimFilename() {
        return `${this.defaultFile.checksum}.${this.defaultFile.extension}`;
      },
      iframeHeight() {
        return (this.options && this.options.height) || defaultContentHeight;
      },
      iframeWidth() {
        return (this.options && this.options.width) || 'auto';
      },
      contentRendererHeight() {
        return pxStringAdd(this.iframeHeight, this.fullscreenHeaderHeight);
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
          return { height: this.iframeHeight };
        }
      },
      breadcrumbs() {
        if (this.zimNavigationHistory.length === 0) {
          const homeBreadcrumb = {
            title: this.$tr('homeBreadcrumb'),
            href: this.indexUrl,
          };
          return [homeBreadcrumb];
        } else {
          return this.zimNavigationHistory.slice();
        }
      },
      onNavRandomArticleClickDebounced() {
        return debounce(this.onNavRandomArticleClick, 500, { leading: true });
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
        const random_article_url = urls.zim_random_article(this.zimFilename);
        this.$refs.zimContentView.navigateToUrl(random_article_url);
      },
      onNavBreadcrumbActivate(breadcrumb) {
        this.isSearching = false;
        if (breadcrumb.href) {
          this.$refs.zimContentView.navigateToUrl(breadcrumb.href);
        }
      },
      onZimSearchViewActivate({ path }) {
        this.isSearching = false;
        // Assume that the first item in zimNavigationHistory is the home
        // article, which we want to keep, and remove everything else.
        this.zimNavigationHistory.splice(1);
        this.$refs.zimContentView.navigateToArticle(path);
      },
      onZimSearchViewCancel() {
        this.isSearching = false;
      },
      onZimSearchOverlayClick(event) {
        if (event.target === this.$refs.zimSearchOverlay) {
          this.isSearching = false;
        }
      },
      onZimContentViewNavigate({ href, title }) {
        this.currentUrl = href;

        const existingIndex = this.zimNavigationHistory.findIndex(
          breadcrumb => breadcrumb.href === href
        );

        if (existingIndex >= 0) {
          this.zimNavigationHistory.splice(existingIndex);
        }

        if (this.zimNavigationHistory.length == 0) {
          // We always assume the first breadcrumb is the home page. It has a
          // special title because the page title for the English Wikipedia
          // Zim file's index page is "User:The_other_Kiwix_guy/Landing".
          title = this.$tr('homeBreadcrumb');
        }

        this.zimNavigationHistory.push({ title, href });
      },
    },
    $trs: {
      enterFullscreen: 'View Fullscreen',
      exitFullscreen: 'Exit Fullscreen',
      homeBreadcrumb: 'Home',
      randomArticle: 'Random Article',
      search: 'Search',
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';
  @import '~kolibri-design-system/lib/keen/styles/md-colors';

  .zim-renderer {
    position: relative;
    background: #ffffff;
  }

  .fullscreen-header {
    text-align: right;
  }

  /deep/ .fullscreen-header .button {
    border-radius: 0;
  }

  .zim-actions {
    display: block;
    float: left;

    .button {
      text-transform: none;
    }

    .random-article-button {
      min-width: 36px;
      padding: 0 8px;
    }
  }

  .main-container {
    @extend %momentum-scroll;

    position: relative;
    width: 100%;
    padding-top: 0.25rem;
    overflow: hidden;
    background-color: #ffffff;
  }

  .zim-search-overlay {
    position: absolute;
    top: 0;
    left: 0;
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

</style>
