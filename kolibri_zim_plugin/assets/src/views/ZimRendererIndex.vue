<template>

  <CoreFullscreen
    ref="zimRenderer"
    class="zim-renderer"
    :style="{ height: contentRendererHeight, width: iframeWidth }"
    @changeFullscreen="isInFullscreen = $event"
  >
    <div
      class="fullscreen-header"
      :style="{ backgroundColor: this.$themePalette.grey.v_100 }"
    >

      <nav class="breadcrumbs">
        <ol class="breadcrumbs-visible-items">
          <li
            class="breadcrumb-search-item"
            :style="{ backgroundColor: this.$themePalette.grey.v_200 }"
          >
            <KButton
              class="breadcrumb-button"
              :primary="false"
              appearance="flat-button"
              aria-controls="zim-container"
              :text="searchText"
              icon="search"
              @click="onNavSearchClick"
            />
          </li>
          <template v-for="(breadcrumb, index) in visibleZimBreadcrumbs">
            <li
              :ref="`breadcrumb${index}`"
              :key="index"
              class="breadcrumb-history-item"
            >
              <KButton
                class="breadcrumb-button"
                :primary="false"
                appearance="flat-button"
                :text="breadcrumb.title"
                :disabled="breadcrumb.href === undefined || breadcrumb.current"
                tabindex="-1"
                @click="onNavBreadcrumbClick(breadcrumb)"
              />
            </li>
          </template>
        </ol>
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
    <div class="iframe-container" :style="containerStyle">
      <iframe
        ref="iframe"
        class="iframe"
        sandbox="allow-scripts allow-same-origin"
        frameBorder="0"
        :style="{ backgroundColor: this.$themePalette.white }"
        :src="indexUrl"
        @load="onIframeLoad"
      >
      </iframe>
    </div>
  </CoreFullscreen>

</template>


<script>

  import CoreFullscreen from 'kolibri.coreVue.components.CoreFullscreen';
  import urls from 'kolibri.urls';

  const defaultContentHeight = '500px';
  const frameTopbarHeight = '37px';
  const pxStringAdd = (x, y) => parseInt(x, 10) + parseInt(y, 10) + 'px';
  export default {
    name: 'ZimRendererIndex',
    components: {
      CoreFullscreen,
    },
    data() {
      return {
        isInFullscreen: false,
        zimBreadcrumbs: new Array(),
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
        return pxStringAdd(this.iframeHeight, frameTopbarHeight);
      },
      fullscreenText() {
        return this.isInFullscreen ? this.$tr('exitFullscreen') : this.$tr('enterFullscreen');
      },
      searchText() {
        return this.$tr('search');
      },
      containerStyle() {
        if (this.isInFullscreen) {
          return {
            position: 'absolute',
            top: frameTopbarHeight,
            bottom: 0,
          };
        }
        return { height: this.iframeHeight };
      },
      visibleZimBreadcrumbs() {
        return this.zimBreadcrumbs.slice(-3);
      },
    },
    mounted() {
      this.$emit('startTracking');
      this.pollProgress();
    },
    beforeDestroy() {
      if (this.timeout) {
        clearTimeout(this.timeout);
      }
      this.$emit('stopTracking');
    },
    methods: {
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
        alert('TODO: Search');
      },
      onIframeLoad() {
        try {
          this.$refs.iframe.contentWindow.removeEventListener('unload', this.onIframeUnload);
          this.$refs.iframe.contentWindow.addEventListener('unload', this.onIframeUnload);
        } catch (DOMException) {
          // pass
        }
        this.onIframeLocationChanged();
      },
      onIframeUnload() {
        setTimeout(this.onIframeLocationChanged, 0);
      },
      onIframeLocationChanged() {
        // FIXME: Building the breadcrumb trail here involves reading from
        //        iframe.contentWindow.location, which is not possible with
        //        cross-origin iframes. This will need to be rewritten when
        //        the zim backend is moved to a different server.

        let href, title, loading, external;
        const contentDocument = this.$refs.iframe.contentDocument;
        const contentWindow = this.$refs.iframe.contentWindow;
        if (contentDocument && contentDocument.readyState == 'loading') {
          title = '…';
          loading = true;
        } else if (contentDocument) {
          title = contentDocument.title;
        } else {
          title = '…';
          external = true;
        }
        try {
          href = contentWindow.location.href;
        } catch (DOMException) {
          href = undefined;
        }
        const existingIndex = this.zimBreadcrumbs.findIndex(breadcrumb => breadcrumb.href === href);
        if (existingIndex >= 0) {
          this.zimBreadcrumbs = this.zimBreadcrumbs.slice(0, existingIndex);
        }
        this.zimBreadcrumbs.forEach(breadcrumb => (breadcrumb.current = false));
        this.zimBreadcrumbs.push({ title, href, loading, external, current: true });
      },
      onNavBreadcrumbClick(breadcrumb) {
        if (breadcrumb.href) {
          this.$refs.iframe.contentWindow.location = breadcrumb.href;
        }
      },
    },
    $trs: {
      exitFullscreen: 'Exit Fullscreen',
      enterFullscreen: 'View Fullscreen',
      search: 'Search',
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  .fullscreen-header {
    text-align: right;
  }

  .fs-icon {
    position: relative;
    top: 8px;
    width: 24px;
    height: 24px;
  }

  .zim-renderer {
    position: relative;
    text-align: center;
  }

  .iframe {
    width: 100%;
    height: 100%;
  }

  .iframe-container {
    @extend %momentum-scroll;

    width: 100%;
    overflow: visible;
  }

  .breadcrumbs {
    display: block;
    float: left;

    ol {
      display: inline-block;
      padding: 0;
      margin: 0;
      list-style: none;
    }

    li {
      display: inline-block;
      max-width: 10rem;
    }

    .breadcrumb-button {
      text-overflow: ellipsis;
      text-transform: none;
    }
  }

</style>
