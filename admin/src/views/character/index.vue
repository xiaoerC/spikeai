<template>
  <div class="flex flex-col gap-4 p-4 w-full h-full box-border">
    <!-- 1. 顶部检索与过滤面板 -->
    <div class="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-sm">
      <el-form :inline="true" :model="query" class="flex flex-wrap items-center gap-3 !m-0">
        <!-- 模式切换：常规角色管理 vs 回收站 -->
        <el-radio-group v-model="activeTab" size="default" class="mr-2" @change="handleTabChange">
          <el-radio-button value="active">
            <span class="flex items-center gap-1.5">
              <el-icon><Grid /></el-icon>
              常规角色池
            </span>
          </el-radio-button>
          <el-radio-button value="recycle">
            <span class="flex items-center gap-1.5 text-rose-500">
              <el-icon><Delete /></el-icon>
              回收站
            </span>
          </el-radio-button>
        </el-radio-group>

        <el-form-item label="角色检索" class="!m-0">
          <el-input
            v-model="query.keyword"
            placeholder="搜索角色名 / 创作者"
            clearable
            class="!w-52"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="内容大类" class="!m-0">
          <el-select
            v-model="query.category"
            placeholder="全部分类"
            clearable
            class="!w-32"
          >
            <el-option label="剧情故事" value="story" />
            <el-option label="跑团数值" value="rpg" />
            <el-option label="特别限制" value="nsfw" />
          </el-select>
        </el-form-item>

        <!-- 常规模式下支持细分状态筛选 -->
        <el-form-item v-if="activeTab === 'active'" label="发布状态" class="!m-0">
          <el-select
            v-model="query.status"
            placeholder="全部正常状态"
            clearable
            class="!w-36"
          >
            <el-option label="已上架" value="published" />
            <el-option label="私密" value="private" />
            <el-option label="已违规下架" value="banned" />
            <el-option label="草稿" value="draft" />
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

      <!-- 批量操作与统计面板 -->
      <div class="flex items-center gap-3">
        <!-- 常规模式批量移入回收站 -->
        <template v-if="activeTab === 'active'">
          <el-button
            type="danger"
            plain
            :disabled="selectedRows.length === 0"
            @click="handleBatchDelete"
          >
            <el-icon class="mr-1"><Delete /></el-icon>
            批量移入回收站 ({{ selectedRows.length }})
          </el-button>
        </template>

        <!-- 回收站模式批量彻底粉碎 -->
        <template v-else>
          <el-button
            type="danger"
            :disabled="selectedRows.length === 0"
            @click="handleBatchDestroy"
          >
            <el-icon class="mr-1"><DeleteFilled /></el-icon>
            批量彻底粉碎 ({{ selectedRows.length }})
          </el-button>
        </template>

        <div class="flex items-center gap-1.5 text-sm font-medium text-slate-700 dark:text-zinc-200 pl-3 border-l border-slate-200 dark:border-zinc-700">
          <span>{{ activeTab === 'active' ? '正常卡片总量:' : '回收站卡片数:' }}</span>
          <strong :class="activeTab === 'active' ? 'text-[var(--el-color-primary)]' : 'text-rose-500'" class="font-bold text-base font-mono">
            {{ total }}
          </strong>
          <span class="text-slate-500 dark:text-zinc-400 text-xs">部</span>
        </div>
      </div>
    </div>

    <!-- 2. 主体角色表格卡片 -->
    <DataTable
      ref="tableRef"
      :columns="columns"
      :table-data="{ list: tableData, total }"
      :table-query="query"
      :loading="loading"
      :show-checkbox="true"
      :show-index="false"
      class="w-full"
      @selection-change="handleSelectionChange"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
      @on-refresh="loadData"
    >
        <!-- 角色卡基本信息列 -->
        <template #basic_info="{ row }">
          <div class="flex items-center gap-3.5 py-2">
            <el-image
              :src="row.avatar_url"
              fit="cover"
              class="w-12 h-12 rounded-xl flex-shrink-0 border border-[var(--el-border-color-lighter)] shadow-xs"
            >
              <template #error>
                <div class="w-full h-full flex items-center justify-center bg-gray-200 text-gray-500 font-bold text-sm">
                  {{ row.name.slice(0, 1) }}
                </div>
              </template>
            </el-image>

            <div class="flex flex-col leading-snug flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="font-bold text-sm text-[var(--el-text-color-primary)] truncate" :title="row.name">
                  {{ row.name }}
                </span>
                <el-tag size="small" type="primary" effect="plain" class="!text-[11px] !px-1.5 shrink-0">
                  {{ row.category === 'story' ? '剧情故事' : row.category === 'rpg' ? '跑团数值' : '常规角色' }}
                </el-tag>
              </div>
              <p class="text-xs text-[var(--el-text-color-secondary)] line-clamp-1 mt-1" :title="row.description">
                {{ row.description || '暂无详细设定描述' }}
              </p>
              <div v-if="row.tags && row.tags.length" class="flex items-center gap-1.5 mt-1.5 flex-wrap">
                <el-tag
                  v-for="t in row.tags.slice(0, 4)"
                  :key="t"
                  size="small"
                  type="info"
                  class="!text-[11px] !px-1.5"
                >
                  {{ t }}
                </el-tag>
                <span v-if="row.tags.length > 4" class="text-[11px] text-slate-400">
                  +{{ row.tags.length - 4 }}
                </span>
              </div>
            </div>
          </div>
        </template>

        <!-- 创作者列 -->
        <template #author="{ row }">
          <div class="flex items-center gap-2.5 py-2 min-w-0">
            <div class="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-xs shrink-0 border border-blue-200/60 dark:border-blue-800/60 shadow-2xs">
              {{ (row.author_name || 'U').slice(0, 1).toUpperCase() }}
            </div>
            <div class="flex flex-col leading-snug min-w-0">
              <span class="font-medium text-xs text-[var(--el-text-color-primary)] truncate" :title="row.author_name">
                {{ row.author_name }}
              </span>
              <span class="text-[11px] text-[var(--el-text-color-secondary)] font-mono truncate" :title="row.author_email">
                {{ row.author_email || '未绑定邮箱' }}
              </span>
            </div>
          </div>
        </template>

        <!-- 设定体量列 -->
        <template #capacity="{ row }">
          <div class="flex flex-col gap-1 py-1 text-xs">
            <div class="flex items-center gap-1.5">
              <span class="text-[var(--el-text-color-placeholder)]">设定规模:</span>
              <span class="font-semibold text-[var(--el-text-color-primary)] font-mono">
                {{ (row.settings_word_count || 0).toLocaleString() }} 字
              </span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="text-[var(--el-text-color-placeholder)]">世界书:</span>
              <span class="font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-1.5 py-0.5 rounded text-[11px]">
                {{ row.worldbook_entry_count ?? 0 }} 条
              </span>
            </div>
            <div class="flex items-center gap-1.5 text-[11px] text-[var(--el-text-color-secondary)]">
              <span class="text-[var(--el-text-color-placeholder)]">版本:</span>
              <span class="font-mono">v{{ row.version || '1.0.0' }}</span>
            </div>
          </div>
        </template>

        <!-- 互动数据列 -->
        <template #stats="{ row }">
          <div class="flex flex-col gap-1 py-1 text-xs">
            <div class="flex items-center gap-1.5">
              <span class="text-[var(--el-text-color-placeholder)]">综合评分:</span>
              <span class="font-bold text-amber-500">★ {{ (row.rating ?? 5.0).toFixed(1) }}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="text-[var(--el-text-color-placeholder)]">会话场次:</span>
              <span class="text-[var(--el-color-primary)] font-semibold font-mono">{{ row.chat_count ?? 0 }} 场</span>
            </div>
            <div class="flex items-center gap-2 text-[11px] text-[var(--el-text-color-secondary)]">
              <span>获赞 {{ row.like_count ?? 0 }}</span>
              <span>·</span>
              <span>收藏 {{ row.favorite_count ?? 0 }}</span>
            </div>
          </div>
        </template>

        <!-- 状态列 -->
        <template #status="{ row }">
          <el-tag
            :type="
              row.status === 'published'
                ? 'success'
                : row.status === 'pending_review'
                ? 'warning'
                : row.status === 'rejected' || row.status === 'deleted'
                ? 'danger'
                : 'info'
            "
            size="small"
            effect="light"
          >
            {{
              row.status === 'published'
                ? '已上架'
                : row.status === 'pending_review'
                ? '待审核'
                : row.status === 'unlisted'
                ? '已下架'
                : row.status === 'rejected'
                ? '审核拒绝'
                : '已软删除'
            }}
          </el-tag>
        </template>

        <!-- 更新时间列 -->
        <template #updated_at="{ row }">
          <span class="text-xs text-[var(--el-text-color-secondary)] font-mono">
            {{ row.updated_at?.slice(0, 19).replace('T', ' ') }}
          </span>
        </template>

        <!-- 差异化操作列 -->
        <template #actions="{ row }">
          <!-- 常规列表操作 -->
          <div v-if="activeTab === 'active'" class="flex items-center justify-center gap-1.5">
            <el-button
              type="primary"
              link
              size="small"
              @click="openDetail(row)"
            >
              档案详情
            </el-button>
            <el-button
              :type="row.status === 'published' ? 'warning' : 'success'"
              link
              size="small"
              @click="openAudit(row)"
            >
              审核/处置
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              :disabled="row.status === 'published'"
              :title="row.status === 'published' ? '已上架卡片需先下架才可删除' : '软删除移入回收站'"
              @click="handleSingleDelete(row)"
            >
              删除
            </el-button>
          </div>

          <!-- 回收站操作 -->
          <div v-else class="flex items-center justify-center gap-1.5">
            <el-button
              type="primary"
              link
              size="small"
              @click="openDetail(row)"
            >
              档案
            </el-button>
            <el-button
              type="success"
              link
              size="small"
              @click="handleRestore(row)"
            >
              恢复
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              class="!font-bold"
              @click="handleSingleDestroy(row)"
            >
              彻底粉碎
            </el-button>
          </div>
        </template>
      </DataTable>

    <!-- 角色卡全景档案抽屉 -->
    <CharacterDetailDrawer ref="detailDrawerRef" @audit="openAudit" />

    <!-- 角色卡审核与状态处置弹窗 -->
    <CharacterAuditDialog ref="auditDialogRef" @success="loadData" />
  </div>
