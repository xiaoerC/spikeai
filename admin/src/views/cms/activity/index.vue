<template>
  <div class="flex flex-col gap-4 p-4 w-full h-full box-border">
    <!-- 1. 顶部检索与操作栏 -->
    <div class="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-sm">
      <el-form :inline="true" :model="query" class="flex flex-wrap items-center gap-3 !m-0">
        <el-form-item label="活动搜索" class="!m-0">
          <el-input
            v-model="query.keyword"
            placeholder="搜索活动标题 / 奖励描述"
            clearable
            class="!w-64"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="活动状态" class="!m-0">
          <el-select
            v-model="query.status"
            placeholder="全部状态"
            clearable
            class="!w-36"
          >
            <el-option label="进行中 (active)" value="active" />
            <el-option label="已结束 (ended)" value="ended" />
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

      <div class="flex items-center gap-3">
        <el-button type="success" @click="handleCreate">
          <el-icon class="mr-1"><Plus /></el-icon> 创建运营活动
        </el-button>
      </div>
    </div>

    <!-- 2. 主体表格 -->
    <DataTable
      :columns="columns"
      :table-data="{ list: tableData, total }"
      :table-query="query"
      :loading="loading"
      table-title="运营活动列表"
      class="w-full flex-1 min-h-0"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        @on-refresh="loadData"
      >
        <template #title="{ row }">
          <div class="flex items-center gap-2 py-1">
            <el-tag size="small" type="primary" effect="plain">{{ row.tag }}</el-tag>
            <span class="font-bold text-xs text-[var(--el-text-color-primary)] truncate" :title="row.title">
              {{ row.title }}
            </span>
          </div>
        </template>

        <template #reward="{ row }">
          <span class="text-xs font-bold text-amber-500">
            {{ row.reward_text }}
          </span>
        </template>

        <template #date_range="{ row }">
          <span class="text-xs font-mono text-[var(--el-text-color-secondary)]">
            {{ row.date_range }}
          </span>
        </template>

        <template #status="{ row }">
          <el-tag
            size="small"
            :type="row.status === 'active' ? 'success' : 'info'"
            effect="dark"
          >
            {{ row.status === 'active' ? '进行中' : '已结束' }}
          </el-tag>
        </template>

        <template #rules="{ row }">
          <el-tag size="small" type="info" effect="plain">
            共 {{ row.rules?.length || 0 }} 条
          </el-tag>
        </template>

        <template #created_at="{ row }">
          <span class="text-xs text-[var(--el-text-color-secondary)] font-mono">
            {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
          </span>
        </template>

        <template #actions="{ row }">
          <div class="flex items-center justify-center gap-2">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button
              :type="row.status === 'active' ? 'warning' : 'success'"
              link
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 'active' ? '结束' : '重启' }}
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </div>
        </template>
      </DataTable>

    <!-- 3. 活动发布/编辑抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="isEdit ? '编辑运营活动' : '发布全新运营活动'"
      size="560px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="flex flex-col gap-3 p-2"
      >
        <el-form-item label="活动标题" prop="title">
          <el-input v-model="form.title" placeholder="如：首届角色卡创作者扶持计划" maxlength="128" show-word-limit />
        </el-form-item>

        <div class="grid grid-cols-2 gap-3">
          <el-form-item label="活动标签" prop="tag">
            <el-input v-model="form.tag" placeholder="如：招募、征集、福利" />
          </el-form-item>

          <el-form-item label="奖励描述" prop="reward_text">
            <el-input v-model="form.reward_text" placeholder="如：瓜分 100,000 月华" />
          </el-form-item>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <el-form-item label="时间范围" prop="date_range">
            <el-input v-model="form.date_range" placeholder="如：长期有效 / 2026.07.01-08.31" />
          </el-form-item>

          <el-form-item label="初始状态" prop="status">
            <el-radio-group v-model="form.status">
              <el-radio-button value="active">进行中</el-radio-button>
              <el-radio-button value="ended">已结束</el-radio-button>
            </el-radio-group>
          </el-form-item>
        </div>

        <el-form-item label="活动规则条目 (可逐条增减)">
          <div class="flex flex-col gap-2 w-full">
            <div
              v-for="(_, index) in form.rules"
              :key="index"
              class="flex items-center gap-2"
            >
              <el-input
                v-model="form.rules[index]"
                placeholder="请输入规则要求内容..."
              />
              <el-button
                type="danger"
                circle
                size="small"
                @click="removeRule(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" plain size="small" @click="addRule">
              <el-icon class="mr-1"><Plus /></el-icon> 添加一条规则
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex items-center justify-end gap-3">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">
            保存活动
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import {
  type IActivityQuery,
  type IAdminActivityForm,
  type IAdminActivityItem,
  createActivity,
  deleteActivity,
  getActivityList,
  updateActivity,
} from '@/api/cms';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus';
import { onMounted, reactive, ref } from 'vue';

