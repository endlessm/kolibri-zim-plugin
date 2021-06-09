<template>

  <form
    class="search-box"
    @submit.prevent="updateSearchQuery"
    @keydown.esc.prevent="handleEscKey"
  >
    <div
      class="search-box-row"
      :style="{
        backgroundColor: $themeTokens.surface,
        borderColor: $themePalette.grey.v_300,
        fontSize: '16px',
      }"
    >
      <label class="visuallyhidden" for="search-input">{{ coreString('searchLabel') }}</label>
      <input
        ref="searchInput"
        v-model.trim="searchInputValue"
        type="search"
        name="search-input"
        class="search-input"
        dir="auto"
        :placeholder="coreString('searchLabel')"
      >
      <div class="search-buttons-wrapper">
        <KIconButton
          icon="clear"
          :color="$themeTokens.text"
          size="small"
          class="search-clear-button"
          :class="searchInputValue === '' ? '' : 'search-clear-button-visible'"
          :ariaLabel="$tr('clearButtonLabel')"
          @click="handleClickClear"
        />
        <div
          class="search-submit-button-wrapper"
          :style="{ backgroundColor: $themeTokens.primaryDark }"
        >
          <KIconButton
            :icon="icon"
            color="white"
            class="search-submit-button"
            :disabled="searchBarDisabled"
            :class="{ 'rtl-icon': icon === 'forward' && isRtl }"
            :style="{ fill: $themeTokens.textInverted }"
            :ariaLabel="$tr('startSearchButtonLabel')"
            type="submit"
          />
        </div>
      </div>
    </div>
  </form>

</template>


<script>

  /*
   * From SearchBox.vue in Kolibri:
   * <https://github.com/learningequality/kolibri/blob/develop/kolibri/plugins/learn/assets/src/views/SearchBox.vue>
   * We need our own version because the upstream one modifies this.$router.
   */

  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';

  export default {
    name: 'ZimSearchForm',
    components: {},
    mixins: [commonCoreStrings],
    props: {
      icon: {
        type: String,
        default: 'search',
        validator(val) {
          return ['search', 'forward'].includes(val);
        },
      },
    },
    data() {
      return {
        searchInputValue: '', // TODO: !!!!!!!!!!
      };
    },
    computed: {
      searchBarDisabled() {
        // Disable the search bar if it has been cleared or has not been changed
        return this.searchInputValue === '' || this.searchInputValue === this.searchTerm;
      },
    },
    mounted() {},
    beforeDestroy() {},
    methods: {
      /**
       * @public
       */
      focus() {
        this.$refs.searchInput.focus();
      },
      clearInput() {
        this.searchInputValue = '';
      },
      handleEscKey() {
        if (this.searchInputValue === '') {
          this.$emit('closeDropdownSearchBox');
        } else {
          this.clearInput();
        }
      },
      handleClickClear() {
        this.clearInput();
        this.$refs.searchInput.focus();
      },
      updateSearchQuery() {
        // const query = {
        //   searchTerm: this.searchInputValue || this.$route.query.searchTerm,
        // };
        // if (this.filters) {
        //   query.kind = this.$refs.contentKindFilter.selection.value;
        //   query.channel_id = this.$refs.channelFilter.selection.value;
        // }
      },
    },
    $trs: {
      clearButtonLabel: 'Clear',
      startSearchButtonLabel: 'Start search',
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  .search-box {
    margin-right: 8px;
  }

  .search-box-within-action-bar {
    width: 235px;
  }

  .search-box-row {
    display: table;
    width: 100%;
    max-width: 450px;
    margin: 0 auto;
    overflow: hidden;
    border: solid 1px;
    border-radius: $radius;
  }

  .search-input {
    display: table-cell;
    width: 100%;
    height: 36px;
    padding: 0;
    padding-left: 8px;
    margin: 0;
    vertical-align: middle;
    border: 0;

    // removes the IE clear button
    &::-ms-clear {
      display: none;
    }
  }

  .search-buttons-wrapper {
    display: table-cell;
    width: 80px;
    height: 36px;
    text-align: right;
    vertical-align: middle;
  }

  .search-clear-button {
    width: 24px;
    height: 24px;
    margin-right: 6px;
    vertical-align: middle;
    visibility: hidden;
  }

  .search-clear-button-visible {
    visibility: visible;
  }

  .search-submit-button {
    width: 36px;
    height: 36px;
  }

  .search-submit-button-wrapper {
    display: inline-block;
    vertical-align: middle;
  }

</style>
