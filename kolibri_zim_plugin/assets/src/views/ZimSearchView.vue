<template>

  <div class="zim-search">
    <ZimSearchForm
      ref="searchForm"
      @input="onSearchFormInput"
      @submit="onSearchFormSubmit"
      @reset="onSearchFormReset"
      @cancel="$emit('cancel')"
    />
    <div v-if="isSearchWaiting > 0" class="zim-search-loader">
      <KLinearLoader />
    </div>
    <template v-if="suggestResults.success && suggestResults.articles.length > 0">
      <ol class="zim-suggest-results-list">
        <template v-for="(article, index) in suggestResults.articles">
          <li
            :ref="`article${index}`"
            :key="index"
            class="zim-suggest-result-item"
          >
            <KButton
              appearance="flat-button"
              class="zim-suggest-result-button"
              :appearanceOverrides="{
                color: $themeTokens.link,
                ':hover': { color: $themeTokens.linkDark },
              }"
              :text="article.title"
              :title="article.title"
              :href="articleUrl(article.path)"
              @click.prevent="$emit('activate', article)"
            />
          </li>
        </template>
      </ol>
    </template>
    <template v-if="searchResults.error">
      <h2>There was an error searching for '{{ searchResults.query }}'</h2>
      <TechnicalTextBlock :text="String(searchResults.error)" />
    </template>
    <template v-else-if="searchResults.success && searchResults.count > 0">
      <h2>
        {{ $tr(
          'searchResultsMsg', {
            query: searchResults.query,
            count: $formatNumber(searchResults.articles.length)
          }
        ) }}
      </h2>
      <ol class="zim-search-results-list">
        <template v-for="(article, index) in searchResults.articles">
          <li
            :ref="`article${index}`"
            :key="index"
            class="zim-search-result-item"
          >
            <KButton
              appearance="basic-link"
              :text="article.title"
              :href="articleUrl(article.path)"
              @click.prevent="$emit('activate', article)"
            />
            <small v-if="article.redirect_from">
              {{ $tr(
                'redirectedFromMsg', {
                  title: article.redirect_from
                }
              ) }}
            </small>
            <p v-if="article.snippet">
              {{ article.snippet }}&nbsp;&hellip;
            </p>
          </li>
        </template>
      </ol>
      <template v-if="searchHasMore">
        <div class="zim-search-footer">
          <p>
            {{ $tr(
              'moreResultsMsg', {
                count: $formatNumber(remainingResults)
              }
            ) }}
          </p>
          <div class="zim-search-more">
            <KButton
              appearance="raised-button"
              primary="true"
              :disabled="isSearchWaiting > 0 || isSearchMoreWaiting > 0"
              :text="$tr('loadMoreButtonLabel')"
              @click.prevent="onSearchMoreClick"
            />
            <KCircularLoader v-if="isSearchMoreWaiting > 0" />
          </div>
        </div>
      </template>
    </template>
    <template v-else-if="searchResults.success && searchResults.count === 0">
      <h2>{{ $tr('noSearchResultsMsg', { query: searchResults.query }) }}</h2>
    </template>
  </div>

</template>


