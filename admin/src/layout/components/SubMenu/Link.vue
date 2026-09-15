<template>
  <component :is="linkType" v-bind="getLinkProps(to)">
    <slot />
  </component>
</template>

<script lang="ts" setup>
import { isExternal } from '@/utils/validate';
import { computed } from 'vue';

const props = defineProps<{
  to: string;
}>();

const isExt = computed(() => isExternal(props.to));
const linkType = computed(() => (isExt.value ? 'a' : 'router-link'));

const getLinkProps = (to: string) => {
  if (isExt.value) {
    return {
      href: to,
      target: '_blank',
      rel: 'noopener',
    };
  }
  return {
    to,
  };
};
</script>

<style lang="scss" scoped>
a {
  text-decoration: none;
}
</style>
