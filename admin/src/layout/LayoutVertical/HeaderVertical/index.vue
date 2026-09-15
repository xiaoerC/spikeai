<template>
  <!--纵向布局-->
  <Height />
  <div
    class="m-layout-header"
    :class="{
      'fixed-header': themeConfig.fixedHeader,
      collapse: themeConfig.fixedHeader && isCollapse,
      'no-collapse': themeConfig.fixedHeader && !isCollapse
    }"
  >
    <div class="header-inner">
      <HeaderToolLeft />
      <HeaderToolRight />
    </div>
    <TagsView v-if="themeConfig.showTag" />
  </div>
</template>

<script lang="ts" setup>
import HeaderToolLeft from '../../components/Header/ToolLeft.vue';
import HeaderToolRight from '../../components/Header/ToolRight.vue';
// 引入组件
import Height from '../../components/Header/components/Height.vue';
import TagsView from '../../components/TagsView/index.vue';

import { useSettingStore } from '@/store/modules/setting';
import { computed } from 'vue';
const SettingStore = useSettingStore();

// 主题配置
const themeConfig = computed(() => SettingStore.themeConfig);
const isCollapse = computed(() => !SettingStore.isCollapse);
</script>

<style lang="scss" scoped>
  @use './index' as *;
</style>
