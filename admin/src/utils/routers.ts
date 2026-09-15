import type { RouteRecordName, RouteRecordRaw } from 'vue-router';
/**
 * 通过递归过滤异步路由表
 * @param routes asyncRoutes
 * @param roles
 */
export function filterAsyncRoutes(
  routes: Array<RouteRecordRaw>,
  roles: string[],
  permissions: string[] = [],
) {
  const res: Array<RouteRecordRaw> = [];
  routes.forEach((route) => {
    const tmp = { ...route };
    if (hasPermission(roles, permissions, tmp)) {
      if (tmp.children) {
        tmp.children = filterAsyncRoutes(tmp.children, roles, permissions);
      }
      res.push(tmp);
    }
  });
  return res;
}

/**
 * 确定当前用户是否具有该路由的访问权限
 */
export function hasPermission(roles: string[], permissions: string[], route: RouteRecordRaw) {
  // 超级管理员拥有全量访问权限
  if (roles.includes('super_admin') || roles.includes('admin')) {
    return true;
  }
  const meta: any = route.meta;
  if (!meta) return true;

  // 按钮/页面细粒度权限码判定
  if (meta.perm) {
    return permissions.includes(meta.perm);
  }

  // 角色列表判定
  if (meta.roles && Array.isArray(meta.roles)) {
    return roles.some((role) => meta.roles.includes(role));
  }

  // 若未配置权限限制，则默认全员可访问
  return true;
}

/**
 * @description 使用递归，过滤需要缓存的路由
 * @param {Array} _route 所有路由表
 * @param {Array} _cache 缓存的路由表
 * @return void
 * */

export function filterKeepAlive(routers: Array<RouteRecordRaw>) {
  const cacheRouter: Array<RouteRecordName> = [];
  const deep = (routers: Array<RouteRecordRaw>) => {
    routers.forEach((item) => {
      if (item.meta?.keepAlive && item.name) {
        cacheRouter.push(item.name);
      }
      if (item.children && item.children.length) {
        deep(item.children);
      }
    });
  };
  deep(routers);
  return cacheRouter;
}
