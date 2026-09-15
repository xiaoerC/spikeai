import { asyncRoutes, constantRoutes, notFoundRouter } from '@/routers/index';
import { filterAsyncRoutes, filterKeepAlive } from '@/utils/routers';
import { defineStore } from 'pinia';
import type { RouteRecordRaw } from 'vue-router';
import type { IPermission } from './type';
export const usePermissionStore = defineStore('permissionState', {
  // state: 返回对象的函数
  state: (): IPermission => ({
    // 路由
    routes: [],
    // 动态路由
    addRoutes: [],
    // 缓存路由
    cacheRoutes: [],
  }),
  getters: {
    permission_routes: (state) => {
      return state.routes;
    },
    keepAliveRoutes: (state) => {
      return filterKeepAlive(asyncRoutes);
    },
  },
  // 可以同步 也可以异步
  actions: {
    // 生成路由
    generateRoutes(roles: string[], permissions: string[] = []): Promise<any[]> {
      return new Promise((resolve) => {
        let accessedRoutes: RouteRecordRaw[];
        if (roles && roles.length && (roles.includes('super_admin') || roles.includes('admin'))) {
          accessedRoutes = asyncRoutes || [];
        } else {
          accessedRoutes = filterAsyncRoutes(asyncRoutes, roles, permissions);
        }
        accessedRoutes = accessedRoutes.concat(notFoundRouter);
        this.routes = constantRoutes.concat(accessedRoutes);
        this.addRoutes = accessedRoutes;
        resolve(accessedRoutes);
      });
    },

    // 清楚路由
    clearRoutes() {
      this.routes = [];
      this.addRoutes = [];
      this.cacheRoutes = [];
    },
    getCacheRoutes() {
      this.cacheRoutes = filterKeepAlive(asyncRoutes);
      return this.cacheRoutes;
    },
  },
});
