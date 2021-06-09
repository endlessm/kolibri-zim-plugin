<template>

  <div class="zim-search">
    <ZimSearchForm
      ref="searchForm"
      @submit="onSearchFormSubmit"
      @reset="onSearchFormReset"
      @cancel="$emit('cancel')"
    />
    <div v-if="isSearchWaiting" class="zim-search-loader">
      <KLinearLoader />
    </div>
  </div>

</template>


<script>

  import urls from 'kolibri.urls';

  import ZimSearchResource from '../api-resources/zimSearchResource';
  import ZimSearchForm from './ZimSearchForm';

  export default {
    name: 'ZimSearchView',
    components: {
      ZimSearchForm,
    },
    props: {
      zimFilename: {
        type: String,
      },
    },
    data() {
      return {
        isSearchWaiting: 0,
        searchResults: {},
      };
    },
    computed: {},
    methods: {
      /**
       * @public
       */
      focus() {
        this.$refs.searchForm.focus();
      },
      onSearchFormSubmit(query) {
        this.startSearch(query);
      },
      onSearchFormReset() {
        this.searchResults = {};
      },
      startSearch(query) {
        this.isSearchWaiting += 1;

        const max_results = 100;

        ZimSearchResource.search(this.zimFilename, { query, max_results })
          .then(result => {
            const { articles, count } = result.data;
            this.searchResults = { query, articles, count, success: true };
          })
          .catch(error => {
            this.searchResults = { query, error };
          })
          .finally(() => {
            this.isSearchWaiting -= 1;
          });
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
