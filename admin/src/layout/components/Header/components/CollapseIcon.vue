<template>
  <div class="hamburger-container" @click="handleCollapse">
    <el-icon v-if="isCollapse" class="icon"><expand /></el-icon>
    <el-icon v-else class="icon"><fold /></el-icon>
  </div>
</template>
<script lang="ts" setup>
import { useSettingStore } from '@/store/modules/setting';
import { computed } from 'vue';
const SettingStore = useSettingStore();
const isCollapse = computed(() => !SettingStore.isCollapse);
const handleCollapse = () => {
  SettingStore.setCollapse(isCollapse.value);
};
</script>
<style lang="scss" scoped>
  .hamburger-container {
    display: flex;
    align-items: center;
    height: 100%;
    padding: 0 15px;

    &:hover {
      background: var(--sidebar-hover-bg-color);
    }

    .icon {
      font-size: 20px;
      color: var(--header-text-color);
      cursor: pointer;
      transition: color 0.2s;

      &:hover {
        color: var(--el-color-primary);
      }
    }
  }
</style>
