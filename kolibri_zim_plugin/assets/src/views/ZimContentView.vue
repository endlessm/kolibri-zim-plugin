<template>

  <iframe
    ref="iframe"
    class="iframe"
    sandbox="allow-scripts allow-same-origin"
    frameBorder="0"
    :style="{ backgroundColor: this.$themePalette.white }"
    :src="indexUrl"
    @load="onIframeLoad"
  ></iframe>

</template>


<script>

  import urls from 'kolibri.urls';

  export default {
    name: 'ZimContentView',
    components: {},
    props: {
      zimFilename: {
        type: String,
      },
    },
    computed: {
      indexUrl() {
        return urls.zim_index(this.zimFilename);
      },
    },
    methods: {
      /**
       * @public
       */
      navigateToUrl(url) {
        this.$refs.iframe.contentWindow.location = url;
      },
      /**
       * @public
       */
      navigateToArticle(path) {
        this.$refs.iframe.contentWindow.location = this.articleUrl(path);
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

        let href, title, isLoading, isExternal;
        const contentDocument = this.$refs.iframe.contentDocument;
        const contentWindow = this.$refs.iframe.contentWindow;

        try {
          href = contentWindow.location.href;
        } catch (DOMException) {
          href = undefined;
        }

        if (contentDocument && contentDocument.readyState == 'loading') {
          title = '…';
          isLoading = true;
        } else if (contentDocument) {
          title = contentDocument.title;
        } else {
          title = '…';
          isExternal = true;
        }

        this.$emit('onnavigate', { href, title, isLoading, isExternal });
      },
      articleUrl(path) {
        return urls.zim_article(this.zimFilename, path);
      },
    },
    $trs: {},
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  .iframe {
    width: 100%;
    height: 100%;
  }

</style>
