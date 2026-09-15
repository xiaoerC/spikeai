import Layout from '@/layout/index.vue';

const chatOpsRouter = [
  {
    path: '/chat-ops',
    component: Layout,
    redirect: '/chat-ops/sessions',
    name: 'chatOps',
    meta: {
      title: '对话与推理审计',
      icon: 'ChatDotRound',
    },
    children: [
      {
        path: '/chat-ops/sessions',
        component: () => import('@/views/chatOps/index.vue'),
        name: 'chatSessionList',
        meta: {
          title: '会话大盘与回溯',
          icon: 'ChatLineRound',
          perm: 'ops:chat:view',
        },
      },
    ],
  },
];

export default chatOpsRouter;