const loading = ref(false);
const submitting = ref(false);
const tableData = ref<IAdminActivityItem[]>([]);
const total = ref(0);

const drawerVisible = ref(false);
const isEdit = ref(false);
const currentId = ref<string>('');
const formRef = ref<FormInstance>();

const query = reactive<IActivityQuery>({
  page: 1,
  size: 10,
  keyword: '',
  status: '',
});

const columns: IColumnConfig[] = [
  { field: 'title', title: '活动标题', minWidth: 220, slot: 'title' },
  { field: 'reward_text', title: '活动奖励', minWidth: 160, slot: 'reward' },
  { field: 'date_range', title: '活动时间范围', width: 180, align: 'center', slot: 'date_range' },
  { field: 'status', title: '状态', width: 110, align: 'center', slot: 'status' },
  { field: 'rules', title: '规则条目', width: 110, align: 'center', slot: 'rules' },
  { field: 'created_at', title: '发布时间', width: 170, align: 'center', slot: 'created_at' },
  { field: 'actions', title: '操作', width: 180, fixed: 'right', align: 'center', slot: 'actions' },
];

const form = reactive<IAdminActivityForm>({
  title: '',
  tag: '福利',
  reward_text: '丰厚月华',
  date_range: '长期有效',
  status: 'active',
  rules: ['提交原创角色卡即可参与'],
});

const rules = {
  title: [{ required: true, message: '请输入活动标题', trigger: 'blur' }],
  tag: [{ required: true, message: '请输入活动标签', trigger: 'blur' }],
  reward_text: [{ required: true, message: '请输入奖励描述', trigger: 'blur' }],
  date_range: [{ required: true, message: '请输入活动时间范围', trigger: 'blur' }],
};

function addRule() {
  form.rules.push('');
}

function removeRule(index: number) {
  form.rules.splice(index, 1);
}

async function loadData() {
  try {
    loading.value = true;
    const res = await getActivityList(query);
    tableData.value = res.list || [];
    total.value = res.total || 0;
  } catch (error: any) {
    ElMessage.error(error?.message || '获取活动列表失败');
  } finally {
    loading.value = false;
  }
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

function handleCreate() {
  isEdit.value = false;
  currentId.value = '';
  form.title = '';
  form.tag = '福利';
  form.reward_text = '丰厚月华';
  form.date_range = '长期有效';
  form.status = 'active';
  form.rules = ['提交原创角色卡即可参与'];
  drawerVisible.value = true;
}

function handleEdit(row: any) {
  const item = row as IAdminActivityItem;
  isEdit.value = true;
  currentId.value = item.id;
  form.title = item.title;
  form.tag = item.tag;
  form.reward_text = item.reward_text;
  form.date_range = item.date_range;
  form.status = item.status;
  form.rules = item.rules ? [...item.rules] : [];
  drawerVisible.value = true;
}

async function handleToggleStatus(row: any) {
  const item = row as IAdminActivityItem;
  const newStatus = item.status === 'active' ? 'ended' : 'active';
  try {
    await updateActivity(item.id, { status: newStatus });
    ElMessage.success(`活动已切换为「${newStatus === 'active' ? '进行中' : '已结束'}」`);
    loadData();
  } catch (error: any) {
    ElMessage.error(error?.message || '切换活动状态失败');
  }
}

async function submitForm() {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    try {
      submitting.value = true;
      const cleanRules = form.rules.filter((r) => r.trim().length > 0);
      const payload = { ...form, rules: cleanRules };
      if (isEdit.value) {
        await updateActivity(currentId.value, payload);
        ElMessage.success('运营活动已更新');
      } else {
        await createActivity(payload);
        ElMessage.success('运营活动已创建上线');
      }
      drawerVisible.value = false;
      loadData();
    } catch (error: any) {
      ElMessage.error(error?.message || '保存运营活动失败');
    } finally {
      submitting.value = false;
    }
  });
}

async function handleDelete(row: any) {
  const item = row as IAdminActivityItem;
  try {
    await ElMessageBox.confirm(`确定要删除运营活动《${item.title}》吗？`, '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    });
    loading.value = true;
    await deleteActivity(item.id);
    ElMessage.success('活动已删除');
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
