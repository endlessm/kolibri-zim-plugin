<template>

  <div ref="main" class="main"></div>

</template>


<script>

  export default {
    name: 'DOMTreeRenderer',
    components: {},
    props: {
      document: {
        type: Document,
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
        resourcesToLoad: null,
        resourcesLoaded: null,
      };
    },
    computed: {
      documentAndLocation() {
        return [this.document, this.location];
      },
    },
    watch: {
      documentAndLocation: {
        handler: function() {
          this.updateShadowChildren();
        },
      },
    },
    mounted() {
      this.shadow = this.$refs.main.attachShadow({ mode: 'closed' });
      this.shadow.addEventListener('click', this.onShadowClick, { capture: true });
      this.updateShadowChildren();
    },
    methods: {
      /**
       * @public
       */
      scrollTo(id) {
        if (!id) {
          this.$refs.main.scrollTo(0, 0);
          return true;
        }
        const targetElem = this.shadow.getElementById(id);
        if (!targetElem) {
          return false;
        }
        targetElem.scrollIntoView();
        return true;
      },
      updateShadowChildren() {
        if (!this.document || !this.location) {
          this.shadow.replaceChildren();
          return;
        }

        // We can't set the base URI with shadow dom, so we need to rewrite
        // relative URLs...
        this.document.getElementsByTagName('*').forEach(this.remapElementUrl);

        this.resourcesToLoad = 0;
        this.resourcesLoaded = 0;

        this.document.head.getElementsByTagName('link').forEach(elem => {
          if (elem.rel === 'stylesheet' && elem.hasAttribute('href')) {
            this.resourcesToLoad += 1;
            elem.addEventListener('load', this.onDocumentResourceLoad, { once: true });
            elem.addEventListener('error', this.onDocumentResourceLoad, { once: true });
          }
        });

        this.shadow.replaceChildren(this.document.documentElement);

        this.updateResourcesLoaded();
      },
      remapElementUrl(elem) {
        if (!this.location) {
          return;
        }

        let urlAttributeName = null;

        if (elem.hasAttribute('href')) {
          urlAttributeName = 'href';
        } else if (elem.hasAttribute('src')) {
          urlAttributeName = 'src';
        }

        if (!urlAttributeName) {
          return;
        }

        const remappedUrl = this.remapUrl(elem.getAttribute(urlAttributeName));

        if (!remappedUrl) {
          return;
        }

        elem.setAttribute(urlAttributeName, remappedUrl);

        if (
          elem.tagName === 'A' &&
          remappedUrl.host !== this.location.host &&
          this.openExternalLinksInNewWindow
        ) {
          elem.setAttribute('target', '_blank');
        }
      },
      remapUrl(url) {
        try {
          return new URL(url, this.location);
        } catch (error) {
          return null;
        }
      },
      onDocumentResourceLoad() {
        this.resourcesLoaded += 1;
        this.updateResourcesLoaded();
      },
      updateResourcesLoaded() {
        if (this.resourcesLoaded >= this.resourcesToLoad && this.document && this.location) {
          this.$emit('loadFinished', { url: this.location });
        }
      },
      onShadowClick(event) {
        const clickElem = this.shadow.elementFromPoint(event.clientX, event.clientY);
        const linkElem = clickElem ? clickElem.closest('a') : null;

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

  .main {
    // Set the transform property so fixed-position children are relative to
    // this element.
    transform: translate(0);
  }

</style>
