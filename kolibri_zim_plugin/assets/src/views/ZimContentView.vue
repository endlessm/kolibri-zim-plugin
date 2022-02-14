<template>

  <div class="main">
    <template v-for="(articleContext, articleId) in articleContextById">
      <DOMTreeRenderer
        :key="articleId"
        :ref="`DOMTreeRenderer:${articleId}`"
        :class="{ 'zim-content': true, 'zim-content-hidden': currentArticleId !== articleId }"
        :document="articleContext.document"
        :location="articleContext.location"
        :openExternalLinksInNewWindow="true"
        @loadFinished="onLoadFinished(articleId)"
        @linkClicked="onLinkClicked"
      />
    </template>
  </div>

</template>


<script>

  import urls from 'kolibri.urls';

  import isEqual from 'lodash/isEqual';
  import isNil from 'lodash/isNil';
  import omitBy from 'lodash/omitBy';
  import pick from 'lodash/pick';

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
        articleContextById: {},
        nextArticleId: null,
        nextArticleHash: null,
        currentArticleId: null,
      };
    },
    computed: {
      zimQueryParams() {
        return {
          zimPath: this.$route.query.zimPath,
          redirectFrom: this.$route.query.redirectFrom,
          zimHash: this.$route.query.zimHash,
        };
      },
      currentArticleContext() {
        return this.articleContextById[this.currentArticleId];
      },
      currentDomTreeRenderer() {
        const refsList = this.$refs[`DOMTreeRenderer:${this.currentArticleId}`] || [];
        return refsList[0];
      },
    },
    watch: {
      zimQueryParams: {
        handler: function({ zimPath, redirectFrom, zimHash }, oldValue) {
          if (!oldValue) {
            this.loadZimPath({ zimPath, redirectFrom, zimHash });
          } else if (zimPath === oldValue.zimPath) {
            this.scrollToZimHash(zimHash);
          } else if (redirectFrom !== oldValue.zimPath) {
            this.loadZimPath({ zimPath, redirectFrom, zimHash });
          }
        },
        immediate: true,
      },
      currentArticleContext: {
        handler: function(currentArticleContext) {
          if (!currentArticleContext) {
            return;
          }

          this.$emit('articleReady', {
            zimPath: currentArticleContext.zimPath,
            redirectFrom: currentArticleContext.redirectFrom,
            title: currentArticleContext.title,
          });
        },
      },
    },
    methods: {
      loadZimPath({ zimPath, redirectFrom, zimHash }) {
        const urlString = zimPath
          ? urls.zim_article(this.zimFilename, zimPath)
          : urls.zim_index(this.zimFilename);
        const requestUrl = new URL(urlString, window.location);
        if (!isNil(redirectFrom)) {
          requestUrl.searchParams.set('redirect_from', redirectFrom);
        }
        const articleId = zimPath;
        return this.pushArticleFromUrl(articleId, requestUrl, zimHash);
      },
      pushArticleFromUrl(articleId, requestUrl, zimHash) {
        this.$emit('articleLoading');

        return fetch(requestUrl)
          .then(response => {
            const contentType = response.headers.get('Content-Type') || '';
            // eslint-disable-next-line no-unused-vars
            const [mimeType, ..._] = contentType.split(';').map(item => item.trim());
            if (mimeType === 'text/html') {
              return Promise.all([new URL(response.url), response.text()]);
            } else {
              return Promise.reject(`Invalid response content type: ${contentType}`);
            }
          })
          .then(([responseUrl, html]) => {
            const parser = new DOMParser();
            const document = parser.parseFromString(html, 'text/html');
            const redirectFrom = responseUrl.searchParams.get('redirect_from');
            this.pushArticle(
              articleId,
              {
                zimPath: this.zimPathFromUrl(responseUrl),
                location: responseUrl,
                redirectFrom,
                document,
                title: document.title,
              },
              zimHash
            );
          })
          .catch(error => {
            console.warn(`Error fetching article: ${error}`);
          });
      },
      pushArticle(articleId, articleContext, zimHash) {
        const articleContextById = pick(this.articleContextById, [this.currentArticleId]);
        articleContextById[articleId] = articleContext;
        this.articleContextById = articleContextById;

        this.nextArticleId = articleId;
        this.nextArticleHash = zimHash;

        this.updateZimQuery(
          {
            zimPath: articleContext.zimPath,
            redirectFrom: articleContext.redirectFrom,
            zimHash,
          },
          true
        );
      },
      updateZimQuery({ zimPath, redirectFrom, zimHash }, replace = false) {
        let query = {};

        if (zimPath !== undefined) {
          query.zimPath = zimPath;
        } else {
          query.zimPath = this.$route.query.zimPath;
        }

        if (redirectFrom !== undefined) {
          query.redirectFrom = redirectFrom;
        } else if (zimPath !== this.$route.query.zimPath) {
          // Remove redirectFrom if the path changes
          query.redirectFrom = undefined;
        } else {
          query.redirectFrom = this.$route.query.redirectFrom;
        }

        if (zimHash !== undefined) {
          query.zimHash = zimHash;
        } else {
          query.zimHash = this.$route.query.zimHash;
        }

        query = omitBy(query, isNil);

        if (isEqual(query, this.$route.query)) {
          return;
        }

        if (replace) {
          this.$router.replace({ query });
        } else {
          this.$router.push({ query });
        }
      },
      scrollToZimHash(zimHash) {
        if (!this.currentDomTreeRenderer) {
          return;
        }
        this.currentDomTreeRenderer.scrollTo(zimHash);
      },
      onLoadFinished(articleId) {
        if (this.nextArticleId !== articleId) {
          return;
        }

        this.currentArticleId = articleId;
        this.nextArticleId = null;

        if (this.nextArticleHash) {
          this.scrollToZimHash(this.nextArticleHash);
          this.nextArticleHash = null;
        }
      },
      onLinkClicked({ url, event }) {
        const zimPath = this.zimPathFromUrl(url);
        const zimHash = url.hash ? url.hash.substr(1) : undefined;

        if (!zimPath) {
          return;
        }

        event.preventDefault();

        this.updateZimQuery({ zimPath, zimHash });
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

  .main {
    position: relative;
  }

  .zim-content {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;
    display: block;
    width: 100%;
    height: 100%;
    overflow: auto;
    opacity: 1;
    transition: opacity 0.5s;
  }

  .zim-content-hidden {
    z-index: 1;
    opacity: 0;
  }

</style>
