import Layout from '@/layout/index.vue';

const characterRouter = [
  {
    path: '/character-ops',
    component: Layout,
    redirect: '/character-ops/list',
    name: 'characterOps',
    meta: {
      title: '内容与设定治理',
      icon: 'DocumentCopy',
    },
    children: [
      {
        path: '/character-ops/list',
        component: () => import('@/views/character/index.vue'),
        name: 'characterList',
        meta: {
          title: '角色卡与设定集',
          icon: 'CollectionTag',
          perm: 'ops:character:view',
        },
      },
    ],
  },
];

export default characterRouter;
