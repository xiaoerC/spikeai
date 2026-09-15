import Layout from '@/layout/index.vue';

const financeRouter = [
  {
    path: '/finance-ops',
    component: Layout,
    redirect: '/finance-ops/orders',
    name: 'financeOps',
    meta: {
      title: '财务与结算中心',
      icon: 'Money',
    },
    children: [
      {
        path: '/finance-ops/orders',
        component: () => import('@/views/finance/index.vue'),
        name: 'financeOrders',
        meta: {
          title: '订单与对账大盘',
          icon: 'Wallet',
          perm: 'ops:finance:view',
        },
      },
    ],
  },
];

export default financeRouter;
