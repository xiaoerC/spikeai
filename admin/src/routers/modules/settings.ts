import Layout from '@/layout/index.vue';

const settingsRouter = [
  {
    path: '/settings',
    component: Layout,
    redirect: '/settings/tavern',
    name: 'settings',
    meta: {
      title: 'AI 调音中枢',
      icon: 'Operation',
    },
    children: [
      {
        path: '/settings/tavern',
        component: () => import('@/views/settings/tavern/index.vue'),
        name: 'tavernStudio',
        meta: {
          title: 'SillyTavern 调音中枢',
          icon: 'Setting',
          perm: 'system:tavern:view',
        },
      },
      {
        path: '/settings/llm',
        component: () => import('@/views/settings/llm/index.vue'),
        name: 'llmStudio',
        meta: {
          title: '大模型 API 配置',
          icon: 'Connection',
          perm: 'system:settings:view',
        },
      },
    ],
  },
];

export default settingsRouter;
