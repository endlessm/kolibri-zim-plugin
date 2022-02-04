<template>

  <transition-group name="zim-breadcrumbs-fade" mode="out-in" tag="ol">
    <template v-for="(breadcrumb, index) in visibleBreadcrumbs">
      <li
        :ref="`breadcrumb${index}`"
        :key="index"
        class="zim-breadcrumb-item"
      >
        <KButton
          class="zim-breadcrumb-button"
          :primary="false"
          appearance="flat-button"
          :text="breadcrumbTitle(breadcrumb)"
          :title="breadcrumbTitle(breadcrumb)"
          :disabled="!breadcrumbIsEnabled(breadcrumb)"
          @click="$emit('activate', breadcrumb)"
        />
      </li>
    </template>
  </transition-group>

</template>


<script>

  import { mapState } from 'vuex';

  export default {
    name: 'ZimBreadcrumbsMenu',
    components: {},
    props: {
      currentPathIsEnabled: {
        type: Boolean,
      },
    },
    computed: {
      ...mapState('zim', ['navigationHistory']),
      currentPath() {
        return this.$route.query.zimPath || '';
      },
      breadcrumbs() {
        return this.navigationHistory.slice();
      },
      visibleBreadcrumbs() {
        return this.breadcrumbs.slice(-4);
      },
    },
    methods: {
      breadcrumbIsEnabled(breadcrumb) {
        if (breadcrumb.path === this.currentPath) {
          return this.currentPathIsEnabled;
        } else {
          return true;
        }
      },
      breadcrumbTitle(breadcrumb) {
        if (breadcrumb.path === '') {
          return this.$tr('homeBreadcrumb');
        } else {
          return breadcrumb.title;
        }
      },
    },
    $trs: {
      homeBreadcrumb: 'Home',
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  ol {
    display: inline-block;
    padding: 0;
    margin: 0;
    margin-left: 4px;
    list-style: none;
  }

  li {
    display: inline-block;
  }

  li::before {
    display: inline-block;
    padding: 0 4px;
    font-size: 1.2em;
    line-height: 1em;
    vertical-align: baseline;
    content: '\2039';
    opacity: 0.5;
  }

  li:first-child::before {
    display: none;
  }

  .zim-breadcrumb-button.button {
    max-width: 8rem;
    padding: 0 8px;
    text-overflow: ellipsis;
    text-transform: none;
  }

  .zim-breadcrumbs-fade-enter-active,
  .zim-breadcrumbs-fade-leave-active {
    transition: opacity 0.5s;
  }

  .zim-breadcrumbs-fade-enter,
  .zim-breadcrumbs-fade-leave-to {
    opacity: 0;
  }

</style>