<script>

  import urls from 'kolibri.urls';
  import TechnicalTextBlock from 'kolibri.coreVue.components.TechnicalTextBlock';

  import debounce from 'lodash/debounce';

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
        isSearchMoreWaiting: 0,
        isSearchWaiting: 0,
        searchResults: {},
        suggestResults: {},
      };
    },
    computed: {
      searchHasMore() {
        return this.searchResults.next;
      },
      remainingResults() {
        if (this.searchResults.next) {
          return this.searchResults.count - this.searchResults.next;
        } else {
          return 0;
        }
      },
      startSuggestDebounced() {
        return debounce(this.startSuggest, 500);
      },
    },
    beforeDestroy() {
      this.startSuggestDebounced.cancel();
    },
    methods: {
      /**
       * @public
       */
      focus() {
        this.$refs.searchForm.focus();
      },
      onSearchFormReset() {
        this.suggestResults = {};
        this.searchResults = {};
      },
      onSearchFormInput() {
        this.startSuggestDebounced();
      },
      onSearchFormSubmit(query) {
        this.isSearchWaiting += 1;
        this.startSearch(query).finally(() => {
          this.isSearchWaiting -= 1;
        });
      },
      onSearchMoreClick() {
        this.isSearchMoreWaiting += 1;
        this.startSearch(this.searchResults.query, this.searchResults.next).finally(() => {
          this.isSearchMoreWaiting -= 1;
        });
      },
      startSuggest() {
        const query = this.$refs.searchForm.getInput();

        if (query.length < 3) {
          this.suggestResults = {};
          return;
        }

        return ZimSearchResource.search(this.zimFilename, {
          query,
          max_results: 20,
          suggest: true,
        })
          .then(result => {
            if (this.$refs.searchForm.getInput() !== query) {
              return;
            }
            const { articles } = result.data;
            this.suggestResults = {
              query,
              articles: this.filterDuplicateArticles(articles, 5),
              success: true,
            };
          })
          .catch(() => {
            this.suggestResults = {};
          });
      },
      startSearch(query, start = 0) {
        const max_results = 10;
        const snippet_length = 140;

        return ZimSearchResource.search(this.zimFilename, {
          query,
          start,
          max_results,
          snippet_length,
        })
          .then(result => {
            const { articles, count } = result.data;
            const end = start + articles.length;
            const next = end < count ? end : null;

            if (query === this.searchResults.query && start === this.searchResults.next) {
              // Add to the existing results
              this.searchResults = {
                query,
                articles: this.searchResults.articles.concat(articles),
                count,
                next,
                success: true,
              };
            } else {
              this.searchResults = {
                query,
                articles,
                count,
                next,
                success: true,
              };
            }
          })
          .catch(error => {
            this.searchResults = { query, error };
          });
      },
      filterDuplicateArticles(articles, limit) {
        // The search suggestions API tends to return many articles which
        // redirect to the same place, for example with minor spelling
        // differences. We solve this by fetching a larger number of results
        // than we will display, and removing the duplicate results.
        const articlePaths = new Set();
        return articles.reduce((result, article) => {
          const path = article.redirect || article.path;
          if (!articlePaths.has(path) && result.length < limit) {
            articlePaths.add(path);
            return result.concat(article);
          } else {
            return result;
          }
        }, []);
      },
      articleUrl(path) {
        return urls.zim_article(this.zimFilename, path);
      },
    },
    $trs: {
      searchResultsMsg:
        "{count, plural, one {{count} result} other {Top {count} results}} for '{query}'",
      noSearchResultsMsg: "No results for '{query}'",
      moreResultsMsg: '{count, plural, one {{count} more result} other {{count} more results}}',
      redirectedFromMsg: 'Redirected from { title }',
      loadMoreButtonLabel: 'Load more',
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/buttons-and-links/buttons';
  @import '~kolibri-design-system/lib/keen/styles/md-colors';
  @import '~kolibri-design-system/lib/styles/definitions';

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

  h2 {
    margin: 1rem 0;
    font-size: 1.17rem;
    font-weight: 600;
  }

  ol.zim-suggest-results-list {
    display: block;
    padding: 0;
    margin: 0.5rem 0 0;
    text-align: center;
    list-style: none;

    li.zim-suggest-result-item {
      display: inline-block;
      max-width: 10rem;
      margin: 0.25rem;

      .zim-suggest-result-button {
        font-weight: normal;
        text-decoration: underline;
        text-overflow: ellipsis;
        text-transform: none;
        border-radius: $radius;
      }
    }
  }

  ol.zim-search-results-list {
    display: block;
    padding: 0;
    margin: 0;
    list-style: none;

    li.zim-search-result-item {
      display: block;
      padding-bottom: 1rem;
      margin: 1rem 0;
      border-bottom: 1px solid $md-grey-400;

      &:last-child {
        margin-bottom: 0;
        border-bottom-style: none;
      }
    }

    .link {
      display: block;
      font-weight: bold;
    }

    small {
      color: $md-grey-700;
    }

    p {
      margin: 0.5rem 0 0;
      font-size: 0.9375rem;
    }
  }

  .zim-search-footer {
    padding: 1rem 0;
    text-align: center;
    border-top: 1px solid $md-grey-600;

    p {
      margin-bottom: 0.5rem;
    }
  }

  .zim-search-more {
    .ui-progress-circular {
      position: absolute;
      display: inline-block;
      margin-left: 16px;
    }
  }

</style>
