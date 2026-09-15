<template>
  <div class="flex flex-col gap-4 p-4 w-full h-full box-border">
    <!-- 1. 顶部检索面板 -->
    <div class="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-sm">
      <el-form :inline="true" :model="query" class="flex flex-wrap items-center gap-3 !m-0">
        <el-form-item label="会话检索" class="!m-0">
          <el-input
            v-model="query.keyword"
            placeholder="搜索用户名 / 邮箱 / 角色 / 备注"
            clearable
            class="!w-64"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="推理模型" class="!m-0">
          <el-select
            v-model="query.model_id"
            placeholder="全部模型"
            clearable
            class="!w-48"
          >
            <el-option label="glm-5.2-o1 (旗舰思维链)" value="glm-5.2-o1" />
            <el-option label="claude-3-5-sonnet" value="claude-3-5-sonnet" />
            <el-option label="gpt-4o" value="gpt-4o" />
            <el-option label="deepseek-r1" value="deepseek-r1" />
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
        <span>全站 AI 对话会话总数:</span>
        <strong class="text-[var(--el-color-primary)] font-bold text-base font-mono">{{ total }}</strong>
        <span class="text-slate-500 dark:text-zinc-400 text-xs">场</span>
      </div>
    </div>
    <!-- 2. 主体会话表格 -->
    <DataTable
      :columns="columns"
      :table-data="{ list: tableData, total }"
      :table-query="query"
      :loading="loading"
      table-title="全站 AI 对话会话列表"
      class="w-full flex-1 min-h-0"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
      @on-refresh="loadData"
    >
      <template #user="{ row }">
        <div class="flex items-center gap-2.5 py-1">
          <el-avatar :size="36" :src="row.user_avatar" class="flex-shrink-0">
            {{ row.user_name.slice(0, 1) }}
          </el-avatar>
          <div class="flex flex-col leading-snug truncate">
            <span class="font-bold text-xs text-[var(--el-text-color-primary)] truncate">{{ row.user_name }}</span>
            <span class="text-[11px] text-[var(--el-text-color-secondary)] truncate" :title="row.user_email">{{ row.user_email }}</span>
          </div>
        </div>
      </template>

      <template #character="{ row }">
        <div class="flex items-center gap-2.5 py-1">
          <el-avatar :size="36" shape="square" :src="row.character_avatar" class="rounded-lg flex-shrink-0 border border-[var(--el-border-color-lighter)]">
            {{ row.character_name.slice(0, 1) }}
          </el-avatar>
          <div class="flex flex-col leading-snug truncate">
            <span class="font-bold text-xs text-[var(--el-text-color-primary)] truncate">{{ row.character_name }}</span>
            <span class="text-[11px] text-[var(--el-text-color-placeholder)] truncate" :title="row.remark">{{ row.remark }}</span>
          </div>
        </div>
      </template>

      <template #model="{ row }">
        <el-tag size="small" type="primary" effect="plain" class="font-mono">
          {{ row.current_model_id }}
        </el-tag>
      </template>

      <template #messages="{ row }">
        <el-tag size="small" type="primary" effect="plain" class="font-mono font-medium">
          {{ row.message_count }} 轮
        </el-tag>
      </template>

      <template #tokens="{ row }">
        <div class="flex flex-col items-end leading-snug text-xs pr-1">
          <span class="font-bold text-emerald-600 dark:text-emerald-400 font-mono">{{ (row.total_tokens || 0).toLocaleString() }}</span>
          <span class="text-[10px] text-slate-400 dark:text-zinc-500">Tokens</span>
        </div>
      </template>

      <template #mode="{ row }">
        <el-tag size="small" :type="row.mode === 'story' ? 'success' : 'info'" effect="light">
          {{ row.mode === 'story' ? '剧情树' : '聊天室' }}
        </el-tag>
      </template>

      <template #updated_at="{ row }">
        <span class="text-xs text-slate-500 dark:text-zinc-400 font-mono">
          {{ row.updated_at?.slice(0, 19).replace('T', ' ') }}
        </span>
      </template>

      <template #actions="{ row }">
        <div class="flex items-center justify-center gap-2">
          <el-button
            type="primary"
            link
            size="small"
            @click="openTranscript(row)"
          >
            全景回溯
          </el-button>
          <el-button
            type="danger"
            link
            size="small"
            @click="handleDelete(row)"
          >
            清理
          </el-button>
        </div>
      </template>
    </DataTable>

    <!-- 对话历史全景回溯抽屉 -->
    <ChatTranscriptDrawer ref="transcriptDrawerRef" @deleted="loadData" />
  </div>
</template>

<script lang="ts" setup>
import {
  type IAdminChatSessionItem,
  type IChatSessionQuery,
  deleteChatSession,
  getChatSessionList,
} from '@/api/chatOps';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { onMounted, reactive, ref } from 'vue';
import ChatTranscriptDrawer from './components/ChatTranscriptDrawer.vue';

const loading = ref(false);
const tableData = ref<IAdminChatSessionItem[]>([]);
const total = ref(0);

const transcriptDrawerRef = ref<any>();

const query = reactive<IChatSessionQuery>({
  page: 1,
  size: 10,
  keyword: '',
  model_id: '',
});

const columns: IColumnConfig[] = [
  { field: 'user_name', title: '参与用户', minWidth: 180, align: 'left', slot: 'user' },
  {
    field: 'character_name',
    title: '对话目标角色',
    minWidth: 180,
    align: 'left',
    slot: 'character',
  },
  { field: 'current_model_id', title: '推理模型', width: 140, align: 'center', slot: 'model' },
  { field: 'message_count', title: '交互轮数', width: 110, align: 'center', slot: 'messages' },
  {
    field: 'total_tokens',
    title: '累计 Token 消耗',
    width: 150,
    align: 'right',
    headerAlign: 'right',
    slot: 'tokens',
  },
  { field: 'mode', title: '模式', width: 100, align: 'center', slot: 'mode' },
  { field: 'updated_at', title: '最后活跃时间', width: 170, align: 'center', slot: 'updated_at' },
  { field: 'actions', title: '操作', width: 160, fixed: 'right', align: 'center', slot: 'actions' },
];

async function loadData() {
  try {
    loading.value = true;
    const res = await getChatSessionList(query);
    tableData.value = res.list || [];
    total.value = res.total || 0;
  } catch (error: any) {
    ElMessage.error(error?.message || '获取会话列表失败');
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
  query.model_id = '';
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

function openTranscript(row: any) {
  transcriptDrawerRef.value?.open(row as IAdminChatSessionItem);
}

async function handleDelete(row: any) {
  const item = row as IAdminChatSessionItem;
  try {
    await ElMessageBox.confirm(
      `确定要删除该会话（用户：${item.user_name}，角色：${item.character_name}）吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      },
    );
    loading.value = true;
    await deleteChatSession(item.id);
    ElMessage.success('会话已删除');
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