</template>

<script lang="ts" setup>
import {
  type IAdminCharacterItem,
  type ICharacterQuery,
  batchDeleteCharacters,
  batchDestroyCharacters,
  deleteCharacter,
  destroyCharacter,
  getCharacterList,
  restoreCharacter,
} from '@/api/character';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { onMounted, reactive, ref } from 'vue';
import CharacterAuditDialog from './components/CharacterAuditDialog.vue';
import CharacterDetailDrawer from './components/CharacterDetailDrawer.vue';

const loading = ref(false);
const tableData = ref<IAdminCharacterItem[]>([]);
const total = ref(0);
const selectedRows = ref<IAdminCharacterItem[]>([]);
const tableRef = ref<any>();

// 当前激活的视图: 'active' (正常角色池) / 'recycle' (回收站)
const activeTab = ref<'active' | 'recycle'>('active');

const detailDrawerRef = ref<any>();
const auditDialogRef = ref<any>();

const query = reactive<ICharacterQuery>({
  page: 1,
  size: 10,
  keyword: '',
  category: '',
  status: '',
});

const columns: IColumnConfig[] = [
  { field: 'name', title: '角色卡基本信息', minWidth: 360, slot: 'basic_info' },
  { field: 'author', title: '创作者', minWidth: 200, slot: 'author' },
  { field: 'capacity', title: '设定体量', minWidth: 170, align: 'left', slot: 'capacity' },
  { field: 'stats', title: '互动数据', minWidth: 190, slot: 'stats' },
  { field: 'status', title: '状态', width: 100, align: 'center', slot: 'status' },
  { field: 'updated_at', title: '更新时间', width: 160, align: 'center', slot: 'updated_at' },
  { field: 'actions', title: '操作', width: 200, fixed: 'right', align: 'center', slot: 'actions' },
];

