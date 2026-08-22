import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/home/index.vue"),
      meta: {
        title: "叙梦 Naro - AI 角色市场",
      },
    },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/login/index.vue"),
      meta: {
        title: "登录 / 注册 - 叙梦 Naro",
      },
    },
    {
      path: "/history",
      name: "history",
      component: () => import("@/views/history/index.vue"),
      meta: {
        title: "历史记录 - 叙梦 Naro",
      },
    },
    {
      path: "/create",
      name: "create",
      component: () => import("@/views/character-create/index.vue"),
      meta: {
        title: "创建角色 - 叙梦 Naro",
      },
    },
    {
      path: "/profile",
      name: "profile",
      component: () => import("@/views/profile/index.vue"),
      meta: {
        title: "个人中心 - 叙梦 Naro",
      },
    },
    {
      path: "/creator",
      name: "creator",
      component: () => import("@/views/creator/index.vue"),
      meta: {
        title: "创作者专区 - 叙梦 Naro",
      },
    },
    {
      path: "/ranking",
      name: "ranking",
      component: () => import("@/views/ranking/index.vue"),
      meta: {
        title: "等级榜 - 叙梦 Naro",
      },
    },
    {
      path: "/activity",
      name: "activity",
      component: () => import("@/views/activity/index.vue"),
      meta: {
        title: "活动中心 - 叙梦 Naro",
      },
    },
    {
      path: "/notice",
      name: "notice",
      component: () => import("@/views/notice/index.vue"),
      meta: {
        title: "公告中心 - 叙梦 Naro",
      },
    },
    {
      path: "/survey",
      name: "survey",
      component: () => import("@/views/survey/index.vue"),
      meta: {
        title: "问卷调查 - 叙梦 Naro",
      },
    },
    {
      path: "/help",
      name: "help",
      component: () => import("@/views/help/index.vue"),
      meta: {
        title: "帮助中心 - 叙梦 Naro",
      },
    },
    {
      path: "/character-history",
      name: "character-history",
      component: () => import("@/views/character-history/index.vue"),
      meta: {
        title: "角色上线历史 - 叙梦 Naro",
      },
    },
    {
      path: "/character/:id",
      name: "character-detail",
      component: () => import("@/views/character-detail/index.vue"),
      meta: {
        title: "角色详情 - 叙梦 Naro",
      },
    },
    {
      path: "/models",
      name: "models",
      component: () => import("@/views/chat-models/index.vue"),
      meta: {
        title: "更多模型 - 叙梦 Naro",
      },
    },
    {
      path: "/chat/:id",
      name: "chat",
      component: () => import("@/views/chat/index.vue"),
      meta: {
        title: "AI 对话 - 叙梦 Naro",
      },
    },

    {
      path: "/:pathMatch(.*)*",
      redirect: "/",
    },
  ],
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    return { top: 0 };
  },
});

router.afterEach((to) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} | 沉浸式 AI 角色互动与分支剧情社区`;
  }
});

export default router;
