<template>
  <div v-if="device === 'mobile' && !isCollapse" class="drawer-bg" @click="handleClickOutside" />
</template>

<script lang="ts" setup>
import { useResizeHandler } from '@/hooks/useResizeHandler';
import { useSettingStore } from '@/store/modules/setting';
import { computed } from 'vue';

const { device } = useResizeHandler();
const SettingStore = useSettingStore();

// 是否折叠
const isCollapse = computed(() => !SettingStore.isCollapse);

// 移动端点击
const handleClickOutside = () => {
  console.log('移动端点击');
  SettingStore.closeSideBar({ withoutAnimation: false });
};
</script>

<style lang="scss" scoped></style>
