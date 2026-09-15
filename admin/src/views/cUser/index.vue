<template>
  <div class="p-4 w-full h-full box-border">
    <DataTable
      :columns="columns"
      :table-data="{ list: tableData, total }"
      :table-query="query"
      :loading="loading"
      class="w-full"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
      @on-refresh="loadData"
    >
      <!-- 顶部自定义筛选工具栏 -->
      <template #filter>
        <div class="flex flex-wrap items-center justify-between gap-4">
          <el-form :inline="true" :model="query" class="flex flex-wrap items-center gap-3 !m-0">
            <el-form-item label="用户检索" class="!m-0">
              <el-input
                v-model="query.keyword"
                placeholder="搜索用户名 / 邮箱"
                clearable
                class="!w-56"
                @keyup.enter="handleSearch"
              />
            </el-form-item>

            <el-form-item label="账号状态" class="!m-0">
              <el-select
                v-model="query.status"
                placeholder="全部状态"
                clearable
                class="!w-32"
              >
                <el-option label="正常" value="active" />
                <el-option label="已封禁" value="banned" />
                <el-option label="已冻结" value="suspended" />
              </el-select>
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
            <span>全站注册 C 端用户:</span>
            <strong class="text-[var(--el-color-primary)] font-bold text-base font-mono">{{ total }}</strong>
            <span class="text-slate-500 dark:text-zinc-400 text-xs">人</span>
          </div>
        </div>
      </template>

      <!-- 用户画像列 -->
      <template #profile="{ row }">
        <div class="flex items-center gap-3 py-1">
          <el-avatar :size="36" :src="row.avatar_url">
            {{ row.username.slice(0, 1).toUpperCase() }}
          </el-avatar>
          <div class="flex flex-col leading-snug">
            <span class="font-medium text-sm text-[var(--el-text-color-primary)]">
              {{ row.username }}
            </span>
            <span class="text-xs text-[var(--el-text-color-secondary)]">
              {{ row.email }}
            </span>
          </div>
        </div>
      </template>

      <!-- 专属邀请码列 -->
      <template #invite_code="{ row }">
        <code class="px-2 py-0.5 rounded bg-[var(--el-fill-color-light)] text-xs font-mono">
          {{ row.invite_code }}
        </code>
      </template>

      <!-- 等级成就列 -->
      <template #level="{ row }">
        <div class="flex flex-col gap-1 text-xs">
          <div class="flex items-center gap-2">
            <el-tag size="small" type="warning" effect="plain">VIP {{ row.vip_level }}</el-tag>
            <span class="text-[var(--el-text-color-secondary)]">玩家 Lv.{{ row.player_level }}</span>
          </div>
          <span class="text-[var(--el-text-color-placeholder)]">创作者 Lv.{{ row.creator_level }}</span>
        </div>
      </template>

      <!-- 资产储备列 -->
      <template #assets="{ row }">
        <div class="flex flex-col gap-1 text-xs">
          <div class="flex items-center gap-1 font-semibold text-amber-500">
            <span>星元:</span>
            <span>{{ row.star_coins }} ★</span>
          </div>
          <div class="flex items-center gap-1 font-semibold text-cyan-500">
            <span>月华:</span>
            <span>{{ row.moon_gems }} 🌙</span>
          </div>
        </div>
      </template>

      <!-- 生态数据列 -->
      <template #eco="{ row }">
        <div class="flex flex-col text-xs text-[var(--el-text-color-secondary)]">
          <span>角色: {{ row.character_count }} 个</span>
          <span>会话: {{ row.chat_session_count }} 场</span>
        </div>
      </template>

      <!-- 账号状态列 -->
      <template #status="{ row }">
        <el-tag
          :type="row.status === 'active' ? 'success' : 'danger'"
          size="small"
          effect="light"
        >
          {{ row.status === 'active' ? '正常' : row.status === 'banned' ? '已封禁' : '已冻结' }}
        </el-tag>
      </template>

      <!-- 注册时间列 -->
      <template #created_at="{ row }">
        <span class="text-xs text-[var(--el-text-color-secondary)] font-mono">
          {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
        </span>
      </template>

      <!-- 操作列 -->
      <template #actions="{ row }">
        <div class="flex items-center justify-center gap-2">
          <el-button
            type="primary"
            link
            size="small"
            @click="openDetail(row)"
          >
            详情/流水
          </el-button>
          <el-button
            type="warning"
            link
            size="small"
            @click="openAdjust(row)"
          >
            调账
          </el-button>
          <el-button
            :type="row.status === 'active' ? 'danger' : 'success'"
            link
            size="small"
            @click="toggleStatus(row)"
          >
            {{ row.status === 'active' ? '封禁' : '解冻' }}
          </el-button>
        </div>
      </template>
    </DataTable>

    <!-- 用户画像与流水抽屉 -->
    <UserDetailDrawer ref="detailDrawerRef" @adjust="openAdjust" />

    <!-- 资产调账弹窗 -->
    <WalletAdjustDialog ref="adjustDialogRef" @success="handleAdjustSuccess" />
  </div>
</template>

<script lang="ts" setup>
import { type ICUserItem, type ICUserQuery, getCUserList, updateCUserStatus } from '@/api/cUser';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { onMounted, reactive, ref } from 'vue';
import UserDetailDrawer from './components/UserDetailDrawer.vue';
import WalletAdjustDialog from './components/WalletAdjustDialog.vue';

const loading = ref(false);
const tableData = ref<ICUserItem[]>([]);
const total = ref(0);

const detailDrawerRef = ref<any>();
const adjustDialogRef = ref<any>();

const query = reactive<ICUserQuery>({
  page: 1,
  size: 10,
  keyword: '',
  status: '',
});

const columns: IColumnConfig[] = [
  { field: 'username', title: '用户画像', minWidth: 200, slot: 'profile' },
  { field: 'invite_code', title: '专属邀请码', width: 130, align: 'center', slot: 'invite_code' },
  { field: 'vip_level', title: '等级成就', width: 160, slot: 'level' },
  { field: 'star_coins', title: '资产储备', width: 180, slot: 'assets' },
  { field: 'character_count', title: '生态数据', width: 130, align: 'center', slot: 'eco' },
  { field: 'status', title: '账号状态', width: 100, align: 'center', slot: 'status' },
  { field: 'created_at', title: '注册时间', width: 170, align: 'center', slot: 'created_at' },
  { field: 'actions', title: '操作', width: 200, fixed: 'right', align: 'center', slot: 'actions' },
];

async function loadData() {
  try {
    loading.value = true;
    const res = await getCUserList(query);
    tableData.value = res.list || [];
    total.value = res.total || 0;
  } catch (error: any) {
    ElMessage.error(error?.message || '获取用户列表失败');
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
  query.status = '';
  loadData();
}

function handlePageChange(page: number) {
  query.page = page;
  loadData();
}

function handleSizeChange(size: number) {
  query.size = size;
  query.page = 1;
  loadData();
}

function openDetail(row: any) {
  detailDrawerRef.value?.open(row as ICUserItem);
}

function openAdjust(row: any) {
  adjustDialogRef.value?.open(row as ICUserItem);
}

function handleAdjustSuccess(data: { userId: string; currency: string; balanceAfter: number }) {
  loadData();
  detailDrawerRef.value?.updateBalance(data.currency, data.balanceAfter);
}

async function toggleStatus(row: any) {
  const user = row as ICUserItem;
  const isBanning = user.status === 'active';
  const actionText = isBanning ? '封禁' : '解冻';

  try {
    const { value: reason } = await ElMessageBox.prompt(
      `请输入${actionText}该账号的原因说明：`,
      `确认${actionText}用户 [${user.username}]`,
      {
        confirmButtonText: `确认${actionText}`,
        cancelButtonText: '取消',
        inputPattern: /^.+$/,
        inputErrorMessage: '请填写原因说明',
      },
    );

    await updateCUserStatus(user.id, {
      status: isBanning ? 'banned' : 'active',
      reason,
    });

    ElMessage.success(`用户已成功${actionText}`);
    loadData();
  } catch (_cancel) {
    // 取消操作
  }
}

onMounted(() => {
  loadData();
});
</script>
