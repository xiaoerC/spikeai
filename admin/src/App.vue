<template>
  <el-config-provider :size="globalComSize" :locale="zhCn">
    <router-view></router-view>
  </el-config-provider>
</template>

<script lang="ts" setup>
import { useSettingStore } from '@/store/modules/setting';
import { applyThemeColor } from '@/theme';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { computed, onMounted, watch } from 'vue';

const settingStore = useSettingStore();
const globalComSize = computed<any>((): string => settingStore.themeConfig.globalComSize);

// 初始化并监听主题颜色与暗黑模式
const syncTheme = () => {
  const primary = settingStore.themeConfig.primary || '#409EFF';
  const isDark = Boolean(settingStore.themeConfig.isDark);
  applyThemeColor(primary, isDark);
  if (typeof document !== 'undefined') {
    document.documentElement.classList.toggle('dark', isDark);
    document.documentElement.setAttribute('data-vxe-ui-theme', isDark ? 'dark' : 'light');
  }
};

onMounted(() => {
  syncTheme();
});

watch([() => settingStore.themeConfig.primary, () => settingStore.themeConfig.isDark], () => {
  syncTheme();
});
</script>

<style lang="scss">
#app {
  position: relative;
  width: 100%;
  height: 100%;
  color: var(--el-text-color-primary);
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    'PingFang SC',
    'Hiragino Sans GB',
    'Microsoft YaHei',
    '微软雅黑',
    'Helvetica Neue',
    Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.el-pager li:focus {
  border: none;
}

.el-dropdown:focus {
  border: none;
}

.svg-icon:focus {
  border: none;
}
</style>
