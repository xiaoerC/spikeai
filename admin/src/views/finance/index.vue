<template>
  <div class="flex flex-col gap-4 p-4 w-full h-full box-border">
    <!-- 1. 顶部 4 大金融级宏观指标大盘卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-bg-color-overlay)] shadow-sm flex items-center justify-between">
        <div class="flex flex-col leading-snug">
          <span class="text-xs text-[var(--el-text-color-secondary)]">累计充值星元总额</span>
          <span class="text-2xl font-bold text-amber-500 mt-1 font-mono">
            {{ summary.total_star_recharged.toLocaleString() }} ★
          </span>
          <span class="text-[11px] text-[var(--el-text-color-placeholder)] mt-0.5">全站星元正向入账</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-500 text-xl font-bold">
          ★
        </div>
      </div>

      <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-bg-color-overlay)] shadow-sm flex items-center justify-between">
        <div class="flex flex-col leading-snug">
          <span class="text-xs text-[var(--el-text-color-secondary)]">累计充值月华总额</span>
          <span class="text-2xl font-bold text-sky-500 mt-1 font-mono">
            {{ summary.total_moon_recharged.toLocaleString() }} 🌙
          </span>
          <span class="text-[11px] text-[var(--el-text-color-placeholder)] mt-0.5">高阶算力核心储备</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-sky-500/10 flex items-center justify-center text-sky-500 text-xl font-bold">
          🌙
        </div>
      </div>

      <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-bg-color-overlay)] shadow-sm flex items-center justify-between">
        <div class="flex flex-col leading-snug">
          <span class="text-xs text-[var(--el-text-color-secondary)]">全站资金交易总笔数</span>
          <span class="text-2xl font-bold text-[var(--el-color-primary)] mt-1 font-mono">
            {{ summary.total_transactions_count.toLocaleString() }}
          </span>
          <span class="text-[11px] text-[var(--el-text-color-placeholder)] mt-0.5">包含充值/消耗/调账流水</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-[var(--el-color-primary)]/10 flex items-center justify-center text-[var(--el-color-primary)] text-xl">
          <el-icon><Tickets /></el-icon>
        </div>
      </div>

      <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-bg-color-overlay)] shadow-sm flex items-center justify-between">
        <div class="flex flex-col leading-snug">
          <span class="text-xs text-[var(--el-text-color-secondary)]">今日交易流水笔数</span>
          <span class="text-2xl font-bold text-emerald-500 mt-1 font-mono">
            {{ summary.today_transactions_count.toLocaleString() }}
          </span>
          <span class="text-[11px] text-[var(--el-text-color-placeholder)] mt-0.5">UTC 今日实时对账</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-500 text-xl">
          <el-icon><TrendCharts /></el-icon>
        </div>
      </div>
    </div>

    <!-- 2. 检索面板 -->
    <div class="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-sm">
      <el-form :inline="true" :model="query" class="flex flex-wrap items-center gap-3 !m-0">
        <el-form-item label="流水检索" class="!m-0">
          <el-input
            v-model="query.keyword"
            placeholder="搜索用户名 / 邮箱 / 流水备注"
            clearable
            class="!w-64"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="业务类型" class="!m-0">
          <el-select
            v-model="query.type"
            placeholder="全部类型"
            clearable
            class="!w-40"
          >
            <el-option label="充值入账 (recharge)" value="recharge" />
            <el-option label="管理员调账 (admin_adjust)" value="admin_adjust" />
            <el-option label="退款冲正 (admin_refund)" value="admin_refund" />
            <el-option label="星元对话消耗 (chat_star)" value="chat_star" />
            <el-option label="月华算力消耗 (chat_moon)" value="chat_moon" />
            <el-option label="每日签到福利 (daily_reward)" value="daily_reward" />
            <el-option label="创作者收益 (creator_share)" value="creator_share" />
          </el-select>
        </el-form-item>

        <el-form-item label="结算币种" class="!m-0">
          <el-radio-group v-model="query.currency" @change="handleSearch">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="star">★ 星元</el-radio-button>
            <el-radio-button value="moon">🌙 月华</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item class="!m-0">
          <div class="flex items-center gap-2">
            <el-button type="primary" @click="handleSearch">
              <el-icon class="mr-1"><Search /></el-icon> 查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon class="mr-1"><Refresh /></el-icon> 重置
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <div class="flex items-center gap-1.5 text-sm font-medium text-slate-700 dark:text-zinc-200">
        <span>检索结果:</span>
        <strong class="text-[var(--el-color-primary)] font-bold text-base font-mono">{{ total }}</strong>
        <span class="text-slate-500 dark:text-zinc-400 text-xs">笔</span>
      </div>
    </div>

    <!-- 3. 主体对账流水表格 -->
    <DataTable
      :columns="columns"
      :table-data="{ list: tableData, total }"
      :table-query="query"
      :loading="loading"
      table-title="对账明细与交易流水"
      class="w-full flex-1 min-h-0"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        @on-refresh="loadData"
      >
        <template #id="{ row }">
          <span class="font-mono text-xs text-[var(--el-text-color-primary)]" :title="row.id">
            {{ row.id.slice(0, 8) }}...{{ row.id.slice(-4) }}
          </span>
        </template>

        <template #user="{ row }">
          <div class="flex items-center gap-2.5 py-1">
            <el-avatar :size="32" :src="row.user_avatar" class="flex-shrink-0">
              {{ row.user_name.slice(0, 1) }}
            </el-avatar>
            <div class="flex flex-col leading-snug truncate">
              <span class="font-bold text-xs text-[var(--el-text-color-primary)] truncate">{{ row.user_name }}</span>
              <span class="text-[11px] text-[var(--el-text-color-secondary)] truncate" :title="row.user_email">{{ row.user_email }}</span>
            </div>
          </div>
        </template>

        <template #type="{ row }">
          <el-tag
            size="small"
            :type="row.type === 'recharge' ? 'success' : row.type === 'admin_refund' ? 'danger' : row.type.includes('adjust') ? 'warning' : 'info'"
            effect="light"
          >
            {{ formatType(row.type) }}
          </el-tag>
        </template>

        <template #currency="{ row }">
          <span :class="row.currency === 'star' ? 'text-amber-500 font-bold' : 'text-sky-500 font-bold'">
            {{ row.currency === 'star' ? '★ 星元' : '🌙 月华' }}
          </span>
        </template>

        <template #amount="{ row }">
          <div class="pr-3">
            <span
              class="font-mono font-bold text-sm"
              :class="row.amount > 0 ? 'text-emerald-500' : 'text-rose-500'"
            >
              {{ row.amount > 0 ? `+${row.amount}` : row.amount }}
            </span>
          </div>
        </template>

        <template #balance_after="{ row }">
          <div class="pr-3">
            <span class="font-mono text-xs text-[var(--el-text-color-regular)]">
              {{ row.balance_after }}
            </span>
          </div>
        </template>

        <template #description="{ row }">
          <span class="text-xs text-[var(--el-text-color-secondary)] line-clamp-2" :title="row.description">
            {{ row.description || '无详细备注' }}
          </span>
        </template>

        <template #created_at="{ row }">
          <span class="text-xs text-[var(--el-text-color-secondary)] font-mono">
            {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
          </span>
        </template>

        <template #actions="{ row }">
          <el-button
            v-if="row.amount > 0 && row.type !== 'admin_refund'"
            type="danger"
            link
            size="small"
            @click="handleRefund(row)"
          >
            退款冲正
          </el-button>
          <span v-else class="text-xs text-[var(--el-text-color-placeholder)]">-</span>
        </template>
      </DataTable>
  </div>
</template>

<script lang="ts" setup>
import {
  type IAdminFinanceSummary,
  type IAdminOrderTransactionItem,
  type IFinanceOrderQuery,
  getFinanceOrders,
  refundOrderTransaction,
} from '@/api/finance';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { onMounted, reactive, ref } from 'vue';

const loading = ref(false);
const tableData = ref<IAdminOrderTransactionItem[]>([]);
const total = ref(0);

const summary = reactive<IAdminFinanceSummary>({
  total_star_recharged: 0,
  total_moon_recharged: 0,
  total_transactions_count: 0,
  today_transactions_count: 0,
});

const query = reactive<IFinanceOrderQuery>({
  page: 1,
  size: 10,
  keyword: '',
  type: '',
  currency: '',
});

const columns: IColumnConfig[] = [
  { field: 'id', title: '流水单号', width: 160, align: 'center', slot: 'id' },
  { field: 'user_name', title: '交易用户', minWidth: 180, slot: 'user' },
  { field: 'type', title: '业务类型', width: 130, align: 'center', slot: 'type' },
  { field: 'currency', title: '币种', width: 100, align: 'center', slot: 'currency' },
  {
    field: 'amount',
    title: '交易数额',
    width: 130,
    align: 'right',
    headerAlign: 'right',
    slot: 'amount',
  },
  {
    field: 'balance_after',
    title: '变动后余额',
    width: 130,
    align: 'right',
    headerAlign: 'right',
    slot: 'balance_after',
  },
  { field: 'description', title: '流水备注 / 业务说明', minWidth: 220, slot: 'description' },
  { field: 'created_at', title: '发生时间', width: 170, align: 'center', slot: 'created_at' },
  { field: 'actions', title: '操作', width: 110, fixed: 'right', align: 'center', slot: 'actions' },
];

function handlePageChange(page: number) {
  query.page = page;
  loadData();
}

function handleSizeChange(size: number) {
  query.size = size;
  query.page = 1;
  loadData();
}

function formatType(type: string) {
  const map: Record<string, string> = {
    recharge: '充值入账',
    admin_adjust: '管理员调账',
    admin_refund: '退款冲正',
    chat_star: '星元对话',
    chat_moon: '月华算力',
    daily_reward: '每日福利',
    creator_share: '创作者分成',
    mod_buy: 'Mod购买',
    reward: '打赏收益',
  };
  return map[type] || type;
}

async function loadData() {
  try {
    loading.value = true;
    const res = await getFinanceOrders(query);
    tableData.value = res.list || [];
    total.value = res.total || 0;
    if (res.summary) {
      summary.total_star_recharged = res.summary.total_star_recharged || 0;
      summary.total_moon_recharged = res.summary.total_moon_recharged || 0;
      summary.total_transactions_count = res.summary.total_transactions_count || 0;
      summary.today_transactions_count = res.summary.today_transactions_count || 0;
    }
  } catch (error: any) {
    ElMessage.error(error?.message || '获取财务流水大盘失败');
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  query.page = 1;
  loadData();
}

function handleReset() {
  query.page = 1;
  query.keyword = '';
  query.type = '';
  query.currency = '';
  loadData();
}

async function handleRefund(row: any) {
  const item = row as IAdminOrderTransactionItem;
  try {
    const { value: reason } = await ElMessageBox.prompt(
      `确定对单号 ${item.id.slice(0, 8)}... (金额: +${item.amount} ${item.currency === 'star' ? '星元' : '月华'}) 执行退款冲正处置吗？该操作将从用户资产中扣回对应额度并记录金融审计流水。`,
      '金融退款冲正确认',
      {
        confirmButtonText: '确定冲正',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入退款冲正原因（如：用户误充、支付争议、风控撤回等）',
        inputPattern: /^.{2,100}$/,
        inputErrorMessage: '冲正原因需在 2 到 100 字之间',
      },
    );

    loading.value = true;
    await refundOrderTransaction(item.id, { reason });
    ElMessage.success('退款冲正处置成功，用户资产已扣减调平');
    loadData();
  } catch {
    // 取消
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>
