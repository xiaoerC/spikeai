import router from '@/routers/index';
import { defineStore } from 'pinia';
import type { RouteLocationNormalizedLoaded } from 'vue-router';
import type { ITagsViewStore } from './type';

export const useTagsViewStore = defineStore('tagsViewStore', {
  state: (): ITagsViewStore => ({
    activeTabsValue: '/home',
    visitedViews: [],
    cachedViews: [],
  }),
  actions: {
    // 设置当前tabs
    setTabsMenuValue(val: string) {
      this.activeTabsValue = val;
    },
    // 添加页面
    addView(view: RouteLocationNormalizedLoaded) {
      this.addVisitedView(view);
    },
    // 删除页面
    removeView(routes: string[]) {
      this.visitedViews = this.visitedViews.filter((item) => !routes.includes(item.path));
    },
    // 添加访问页面
    addVisitedView(view: RouteLocationNormalizedLoaded) {
      this.setTabsMenuValue(view.path);
      if (this.visitedViews.some((v) => v.path === view.path)) return;

      this.visitedViews.push(
        Object.assign({}, view, {
          title: view.meta.title || 'no-name',
        }),
      );
      if (view.meta.keepAlive) {
        this.cachedViews.push(view);
      }
    },
    // 删除页面
    delView(activeTabPath: string) {
      this.delVisitedView(activeTabPath);
      this.delCachedView(activeTabPath);
    },
    // 跳转上一下页面
    toLastView(activeTabPath: string) {
      const index = this.visitedViews.findIndex((item) => item.path === activeTabPath);
      const nextTab = this.visitedViews[index + 1] || this.visitedViews[index - 1];
      if (!nextTab) return;
      router.push(nextTab.path);
      this.addVisitedView(nextTab);
    },
    // 删除访问的页面
    delVisitedView(path: string) {
      this.visitedViews = this.visitedViews.filter((v) => {
        return v.path !== path || v.meta.affix;
      });
      this.cachedViews = this.cachedViews.filter((v) => {
        return v.path !== path || v.meta.affix;
      });
    },
    // 删除缓存的页面
    delCachedView(path: string) {
      const index = this.cachedViews.findIndex((item) => item.path === path);
      if (index === -1) return;
      this.cachedViews.splice(index, 1);
    },
    // 清空所有页面
    clearVisitedView() {
      this.delAllViews();
    },
    // 删除所有页面
    delAllViews() {
      this.visitedViews = this.visitedViews.filter((v) => v.meta.affix);
      this.cachedViews = this.visitedViews.filter((v) => v.meta.affix);
    },
    // 关闭除当前所有页面
    delOtherViews(path: string) {
      this.visitedViews = this.visitedViews.filter((item) => {
        return item.path === path || item.meta.affix;
      });
      this.cachedViews = this.visitedViews.filter((item) => {
        return item.path === path || item.meta.affix;
      });
    },
    // 回到首页
    goHome() {
      this.activeTabsValue = '/home';
      router.push({ path: '/home' });
    },
  },
});
