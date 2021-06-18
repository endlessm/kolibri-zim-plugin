<template>

  <ShuffleIconBaselineSvg :style="{ fill: computedColor }" />

</template>


<script>

  import ShuffleIconBaselineSvg from 'kolibri-design-system/lib/KIcon/precompiled-icons/material-icons/shuffle/baseline.vue';

  export default {
    name: 'ShuffleIcon',
    components: {
      ShuffleIconBaselineSvg,
    },
    props: {
      color: {
        type: String,
        default: null,
      },
      disableColor: {
        type: Boolean,
        default: false,
      },
    },
    computed: {
      computedColor() {
        if (this.disableColor) {
          return null;
        }
        if (this.color) {
          return this.color;
        }
        return this.$themeTokens.text;
      },
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  svg {
    position: relative;
    top: 0.125em;
    width: 1.125em;
    height: 1.125em;
    transition: fill $core-time ease;
  }

</style>
