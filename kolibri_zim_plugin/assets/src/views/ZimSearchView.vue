<template>
  <div class="zim-search">
    <ZimSearchForm ref="searchForm" />
  </div>
</template>


<script>

  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import urls from 'kolibri.urls';

  import ZimSearchForm from './ZimSearchForm';

  export default {
    name: 'ZimRendererIndex',
    components: {
      ZimSearchForm,
    },
    props: {
      zimFilename: {
        type: String,
      },
    },
    data() {
      return {};
    },
    computed: {
      searchText() {
        return this.$tr('search');
      },
    },
    methods: {
      /**
       * @public
       */
      focus() {
        this.$refs.searchForm.focus();
      },
      articleUrl(path) {
        return urls.zim_article(this.zimFilename, path);
      },
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  .zim-search {
    width: 100%;
    height: 100%;
    overflow: auto;
    padding: 16px;
  }

</style>
