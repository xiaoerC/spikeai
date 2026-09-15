<template>
  <el-menu-item :index="subItem.path" @click="handleClickMenu(subItem)">
    <el-icon>
      <component :is="subItem?.meta?.icon"></component>
    </el-icon>
    <template #title>
      <span>{{ subItem?.meta?.title }}</span>
    </template>
  </el-menu-item>
</template>

<script setup lang="ts">
import { isExternal } from '@/utils/validate';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const props = defineProps({
  menuList: {
    type: Array,
    default: () => [],
  },
  subItem: {
    type: Object,
    default: () => {},
  },
});

const handleClickMenu = (subItem) => {
  if (isExternal(subItem.path)) return window.open(subItem.path, '_blank');
  router.push(subItem.path);
};
</script>
