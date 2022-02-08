<template>

  <div
    ref="content"
    class="content"
  ></div>

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
    data() {
      return {
        shadow: null,
      };
    },
    computed: {
      zimPath() {
        return this.$route.query.zimPath || '';
      },
    },
    watch: {
      '$route.query.zimPath': {
        handler: function(zimPath) {
          this.loadArticle(zimPath);
        },
        immediate: true,
      },
    },
    mounted() {
      this.shadow = this.$refs.content.attachShadow({ mode: 'closed' });
      this.shadow.addEventListener('click', this.onShadowClick, { capture: true });
      this.loadArticle(this.zimPath);
    },
    methods: {
      /**
       * @public
       */
      navigateToUrl(url) {
        const articlePath = this.zimPathFromUrl(new URL(url));
        if (articlePath) {
          this.navigateToArticle(articlePath);
        }
      },
      /**
       * @public
       */
      navigateToArticle(path) {
        this.loadArticle(path);
      },
      setContent(html, baseUrl) {
        const parser = new DOMParser();
        const document = parser.parseFromString(html, 'text/html');
        const title = document.title;
        // We can't set the base URI with shadow dom, so we will need to
        // rewrite relative URLs...
        document.getElementsByTagName('*').forEach(elem => {
          if (elem.hasAttribute('href')) {
            const href = elem.getAttribute('href');
            const remapUrl = new URL(href, baseUrl);
            elem.setAttribute('href', remapUrl);

            const zimPath = this.zimPathFromUrl(remapUrl);

            if (zimPath) {
              elem.setAttribute('data-kolibri-zim-path', zimPath);
              elem.setAttribute('data-kolibri-zim-hash', remapUrl.hash);
            }

            if (remapUrl.host !== baseUrl.host) {
              elem.setAttribute('target', '_blank');
            }
          } else if (elem.hasAttribute('src')) {
            const src = elem.getAttribute('src');
            const remapUrl = new URL(src, baseUrl);
            elem.setAttribute('src', remapUrl);
          }
        });
        // TODO: Wait for external resources to load, first, to prevent flash
        //       of unstyled content.
        this.shadow.replaceChildren(document.documentElement);
        return title;
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
      onShadowClick(event) {
        const clickElem = this.shadow.elementFromPoint(event.clientX, event.clientY);
        const linkElem = clickElem ? clickElem.closest('a') : undefined;

        if (!linkElem) {
          return;
        }

        const zimPath = linkElem.dataset.kolibriZimPath;
        const zimHash = linkElem.dataset.kolibriZimHash;

        if (zimPath == this.zimPath && zimHash) {
          // TODO: It would be nice if we put this hash in the URL somewhere
          //       so the user can navigate back easily.
          event.preventDefault();
          const targetElem = this.shadow.getElementById(zimHash.slice(1));
          targetElem.scrollIntoView();
        } else if (zimPath == this.zimPath) {
          event.preventDefault();
        } else if (zimPath) {
          event.preventDefault();
          this.$router.push({ query: { zimPath } });
        }
      },
      loadArticle(path) {
        const url = path
          ? urls.zim_article(this.zimFilename, path)
          : urls.zim_index(this.zimFilename);

        return fetch(url)
          .then(response => {
            return Promise.all([response.ok, response.text(), new URL(response.url)]);
          })
          .then(([response_ok, html, baseUrl]) => {
            return Promise.all([response_ok, baseUrl, this.setContent(html, baseUrl)]);
          })
          .then(([response_ok, baseUrl, title]) => {
            if (response_ok) {
              const redirectFrom = baseUrl.searchParams.get('redirect_from');
              this.$emit('onnavigate', { path, redirectFrom, title });
            }
          });
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
    // Set the transform property so fixed-position children are relative to
    // this element.
    transform: translate(0);
  }

</style>
