import Layout from '@/layout/index.vue';

const cUserRouter = [
  {
    path: '/c-users',
    component: Layout,
    redirect: '/c-users/list',
    name: 'cUsers',
    meta: {
      title: '用户与资产运营',
      icon: 'UserFilled',
    },
    children: [
      {
        path: '/c-users/list',
        component: () => import('@/views/cUser/index.vue'),
        name: 'cUserList',
        meta: {
          title: 'C端用户画像',
          icon: 'User',
          perm: 'ops:cuser:view',
        },
      },
    ],
  },
];

export default cUserRouter;
