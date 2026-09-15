<template>
  <el-drawer v-model="drawer" title="主题与界面配置" size="320px">
    <div class="theme-item">
      <label>导航栏布局</label>
      <el-select
        v-model="layout"
        placeholder="请选择"
        style="width: 140px"
        @change="(val: string) => changeSwitch('mode', val)"
      >
        <el-option label="纵向导航" value="vertical" />
        <el-option label="横向导航" value="horizontal" />
        <el-option label="分栏导航" value="columns" />
      </el-select>
    </div>
    <div class="theme-item">
      <label>系统主题色</label>
      <el-color-picker
        v-model="primary"
        :predefine="THEME_PRESET_COLORS"
        @change="changePrimary"
      />
    </div>
    <div class="theme-item">
      <label>深色模式</label>
      <switch-dark />
    </div>
    <div class="theme-item">
      <label>灰色悼念模式</label>
      <el-switch v-model="gray" @change="(val: boolean) => changeGrayWeak('gray', val)" />
    </div>
    <div class="theme-item">
      <label>色弱辅助模式</label>
      <el-switch v-model="weak" @change="(val: boolean) => changeGrayWeak('weak', val)" />
    </div>
    <div class="theme-item">
      <label>标签栏 (TagsView)</label>
      <el-switch v-model="showTag" @change="(val: boolean) => changeSwitch('showTag', val)" />
    </div>
    <div class="theme-item">
      <label>侧边栏 Logo</label>
      <el-switch v-model="showLogo" @change="(val: boolean) => changeSwitch('showLogo', val)" />
    </div>
    <div class="theme-item">
      <label>子菜单单项手风琴</label>
      <el-switch v-model="uniqueOpened" @change="(val: boolean) => changeSwitch('uniqueOpened', val)" />
    </div>
    <div class="theme-item">
      <label>固定顶栏 (Header)</label>
      <el-switch v-model="fixedHeader" @change="(val: boolean) => changeSwitch('fixedHeader', val)" />
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
import SwitchDark from '@/components/SwitchDark/index.vue';
import { PRIMARY_COLOR } from '@/config/index';
import { useSettingStore } from '@/store/modules/setting';
import { THEME_PRESET_COLORS, applyThemeColor } from '@/theme';
import { closeLoading, openLoading } from '@/utils/element';
import { ElMessage } from 'element-plus';
import { computed, ref, watch } from 'vue';

const settingStore = useSettingStore();
const layout = ref(settingStore.themeConfig.mode);
const showTag = ref(settingStore.themeConfig.showTag);
const showLogo = ref(settingStore.themeConfig.showLogo);
const uniqueOpened = ref(settingStore.themeConfig.uniqueOpened);
const primary = ref(settingStore.themeConfig.primary || PRIMARY_COLOR);
const fixedHeader = ref(settingStore.themeConfig.fixedHeader);
const gray = ref(settingStore.themeConfig.gray);
const weak = ref(settingStore.themeConfig.weak);

const drawer = computed({
  get() {
    return settingStore.themeConfig.showSetting;
  },
  set(val: boolean) {
    settingStore.setThemeConfig({ key: 'showSetting', val });
  },
});

const changeSwitch = (key: string, val: any) => {
  settingStore.setThemeConfig({ key, val });
  if (key === 'mode') {
    openLoading();
    setTimeout(() => {
      closeLoading();
    }, 400);
  }
};

// 监听布局变化同步至 body class
watch(
  () => layout.value,
  (val) => {
    if (typeof document !== 'undefined') {
      document.body.setAttribute('class', `layout-${val}`);
    }
  },
  { immediate: true },
);

// 修改主题颜色，同时生成衍生色并持久化
const changePrimary = (val: string | null) => {
  const color = val || PRIMARY_COLOR;
  primary.value = color;
  if (!val) {
    ElMessage.success(`主题颜色已重置为默认值 ${PRIMARY_COLOR}`);
  }
  applyThemeColor(color, Boolean(settingStore.themeConfig.isDark));
  changeSwitch('primary', color);
};

// 灰色与色弱滤镜
const changeGrayWeak = (type: 'gray' | 'weak', val: boolean) => {
  if (typeof document === 'undefined') return;
  const html = document.documentElement;
  if (!val) {
    html.style.filter = '';
  } else if (type === 'gray') {
    html.style.filter = 'grayscale(100%)';
  } else if (type === 'weak') {
    html.style.filter = 'invert(80%)';
  }
  changeSwitch(type, val);
};
</script>

<style lang="scss" scoped>
:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

:deep(.el-drawer__title) {
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 16px;
}

.theme-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-bottom: 18px;
  color: var(--el-text-color-regular);
  font-size: 14px;
}
</style>
