<template>

  <ol class="breadcrumbs-list">
    <template v-for="(breadcrumb, index) in visibleBreadcrumbs">
      <li
        :ref="`breadcrumb${index}`"
        :key="index"
        class="breadcrumb-item"
      >
        <KButton
          class="breadcrumb-button"
          :primary="false"
          appearance="flat-button"
          :text="breadcrumb.title"
          :disabled="!breadcrumbIsEnabled(breadcrumb)"
          tabindex="-1"
          @click="$emit('activate', breadcrumb)"
        />
      </li>
    </template>
  </ol>

</template>


<script>

  export default {
    name: 'ZimBreadcrumbsMenu',
    components: {},
    props: {
      breadcrumbs: {
        type: Array,
      },
      currentUrl: {
        type: String,
      },
    },
    computed: {
      visibleBreadcrumbs() {
        return this.breadcrumbs.slice(-4);
      },
    },
    methods: {
      breadcrumbIsEnabled(breadcrumb) {
        if (breadcrumb.href === undefined) {
          return false;
        } else {
          return breadcrumb.href !== this.currentUrl;
        }
      },
    },
    $trs: {},
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  ol {
    display: inline-block;
    padding: 0;
    margin: 0;
    list-style: none;
  }

  li {
    display: inline-block;
    max-width: 10rem;
  }

  .breadcrumb-button {
    text-overflow: ellipsis;
    text-transform: none;
  }

</style>
