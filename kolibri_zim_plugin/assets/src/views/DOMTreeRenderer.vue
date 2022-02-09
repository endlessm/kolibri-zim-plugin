<template>

  <div ref="content" class="content"></div>

</template>


<script>

  export default {
    name: 'DOMTreeRenderer',
    components: {},
    props: {
      document: {
        type: Element,
      },
      location: {
        type: URL,
      },
      openExternalLinksInNewWindow: {
        type: Boolean,
      },
    },
    data() {
      return {
        shadow: null,
        resourcesToLoad: undefined,
        resourcesLoaded: undefined,
      };
    },
    computed: {
      documentAndLocation() {
        return [this.document, this.location];
      },
    },
    watch: {
      documentAndLocation: {
        handler: function([document, location]) {
          if (!document || !location) {
            this.shadow.replaceChildren();
            return;
          }

          this.$emit('loadStarted');

          // We can't set the base URI with shadow dom, so we need to rewrite
          // relative URLs...
          document.getElementsByTagName('*').forEach(this.remapElementUrl);

          this.resourcesToLoad = 0;
          this.resourcesLoaded = 0;
          document.head.getElementsByTagName('link').forEach(elem => {
            if (elem.rel === 'stylesheet' && elem.hasAttribute('href')) {
              this.resourcesToLoad += 1;
              elem.addEventListener('load', this.onDocumentResourceLoad, { once: true });
              elem.addEventListener('error', this.onDocumentResourceLoad, { once: true });
            }
          });

          this.shadow.replaceChildren(document.documentElement);

          if (this.resourcesToLoad === 0 && this.resourcesLoaded === 0) {
            this.$emit('loadFinished');
          }
        },
      },
      resourcesLoaded: {
        handler: function(resourcesLoaded) {
          if (resourcesLoaded >= this.resourcesToLoad && this.document && this.location) {
            this.$emit('loadFinished');
          }
        },
      },
    },
    mounted() {
      this.shadow = this.$refs.content.attachShadow({ mode: 'closed' });
      this.shadow.addEventListener('click', this.onShadowClick, { capture: true });
    },
    methods: {
      /**
       * @public
       */
      scrollTo(id) {
        if (!id) {
          this.$refs.content.scrollTo(0, 0);
          return true;
        }
        const targetElem = this.shadow.getElementById(id);
        if (!targetElem) {
          return false;
        }
        targetElem.scrollIntoView();
        return true;
      },
      remapElementUrl(elem) {
        if (!this.location) {
          return;
        }

        if (elem.hasAttribute('href')) {
          const href = elem.getAttribute('href');
          const remapUrl = new URL(href, this.location);
          elem.setAttribute('href', remapUrl);
          if (
            elem.tagName === 'A' &&
            remapUrl.host !== this.location.host &&
            this.openExternalLinksInNewWindow
          ) {
            elem.setAttribute('target', '_blank');
          }
        } else if (elem.hasAttribute('src')) {
          const src = elem.getAttribute('src');
          const remapUrl = new URL(src, this.location);
          elem.setAttribute('src', remapUrl);
        }
      },
      onDocumentResourceLoad() {
        this.resourcesLoaded += 1;
      },
      onShadowClick(event) {
        const clickElem = this.shadow.elementFromPoint(event.clientX, event.clientY);
        const linkElem = clickElem ? clickElem.closest('a') : undefined;

        if (!linkElem) {
          return;
        }

        if (linkElem.hasAttribute('href') && linkElem.getAttribute('target') != '_blank') {
          const href = linkElem.getAttribute('href');
          const url = new URL(href);

          this.$emit('linkClicked', { url, event });
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
    // Set the transform property so fixed-position children are relative to
    // this element.
    transform: translate(0);
  }

  .load-content {
    display: none;
  }

</style>
