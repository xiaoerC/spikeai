<template>
  <div class="flex flex-col gap-4 p-4 w-full h-full box-border">
    <!-- 1. 顶部检索与操作栏 -->
    <div class="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-sm">
      <el-form :inline="true" :model="query" class="flex flex-wrap items-center gap-3 !m-0">
        <el-form-item label="公告搜索" class="!m-0">
          <el-input
            v-model="query.keyword"
            placeholder="搜索公告标题 / 摘要"
            clearable
            class="!w-64"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="公告分类" class="!m-0">
          <el-select
            v-model="query.category"
            placeholder="全部分类"
            clearable
            class="!w-40"
          >
            <el-option label="系统公告" value="系统公告" />
            <el-option label="更新日志" value="更新日志" />
            <el-option label="活动公告" value="活动公告" />
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
          <el-icon class="mr-1"><Plus /></el-icon> 发布新公告
        </el-button>
      </div>
    </div>

    <!-- 2. 主体表格 -->
    <DataTable
      :columns="columns"
      :table-data="{ list: tableData, total }"
      :table-query="query"
      :loading="loading"
      table-title="系统公告列表"
      class="w-full flex-1 min-h-0"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        @on-refresh="loadData"
      >
        <template #title="{ row }">
          <div class="flex items-center gap-2 py-1">
            <el-tag
              size="small"
              :type="row.badge_type === 'update' ? 'warning' : row.badge_type === 'event' ? 'success' : 'primary'"
              effect="dark"
            >
              {{ formatBadge(row.badge_type) }}
            </el-tag>
            <span class="font-bold text-xs text-[var(--el-text-color-primary)] truncate" :title="row.title">
              {{ row.title }}
            </span>
          </div>
        </template>

        <template #category="{ row }">
          <el-tag size="small" effect="plain">{{ row.category }}</el-tag>
        </template>

        <template #date_text="{ row }">
          <span class="text-xs font-mono text-[var(--el-text-color-secondary)]">
            {{ row.date_text }}
          </span>
        </template>

        <template #summary="{ row }">
          <span class="text-xs text-[var(--el-text-color-secondary)] line-clamp-2" :title="row.summary">
            {{ row.summary }}
          </span>
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
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </div>
        </template>
      </DataTable>

    <!-- 3. 公告发布/编辑抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="isEdit ? '编辑系统公告' : '发布全站新公告'"
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
        <el-form-item label="公告标题" prop="title">
          <el-input v-model="form.title" placeholder="如：SpikeAI V2.5 纯净架构上线公告" maxlength="128" show-word-limit />
        </el-form-item>

        <div class="grid grid-cols-2 gap-3">
          <el-form-item label="分类" prop="category">
            <el-select v-model="form.category" class="w-full">
              <el-option label="系统公告" value="系统公告" />
              <el-option label="更新日志" value="更新日志" />
              <el-option label="活动公告" value="活动公告" />
            </el-select>
          </el-form-item>

          <el-form-item label="展示日期标签" prop="date_text">
            <el-input v-model="form.date_text" placeholder="如：2026-09-04" />
          </el-form-item>
        </div>

        <el-form-item label="徽章类型" prop="badge_type">
          <el-radio-group v-model="form.badge_type">
            <el-radio-button value="notice">普通重要 (notice)</el-radio-button>
            <el-radio-button value="update">版本更新 (update)</el-radio-button>
            <el-radio-button value="event">活动福利 (event)</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="摘要导语" prop="summary">
          <el-input
            v-model="form.summary"
            type="textarea"
            :rows="3"
            placeholder="输入在列表展示的精简公告摘要..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="详细内容 HTML" prop="content_html">
          <el-input
            v-model="form.content_html"
            type="textarea"
            :rows="6"
            placeholder="支持输入富文本 HTML 标签，如 <p>...</p>"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex items-center justify-end gap-3">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">
            保存发布
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import {
  type IAdminNoticeForm,
  type IAdminNoticeItem,
  type INoticeQuery,
  createNotice,
  deleteNotice,
  getNoticeList,
  updateNotice,
} from '@/api/cms';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus';
import { onMounted, reactive, ref } from 'vue';

const loading = ref(false);
const submitting = ref(false);
const tableData = ref<IAdminNoticeItem[]>([]);
const total = ref(0);

const drawerVisible = ref(false);
const isEdit = ref(false);
const currentId = ref<string>('');
const formRef = ref<FormInstance>();

const query = reactive<INoticeQuery>({
  page: 1,
  size: 10,
  keyword: '',
  category: '',
});

const columns: IColumnConfig[] = [
  { field: 'title', title: '公告标题', minWidth: 220, slot: 'title' },
  { field: 'category', title: '分类', width: 120, align: 'center', slot: 'category' },
  { field: 'date_text', title: '展示日期', width: 130, align: 'center', slot: 'date_text' },
  { field: 'summary', title: '摘要导语', minWidth: 260, slot: 'summary' },
  { field: 'created_at', title: '创建时间', width: 170, align: 'center', slot: 'created_at' },
  { field: 'actions', title: '操作', width: 140, fixed: 'right', align: 'center', slot: 'actions' },
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

const form = reactive<IAdminNoticeForm>({
  title: '',
  category: '系统公告',
  date_text: new Date().toISOString().slice(0, 10),
  badge_type: 'notice',
  summary: '',
  content_html: '',
});

const rules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  date_text: [{ required: true, message: '请输入展示日期', trigger: 'blur' }],
  summary: [{ required: true, message: '请输入摘要导语', trigger: 'blur' }],
};

function formatBadge(type: string) {
  const map: Record<string, string> = {
    notice: '重要',
    update: '更新',
    event: '活动',
  };
  return map[type] || type;
}

async function loadData() {
  try {
    loading.value = true;
    const res = await getNoticeList(query);
    tableData.value = res.list || [];
    total.value = res.total || 0;
  } catch (error: any) {
    ElMessage.error(error?.message || '获取公告列表失败');
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
  query.category = '';
  loadData();
}

function handleCreate() {
  isEdit.value = false;
  currentId.value = '';
  form.title = '';
  form.category = '系统公告';
  form.date_text = new Date().toISOString().slice(0, 10);
  form.badge_type = 'notice';
  form.summary = '';
  form.content_html = '';
  drawerVisible.value = true;
}

function handleEdit(row: any) {
  const item = row as IAdminNoticeItem;
  isEdit.value = true;
  currentId.value = item.id;
  form.title = item.title;
  form.category = item.category;
  form.date_text = item.date_text;
  form.badge_type = item.badge_type;
  form.summary = item.summary;
  form.content_html = item.content_html;
  drawerVisible.value = true;
}

async function submitForm() {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    try {
      submitting.value = true;
      if (isEdit.value) {
        await updateNotice(currentId.value, form);
        ElMessage.success('公告已更新');
      } else {
        await createNotice(form);
        ElMessage.success('公告已发布');
      }
      drawerVisible.value = false;
      loadData();
    } catch (error: any) {
      ElMessage.error(error?.message || '保存公告失败');
    } finally {
      submitting.value = false;
    }
  });
}

async function handleDelete(row: any) {
  const item = row as IAdminNoticeItem;
  try {
    await ElMessageBox.confirm(
      `确定要删除公告《${item.title}》吗？删除后前台将立即下架。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    );
    loading.value = true;
    await deleteNotice(item.id);
    ElMessage.success('公告已删除');
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
