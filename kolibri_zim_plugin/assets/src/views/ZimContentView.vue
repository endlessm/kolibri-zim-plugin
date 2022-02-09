<template>

  <DOMTreeRenderer
    ref="domTreeRenderer"
    :document="document"
    :location="location"
    :openExternalLinksInNewWindow="true"
    :class="[ 'content', documentReady === false ? 'content--loading' : null ]"
    @loadStarted="onLoadStarted"
    @loadFinished="onLoadFinished"
    @linkClicked="onLinkClicked"
  />

</template>


<script>

  import urls from 'kolibri.urls';

  import DOMTreeRenderer from './DOMTreeRenderer';

  export default {
    name: 'ZimContentView',
    components: {
      DOMTreeRenderer,
    },
    props: {
      zimFilename: {
        type: String,
      },
    },
    data() {
      return {
        document: null,
        location: null,
        documentReady: false,
      };
    },
    computed: {
      zimPathAndZimHash() {
        return [
          this.$route.query.zimPath,
          this.$route.query.zimHash,
          this.$route.query.redirectFrom,
        ];
      },
    },
    watch: {
      zimPathAndZimHash: {
        handler: function([zimPath, zimHash, redirectFrom], oldValue) {
          if (!oldValue) {
            this.loadZimPath(zimPath, zimHash);
          } else {
            const oldZimPath = oldValue[0];
            if (zimPath === oldZimPath || redirectFrom === oldZimPath) {
              this.scrollToZimHash(zimHash);
            } else {
              this.loadZimPath(zimPath, zimHash);
            }
          }
        },
        immediate: true,
      },
    },
    methods: {
      loadZimPath(requestZimPath, zimHash) {
        const urlString = requestZimPath
          ? urls.zim_article(this.zimFilename, requestZimPath)
          : urls.zim_index(this.zimFilename);
        const requestUrl = new URL(urlString, window.location);

        return fetch(requestUrl)
          .then(response => {
            const responseUrl = new URL(response.url);
            const responseZimPath = this.zimPathFromUrl(responseUrl);

            if (responseZimPath != requestZimPath) {
              this.$router.replace({
                query: {
                  zimPath: responseZimPath,
                  zimHash: zimHash,
                  redirectFrom: responseUrl.searchParams.get('redirect_from'),
                },
              });
            }

            const articleContext = {
              url: responseUrl,
              zimPath: this.$route.query.zimPath,
              redirectFrom: this.$route.query.redirectFrom,
            };

            return Promise.all([response.ok, articleContext, response.text()]);
          })
          .then(([response_ok, articleContext, html]) => {
            return Promise.all([
              response_ok,
              articleContext,
              this.setDocumentFromHtml(html, articleContext.url),
            ]);
          })
          .then(([response_ok, articleContext, title]) => {
            if (!response_ok) {
              return;
            }
            this.scrollToZimHash(zimHash);
            this.$emit('articleReady', {
              ...articleContext,
              title,
            });
          });
      },
      scrollToZimHash(zimHash) {
        if (!this.$refs.domTreeRenderer) {
          return;
        }
        this.$refs.domTreeRenderer.scrollTo(zimHash);
      },
      setDocumentFromHtml(html, location) {
        const parser = new DOMParser();
        const document = parser.parseFromString(html, 'text/html');
        const title = document.title;
        this.document = document;
        this.location = location;
        return title;
      },
      onLoadStarted() {
        this.documentReady = false;
      },
      onLoadFinished() {
        this.documentReady = true;
      },
      onLinkClicked({ url, event }) {
        event.preventDefault();

        const zimPath = this.zimPathFromUrl(url);
        const zimHash = url.hash ? url.hash.substr(1) : '';

        if (zimPath) {
          event.preventDefault();
          if (zimPath != this.$route.query.zimPath || zimHash != this.$route.query.zimHash) {
            this.$router.push({ query: { zimPath, zimHash } });
          }
        }
      },
      zimPathFromUrl(url) {
        const fullPath = url.pathname;
        const basePath = urls.zim_article(this.zimFilename, '');

        if (fullPath.startsWith(basePath)) {
          return fullPath.substr(basePath.length);
        } else {
          return undefined;
        }
      },
    },
    $trs: {},
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  .content {
    display: block;
    width: 100%;
    height: 100%;
    overflow: auto;
    opacity: 1;
    transition: opacity 0.5s ease;
    // Set the transform property so fixed-position children are relative to
    // this element.
    transform: translate(0);
  }

  .content--loading {
    opacity: 0;
  }

</style>
