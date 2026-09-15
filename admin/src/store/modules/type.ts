import type { RouteLocationNormalizedLoaded, RouteRecordName, RouteRecordRaw } from 'vue-router';

export interface ITagsViewStore {
  activeTabsValue: string;
  visitedViews: RouteLocationNormalizedLoaded[];
  cachedViews: RouteLocationNormalizedLoaded[];
}

export interface ISettingStore {
  // menu 是否收缩
  isCollapse: boolean;
  // 动画
  withoutAnimation: boolean;
  // 客户端
  device: string;
  // 刷新当前页
  isReload: boolean;
  // 主题设置
  themeConfig: IThemeConfig;
}

export interface IThemeConfig {
  // 显示设置
  showSetting: boolean;
  // 菜单展示模式 默认 vertical   horizontal / vertical /columns
  mode: string;
  // tagsView 是否展示 默认展示
  showTag: boolean;
  // 页脚
  footer: boolean;
  // 深色模式 切换暗黑模式
  isDark: boolean;
  // 显示侧边栏Logo
  showLogo: boolean;
  // 主题颜色
  primary: string;
  // element组件大小
  globalComSize: string;
  // 是否只保持一个子菜单的展开
  uniqueOpened: boolean;
  // 固定header
  fixedHeader: boolean;
  // 灰色模式
  gray: boolean;
  // 色弱模式
  weak: boolean;
}

export interface IUserStore {
  // 登录token
  token: string;
  // 登录用户信息
  userInfo: IUserInfo | null;
  // 角色
  roles: string[];
  // 权限
  permissions: string[];
}

export interface IUserInfo {
  id: string;
  username: string;
  email: string;
  real_name: string;
  avatar?: string | null;
  phone?: string | null;
  job_number?: string | null;
  department_id?: string | null;
  department_name?: string | null;
  is_super_admin: boolean;
  status: string;
  name?: string;
  photo?: string | null;
}

export interface IPermission {
  // 路由
  routes: RouteRecordRaw[];
  // 动态路由
  addRoutes: RouteRecordRaw[];
  // 缓存路由
  cacheRoutes: RouteRecordName[];
}