async function loadData() {
  try {
    loading.value = true;
    const params: ICharacterQuery = {
      page: query.page,
      size: query.size,
      keyword: query.keyword || undefined,
      category: query.category || undefined,
      status: activeTab.value === 'recycle' ? 'deleted' : query.status || undefined,
    };
    const res = await getCharacterList(params);
    tableData.value = res.list || [];
    total.value = res.total || 0;
    selectedRows.value = [];
    tableRef.value?.clearCheckboxRow();
  } catch (error: any) {
    ElMessage.error(error?.message || '获取角色卡列表失败');
  } finally {
    loading.value = false;
  }
}

function handleTabChange() {
  selectedRows.value = [];
  tableRef.value?.clearCheckboxRow();
  query.page = 1;
  query.status = '';
  loadData();
}

function handleSearch() {
  query.page = 1;
  loadData();
}

function handleReset() {
  query.page = 1;
  query.keyword = '';
  query.category = '';
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

function handleSelectionChange(rows: any[]) {
  selectedRows.value = rows;
}

// 单条移入回收站 (软删除)
async function handleSingleDelete(row: any) {
  if (row.status === 'published') {
    ElMessage.warning('已上架角色卡禁止直接删除，请先下架！');
    return;
  }
  try {
    await ElMessageBox.confirm(
      `确定将已下架的角色卡《${row.name}》移入回收站吗？`,
      '移入回收站确认',
      {
        confirmButtonText: '确定移入',
        cancelButtonText: '取消',
        type: 'warning',
      },
    );
    loading.value = true;
    await deleteCharacter(row.id);
    ElMessage.success(`角色卡《${row.name}》已移入回收站`);
    loadData();
  } catch {
    // 取消
  } finally {
    loading.value = false;
  }
}

// 批量移入回收站 (批量软删除)
async function handleBatchDelete() {
  if (selectedRows.value.length === 0) return;

  const publishedCards = selectedRows.value.filter((r) => r.status === 'published');
  if (publishedCards.length > 0) {
    ElMessage.warning(
      `所选包含【已上架】角色卡（如《${publishedCards[0].name}》），必须先下架方可删除！`,
    );
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定将选中的 ${selectedRows.value.length} 部已下架角色卡批量移入回收站吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定移入',
        cancelButtonText: '取消',
        type: 'warning',
      },
    );
    loading.value = true;
    const ids = selectedRows.value.map((r) => r.id);
    const res = await batchDeleteCharacters(ids);
    ElMessage.success(res.message || '批量删除成功');
    loadData();
  } catch {
    // 取消
  } finally {
    loading.value = false;
  }
}

