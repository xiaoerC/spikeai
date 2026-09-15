<template>
  <div v-if="themeConfig.fixedHeader" :style="{ height: `${themeConfig.showTag ? 90 : 50}px` }"></div>
</template>

<script lang="ts" setup>
import { useSettingStore } from '@/store/modules/setting';
import { computed } from 'vue';
const SettingStore = useSettingStore();
const themeConfig = computed(() => SettingStore.themeConfig);
</script>
