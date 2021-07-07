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
          :text="breadcrumb.title"
          :title="breadcrumb.title"
          :disabled="!breadcrumbIsEnabled(breadcrumb)"
          @click="$emit('activate', breadcrumb)"
        />
      </li>
    </template>
  </transition-group>

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
    margin-left: 4px;
    list-style: none;
  }

  li {
    display: inline-block;
    max-width: 8rem;
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