// 从回收站恢复
async function handleRestore(row: any) {
  try {
    loading.value = true;
    await restoreCharacter(row.id);
    ElMessage.success(`角色卡《${row.name}》已恢复为下架待审状态`);
    loadData();
  } catch (error: any) {
    ElMessage.error(error?.message || '恢复失败');
  } finally {
    loading.value = false;
  }
}

// 回收站单条彻底粉碎 (物理删除)
async function handleSingleDestroy(row: any) {
  try {
    await ElMessageBox.confirm(
      `⚠️ 极其危险：彻底粉碎将从数据库中永久物理清除角色卡《${row.name}》及其全部关联数据，此操作不可撤销！确定彻底粉碎吗？`,
      '彻底物理粉碎警告',
      {
        confirmButtonText: '确定彻底粉碎',
        cancelButtonText: '取消',
        type: 'error',
      },
    );
    loading.value = true;
    await destroyCharacter(row.id);
    ElMessage.success(`角色卡《${row.name}》已被彻底物理粉碎`);
    loadData();
  } catch {
    // 取消
  } finally {
    loading.value = false;
  }
}

// 回收站批量彻底粉碎
async function handleBatchDestroy() {
  if (selectedRows.value.length === 0) return;
  try {
    await ElMessageBox.confirm(
      `⚠️ 极其危险：即将永久物理清除选中的 ${selectedRows.value.length} 部角色卡！此操作完全不可逆，确定继续执行吗？`,
      '批量彻底物理粉碎警告',
      {
        confirmButtonText: '确定批量粉碎',
        cancelButtonText: '取消',
        type: 'error',
      },
    );
    loading.value = true;
    const ids = selectedRows.value.map((r) => r.id);
    const res = await batchDestroyCharacters(ids);
    ElMessage.success(res.message || '批量粉碎成功');
    loadData();
  } catch {
    // 取消
  } finally {
    loading.value = false;
  }
}

function openDetail(row: any) {
  detailDrawerRef.value?.open(row as IAdminCharacterItem);
}

function openAudit(row: any) {
  auditDialogRef.value?.open(row as IAdminCharacterItem);
}

onMounted(() => {
  loadData();
});
</script>
