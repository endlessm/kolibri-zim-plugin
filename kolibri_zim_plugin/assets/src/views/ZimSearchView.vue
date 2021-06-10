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
    <template v-if="searchResults.error">
      <h2>There was an error searching for '{{ searchResults.query }}'</h2>
      <TechnicalTextBlock :text="String(searchResults.error)" />
    </template>
    <template v-else-if="searchResults.success && searchResults.count > 0">
      <h2>
        {{ $tr(
          'searchResultsMsg', { query: searchResults.query, count: searchResults.articles.length }
        ) }}
      </h2>
      <ol class="search-results-list">
        <template v-for="(article, index) in searchResults.articles">
          <li
            :ref="`article${index}`"
            :key="index"
            class="search-result-item"
          >
            <KButton
              appearance="basic-link"
              :text="article.title"
              :href="articleUrl(article.path)"
              @click.prevent="$emit('activate', article)"
            />
          </li>
        </template>
      </ol>
    </template>
    <template v-else-if="searchResults.success && searchResults.count === 0">
      <h2>{{ $tr('noSearchResultsMsg', { query: searchResults.query }) }}</h2>
    </template>
  </div>

</template>


<script>

  import urls from 'kolibri.urls';
  import TechnicalTextBlock from 'kolibri.coreVue.components.TechnicalTextBlock';

  import ZimSearchResource from '../api-resources/zimSearchResource';
  import ZimSearchForm from './ZimSearchForm';

  export default {
    name: 'ZimSearchView',
    components: {
      ZimSearchForm,
      TechnicalTextBlock,
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
    $trs: {
      searchResultsMsg:
        "{count, plural, one {{count} result} other {Top {count} results}} for '{query}'",
      noSearchResultsMsg: "No results for '{query}'",
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';
  @import '~kolibri-design-system/lib/buttons-and-links/buttons';

  .zim-search {
    padding: 16px;
  }

  .zim-search-loader {
    position: absolute;
    right: 0;
    left: 0;

    .ui-progress-linear {
      position: relative;
      max-width: 450px;
      margin: 0 auto;
    }
  }

  ol {
    display: block;
    padding: 0;
    margin: 0;
    list-style: none;
  }

  li {
    display: block;
    margin: 0.5rem 0;

    &::before {
      display: inline-block;
      margin: 0 6px 0 2px;
      content: '\203A';
    }
  }

</style>
