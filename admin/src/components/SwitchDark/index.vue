<template>
  <el-switch
    v-model="themeConfig.isDark"
    inline-prompt
    :active-icon="Sunny"
    :inactive-icon="Moon"
    @change="switchDark"
  />
</template>

<script setup lang="ts" name="switchDark">
import { useSettingStore } from '@/store/modules/setting';
import { Moon, Sunny } from '@element-plus/icons-vue';
import { computed, ref } from 'vue';

const SettingStore = useSettingStore();
// 设置信息
const themeConfig = computed(() => SettingStore.themeConfig);

// 切换暗黑模式
const switchDark = () => {
  const isDark = Boolean(themeConfig.value.isDark);
  if (typeof document !== 'undefined') {
    document.documentElement.classList.toggle('dark', isDark);
    document.documentElement.setAttribute('data-vxe-ui-theme', isDark ? 'dark' : 'light');
  }
};
</script>
