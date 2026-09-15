import Layout from '@/layout/index.vue';

const omRouter = [
  {
    path: '/om',
    component: Layout,
    redirect: '/om/department',
    name: 'om',
    meta: {
      title: '组织管理',
      icon: 'office-building',
    },
    children: [
      {
        path: '/om/department',
        component: () => import('@/views/om/department/index.vue'),
        name: 'department',
        meta: { title: '部门管理', icon: 'OfficeBuilding', perm: 'system:dept:view' },
      },
      {
        path: '/om/role',
        component: () => import('@/views/om/role/index.vue'),
        name: 'role',
        meta: { title: '角色管理', icon: 'Lock', perm: 'system:role:view' },
      },
      {
        path: '/om/user',
        component: () => import('@/views/om/user/index.vue'),
        name: 'user',
        meta: { title: '用户管理', icon: 'User', perm: 'system:user:view' },
      },
    ],
  },
];

export default omRouter;
