<template>
  <el-drawer
    v-model="visible"
    title="C 端用户画像与资产明细"
    size="620px"
    destroy-on-close
    class="custom-drawer"
  >
    <div v-if="user" class="flex flex-col gap-6">
      <!-- 1. 用户核心身份与画像卡片 -->
      <div class="flex items-start gap-4 p-4 rounded-xl bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
        <el-avatar :size="56" :src="user.avatar_url">
          {{ user.username.slice(0, 1).toUpperCase() }}
        </el-avatar>
        <div class="flex flex-col flex-1 gap-1">
          <div class="flex items-center justify-between">
            <span class="text-base font-bold text-[var(--el-text-color-primary)]">
              {{ user.username }}
            </span>
            <el-tag
              :type="user.status === 'active' ? 'success' : 'danger'"
              size="small"
              class="font-medium"
            >
              {{ user.status === 'active' ? '正常' : user.status === 'banned' ? '已封禁' : '已冻结' }}
            </el-tag>
          </div>
          <span class="text-xs text-[var(--el-text-color-secondary)]">UID: {{ user.id }}</span>
          <span class="text-xs text-[var(--el-text-color-secondary)]">邮箱: {{ user.email }}</span>
          <span class="text-xs text-[var(--el-text-color-secondary)]">专属邀请码: {{ user.invite_code }}</span>
        </div>
      </div>

      <!-- 2. 等级画像与创作者生态指标 -->
      <div class="grid grid-cols-2 gap-3">
        <div class="flex flex-col p-3 rounded-lg border border-[var(--el-border-color-lighter)] bg-[var(--el-bg-color-overlay)]">
          <span class="text-xs text-[var(--el-text-color-secondary)]">玩家成长画像</span>
          <div class="flex items-baseline gap-2 mt-1">
            <span class="text-lg font-bold text-[var(--el-color-primary)]">Lv.{{ user.player_level }}</span>
            <span class="text-xs text-[var(--el-text-color-placeholder)]">经验: {{ user.player_xp }}</span>
          </div>
          <span class="text-xs text-[var(--el-text-color-secondary)] mt-2">VIP 等级: VIP {{ user.vip_level }}</span>
        </div>

        <div class="flex flex-col p-3 rounded-lg border border-[var(--el-border-color-lighter)] bg-[var(--el-bg-color-overlay)]">
          <span class="text-xs text-[var(--el-text-color-secondary)]">创作者与互动贡献</span>
          <div class="flex items-baseline gap-2 mt-1">
            <span class="text-lg font-bold text-amber-500">Lv.{{ user.creator_level }}</span>
            <span class="text-xs text-[var(--el-text-color-placeholder)]">作品: {{ user.character_count }} 个</span>
          </div>
          <span class="text-xs text-[var(--el-text-color-secondary)] mt-2">参与会话: {{ user.chat_session_count }} 场</span>
        </div>
      </div>

      <!-- 3. 资产双币余额总览 -->
      <div class="flex flex-col gap-2 p-4 rounded-xl bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
        <div class="flex items-center justify-between">
          <span class="text-sm font-semibold text-[var(--el-text-color-primary)]">当前资产储备</span>
          <el-button type="primary" link size="small" @click="handleOpenAdjust">
            人工调账
          </el-button>
        </div>
        <div class="grid grid-cols-2 gap-4 mt-2">
          <div class="flex flex-col p-3 rounded-lg bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)]">
            <span class="text-xs text-[var(--el-text-color-secondary)]">星元 (基础剧情代币)</span>
            <span class="text-xl font-black text-amber-500 mt-1">{{ user.star_coins }} ★</span>
          </div>
          <div class="flex flex-col p-3 rounded-lg bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)]">
            <span class="text-xs text-[var(--el-text-color-secondary)]">月华 (高级算力代币)</span>
            <span class="text-xl font-black text-cyan-500 mt-1">{{ user.moon_gems }} 🌙</span>
          </div>
        </div>
      </div>

      <!-- 4. 钱包资金流动审计流水明细 -->
      <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <span class="text-sm font-semibold text-[var(--el-text-color-primary)]">资金审计流水记录</span>
          <el-radio-group v-model="txCurrency" size="small" @change="fetchTransactions(1)">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="star">仅星元</el-radio-button>
            <el-radio-button value="moon">仅月华</el-radio-button>
          </el-radio-group>
        </div>

        <DataTable
          :columns="txColumns"
          :table-data="{ list: transactions, total: txTotal }"
          :table-query="{ page: txPage, size: txSize }"
          :loading="loadingTx"
          :show-table-setting="false"
          :is-page-small="true"
          :is-show-header="false"
          :max-height="360"
          @current-change="fetchTransactions"
          @size-change="(size: number) => { txSize = size; fetchTransactions(1); }"
        >
          <template #created_at="{ row }">
            <span class="text-xs text-[var(--el-text-color-secondary)] font-mono">
              {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
            </span>
          </template>

          <template #currency="{ row }">
            <el-tag :type="row.currency === 'star' ? 'warning' : 'primary'" size="small">
              {{ row.currency === 'star' ? '星元' : '月华' }}
            </el-tag>
          </template>

          <template #amount="{ row }">
            <span class="font-mono font-bold" :class="row.amount >= 0 ? 'text-emerald-500' : 'text-rose-500'">
              {{ row.amount >= 0 ? `+${row.amount}` : row.amount }}
            </span>
          </template>
        </DataTable>
      </div>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
import { type ICUserItem, type IWalletTransactionItem, getWalletTransactions } from '@/api/cUser';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { ElMessage } from 'element-plus';
import { ref } from 'vue';

const emit = defineEmits<(e: 'adjust', user: ICUserItem) => void>();

const visible = ref(false);
const user = ref<ICUserItem | null>(null);

const loadingTx = ref(false);
const transactions = ref<IWalletTransactionItem[]>([]);
const txTotal = ref(0);
const txPage = ref(1);
const txSize = ref(10);
const txCurrency = ref('');

const txColumns: IColumnConfig[] = [
  { field: 'created_at', title: '发生时间', width: 160, align: 'center', slot: 'created_at' },
  { field: 'currency', title: '币种', width: 80, align: 'center', slot: 'currency' },
  {
    field: 'amount',
    title: '变动数值',
    width: 110,
    align: 'right',
    headerAlign: 'right',
    slot: 'amount',
  },
  { field: 'balance_after', title: '变动后余额', width: 110, align: 'right', headerAlign: 'right' },
  { field: 'description', title: '流水说明', minWidth: 140, showOverflow: true },
];

function open(target: ICUserItem) {
  user.value = target;
  visible.value = true;
  txPage.value = 1;
  txCurrency.value = '';
  fetchTransactions(1);
}

async function fetchTransactions(page = 1) {
  if (!user.value) return;
  txPage.value = page;
  try {
    loadingTx.value = true;
    const res = await getWalletTransactions(user.value.id, {
      page: txPage.value,
      size: txSize.value,
      currency: txCurrency.value || undefined,
    });
    transactions.value = res.list || [];
    txTotal.value = res.total || 0;
  } catch (err: any) {
    console.error('[UserDetailDrawer] fetchTransactions error:', err);
    ElMessage.error(err?.message || '获取资金流水记录失败');
    transactions.value = [];
    txTotal.value = 0;
  } finally {
    loadingTx.value = false;
  }
}

function handleOpenAdjust() {
  if (user.value) {
    emit('adjust', user.value);
  }
}

function updateBalance(currency: string, newBalance: number) {
  if (!user.value) return;
  if (currency === 'star') {
    user.value.star_coins = newBalance;
  } else {
    user.value.moon_gems = newBalance;
  }
  fetchTransactions(1);
}

defineExpose({
  open,
  updateBalance,
});
</script>
