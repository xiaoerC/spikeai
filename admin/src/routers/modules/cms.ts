import Layout from '@/layout/index.vue';

const cmsRouter = [
  {
    path: '/cms-ops',
    component: Layout,
    redirect: '/cms-ops/notices',
    name: 'cmsOps',
    meta: {
      title: '运营与内容中心',
      icon: 'Bell',
    },
    children: [
      {
        path: '/cms-ops/notices',
        component: () => import('@/views/cms/notice/index.vue'),
        name: 'cmsNoticeList',
        meta: {
          title: '系统公告管理',
          icon: 'Notification',
          perm: 'ops:notice:view',
        },
      },
      {
        path: '/cms-ops/activities',
        component: () => import('@/views/cms/activity/index.vue'),
        name: 'cmsActivityList',
        meta: {
          title: '运营活动管理',
          icon: 'Present',
          perm: 'ops:activity:view',
        },
      },
    ],
  },
];

export default cmsRouter;
