import Layout from '@/layout/index.vue';
import {
  type RouteRecordRaw,
  type Router,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';

// 扩展继承属性
interface extendRoute {
  hidden?: boolean;
}

import cUserRouter from './modules/cUser';
import characterRouter from './modules/character';
import chatOpsRouter from './modules/chatOps';
import cmsRouter from './modules/cms';
import financeRouter from './modules/finance';
import omRouter from './modules/om';
import settingsRouter from './modules/settings';

// 异步权限路由表
export const asyncRoutes: Array<RouteRecordRaw & extendRoute> = [
  ...cUserRouter,
  ...characterRouter,
  ...chatOpsRouter,
  ...settingsRouter,
  ...financeRouter,
  ...cmsRouter,
  ...omRouter,
];

/**
 * path ==> 路由路径
 * name ==> 路由名称
 * component ==> 路由组件
 * redirect ==> 路由重定向
 * alwaysShow ==> 如果设置为true，将始终显示根菜单，无论其子路由长度如何
 * hidden ==> 如果“hidden:true”不会显示在侧边栏中（默认值为false）
 * keepAlive ==> 设为true 缓存
 * meta ==> 路由元信息
 * meta.title ==> 路由标题
 * meta.icon ==> 菜单icon
 * meta.affix ==> 如果设置为true将会出现在 标签栏中
 * meta.breadcrumb ==> 如果设置为false，该项将隐藏在breadcrumb中（默认值为true）
 * meta.activeMenu ==> 详情页的时候可以设置菜单高亮 ,高亮菜单的path
 */

export const constantRoutes: Array<RouteRecordRaw & extendRoute> = [
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/errorPages/404.vue'),
    hidden: true,
  },
  {
    path: '/403',
    name: '403',
    component: () => import('@/views/errorPages/403.vue'),
    hidden: true,
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/index.vue'),
    hidden: true,
    meta: { title: '登录' },
  },
  {
    path: '/',
    name: 'layout',
    component: Layout,
    redirect: '/home',
    meta: { title: '首页', icon: 'House' },
    children: [
      {
        path: '/home',
        component: () => import('@/views/home/index.vue'),
        name: 'home',
        meta: { title: '首页', icon: 'House', affix: true, role: ['other'] },
      },
    ],
  },
];

/**
 * notFoundRouter(找不到路由)
 */
export const notFoundRouter = {
  path: '/:pathMatch(.*)',
  name: 'notFound',
  redirect: '/404',
};

const router = createRouter({
  // history: createWebHistory(process.env.BASE_URL), // history
  history: createWebHashHistory(), // hash
  routes: constantRoutes,
});

export default router;
