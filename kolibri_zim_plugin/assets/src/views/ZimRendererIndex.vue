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
        <ZimBreadcrumbsMenu
          :breadcrumbs="breadcrumbs"
          :currentUrl="isSearching ? undefined : currentUrl"
          @activate="onNavBreadcrumbClick"
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
    <div class="search" :style="searchStyle">
      <p>Search box and search results go here</p>
      <ZimSearchForm ref="searchForm" />
    </div>
    <div class="zim-content-container" :style="zimContentContainerStyle">
      <ZimContent
        ref="zimContent"
        :indexUrl="indexUrl"
        @onnavigate="onZimContentNavigate"
      />
    </div>
  </CoreFullscreen>

</template>


<script>

  import CoreFullscreen from 'kolibri.coreVue.components.CoreFullscreen';
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import urls from 'kolibri.urls';

  import ZimBreadcrumbsMenu from './ZimBreadcrumbsMenu';
  import ZimContent from './ZimContent';
  import ZimSearchForm from './ZimSearchForm';

  const defaultContentHeight = '500px';
  const defaultFullscreenHeaderHeight = '37px';
  const pxStringAdd = (x, y) => parseInt(x, 10) + parseInt(y, 10) + 'px';

  export default {
    name: 'ZimRendererIndex',
    components: {
      CoreFullscreen,
      ZimSearchForm,
      ZimContent,
      ZimBreadcrumbsMenu,
    },
    mixins: [commonCoreStrings],
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
      indexUrl() {
        const zim_filename = `${this.defaultFile.checksum}.${this.defaultFile.extension}`;
        return urls.zim_index(zim_filename);
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
      navSearchButtonStyle() {
        if (this.isSearching) {
          return { backgroundColor: this.$themePalette.grey.v_300 };
        } else {
          return { backgroundColor: this.$themePalette.grey.v_200 };
        }
      },
      searchStyle() {
        if (this.isSearching) {
          return { display: 'block' };
        } else {
          return { display: 'none' };
        }
      },
      zimContentContainerStyle() {
        if (this.isSearching) {
          return { display: 'none' };
        } else if (this.isInFullscreen) {
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
      onZimContentNavigate({ href, title }) {
        this.currentUrl = href;

        const existingIndex = this.zimNavigationHistory.findIndex(
          breadcrumb => breadcrumb.href === href
        );
        if (existingIndex >= 0) {
          this.zimNavigationHistory = this.zimNavigationHistory.slice(0, existingIndex);
        }

        if (this.zimNavigationHistory.length == 0) {
          // We always assume the first breadcrumb is the home page. It has a
          // special title because the page title for the English Wikipedia
          // Zim file's index page is "User:The_other_Kiwix_guy/Landing".
          title = this.$tr('homeBreadcrumb');
        }

        this.zimNavigationHistory.push({ title, href });
      },
      onNavSearchClick() {
        this.isSearching = true;
        setTimeout(() => {
          if (this.$refs.searchForm) this.$refs.searchForm.focus();
        }, 100);
      },
      onNavBreadcrumbClick(breadcrumb) {
        this.isSearching = false;
        if (breadcrumb.href) {
          this.$refs.zimContent.navigate(breadcrumb.href);
        }
      },
    },
    $trs: {
      enterFullscreen: 'View Fullscreen',
      exitFullscreen: 'Exit Fullscreen',
      homeBreadcrumb: 'Home',
      search: 'Search',
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  .fullscreen-header {
    text-align: right;
  }

  .zim-actions {
    display: block;
    float: left;

    .search-button {
      text-transform: none;
    }
  }

  .zim-renderer {
    position: relative;
    text-align: center;
    background: #ffffff;
  }

  .zim-content-container {
    @extend %momentum-scroll;

    width: 100%;
    padding-top: 0.25rem;
    overflow: visible;
    background-color: #ffffff;
  }

</style>
