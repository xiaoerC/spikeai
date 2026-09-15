import { PRIMARY_COLOR } from '@/config';
import { defineStore } from 'pinia';
import type { ISettingStore } from './type';

export const useSettingStore = defineStore('settingState', {
  // state: 返回对象的函数
  state: (): ISettingStore => ({
    isCollapse: true,
    withoutAnimation: false,
    device: 'desktop',
    isReload: true,
    themeConfig: {
      showSetting: false,
      mode: 'vertical',
      showTag: true,
      footer: true,
      isDark: false,
      showLogo: true,
      primary: PRIMARY_COLOR,
      globalComSize: 'default',
      uniqueOpened: false,
      fixedHeader: true,
      gray: false,
      weak: false,
    },
  }),
  getters: {},
  // 可以同步 也可以异步
  actions: {
    // 设置主题
    setThemeConfig({ key, val }: Record<string, any>) {
      this.themeConfig[key] = val;
    },
    // 切换 Collapse
    setCollapse(value: boolean) {
      this.isCollapse = value;
      this.withoutAnimation = false;
    },
    // 关闭侧边栏
    closeSideBar({ withoutAnimation }: { withoutAnimation: boolean }) {
      this.isCollapse = false;
      this.withoutAnimation = withoutAnimation;
    },
    // 替换当前客户端
    toggleDevice(device: string) {
      this.device = device;
    },
    // 刷新
    setReload() {
      this.isReload = false;
      setTimeout(() => {
        this.isReload = true;
      }, 50);
    },
  },
  // 这部分数据不需要存储
  persist: {
    // 本地存储的名称
    key: 'settingState',
    // 保存的位置
    storage: window.localStorage, // localstorage
    afterHydrate: (ctx) => {
      // 迁移旧版默认值：将手风琴模式默认设为 false（支持多二级菜单同时展开）
      const MIGRATION_KEY = 'spk_sidebar_multi_open_v1';
      if (!window.localStorage.getItem(MIGRATION_KEY)) {
        if (ctx.store.themeConfig) {
          ctx.store.themeConfig.uniqueOpened = false;
        }
        window.localStorage.setItem(MIGRATION_KEY, '1');
      }
    },
  },
});
