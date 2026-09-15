<script lang="ts" setup>
import {
  type IAdminUserItem,
  type IDepartmentNode,
  type IRoleItem,
  deleteAdminUser,
  getAdminRoleList,
  getAdminUserList,
  getDepartmentTree,
  resetAdminUserPassword,
  updateAdminUser,
} from '@/api/rbac';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { OP_TYPE } from '@/constant';
import UserOpDialog from '@/views/om/user/components/userOpDialog.vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const userGlobalData = ref<{ roleList: IRoleItem[]; deptList: IDepartmentNode[] }>({
  roleList: [],
  deptList: [],
});
provide('userGlobalData', userGlobalData);

const loading = ref(false);
const list = ref<IAdminUserItem[]>([]);
const total = ref(0);

const queryParams = reactive({
  page: 1,
  size: 10,
  keyword: '',
  department_id: undefined as string | undefined,
  status: undefined as string | undefined,
});

const columns: IColumnConfig[] = [
  { field: 'username', title: '登录账号', minWidth: 120, fixed: 'left', slot: 'username' },
  { field: 'real_name', title: '真实姓名', minWidth: 110 },
  { field: 'email', title: '工作邮箱', minWidth: 180, showOverflow: true },
  { field: 'phone', title: '联系电话', width: 140, align: 'center', slot: 'phone' },
  { field: 'department_name', title: '所属部门', minWidth: 130, slot: 'dept' },
  { field: 'roles', title: '拥有角色', minWidth: 160, slot: 'roles' },
  { field: 'status', title: '状态', width: 100, align: 'center', slot: 'status' },
  { field: 'last_login_at', title: '最后登录', width: 170, align: 'center', slot: 'last_login' },
  { field: 'actions', title: '操作', width: 220, fixed: 'right', align: 'center', slot: 'actions' },
];

const handlePageChange = (page: number) => {
  queryParams.page = page;
  fetchList();
};

const handleSizeChange = (size: number) => {
  queryParams.size = size;
  queryParams.page = 1;
  fetchList();
};

// 拉取列表
const fetchList = async () => {
  loading.value = true;
  try {
    const res = await getAdminUserList(queryParams);
    list.value = res.list;
    total.value = res.total;
  } finally {
    loading.value = false;
  }
};

// 预加载部门与角色数据
const initGlobalData = async () => {
  try {
    const [roles, depts] = await Promise.all([getAdminRoleList(), getDepartmentTree()]);
    userGlobalData.value.roleList = roles;
    userGlobalData.value.deptList = depts;
  } catch (e) {
    console.error('初始化部门与角色数据异常:', e);
  }
};

onMounted(() => {
  initGlobalData();
  fetchList();
});

const handleSearch = () => {
  queryParams.page = 1;
  fetchList();
};

const handleReset = () => {
  queryParams.keyword = '';
  queryParams.department_id = undefined;
  queryParams.status = undefined;
  queryParams.page = 1;
  fetchList();
};

// 操作弹窗
const dialogVisible = ref(false);
const dialogType = ref<OP_TYPE>(OP_TYPE.ADD);
const currentRow = ref<Partial<IAdminUserItem>>({});

const handleCreate = () => {
  dialogType.value = OP_TYPE.ADD;
  currentRow.value = {};
  dialogVisible.value = true;
};

const handleEdit = (row: any) => {
  dialogType.value = OP_TYPE.EDIT;
  currentRow.value = { ...row };
  dialogVisible.value = true;
};

// 状态切换
const handleStatusChange = async (row: any) => {
  if (row.is_super_admin) {
    ElMessage.warning('超级管理员状态不允许禁用');
    row.status = 'active';
    return;
  }
  try {
    await updateAdminUser(row.id, { status: row.status });
    ElMessage.success('管理员状态已更新');
  } catch {
    row.status = row.status === 'active' ? 'disabled' : 'active';
  }
};

// 重置密码
const handleResetPwd = (row: any) => {
  ElMessageBox.prompt(`请输入管理员 [${row.username}] 的新密码:`, '重置密码', {
    confirmButtonText: '确定重置',
    cancelButtonText: '取消',
    inputPattern: /^.{6,128}$/,
    inputErrorMessage: '密码长度至少6位',
  }).then(async ({ value }) => {
    if (value) {
      await resetAdminUserPassword(row.id, value);
      ElMessage.success('密码已成功重置');
    }
  });
};

// 删除管理员
const handleDelete = (row: any) => {
  if (row.is_super_admin) {
    ElMessage.warning('超级管理员不允许删除');
    return;
  }
  ElMessageBox.confirm(`确认彻底删除管理员账号 [${row.username}] 吗？`, '高风险提示', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    await deleteAdminUser(row.id);
    ElMessage.success('管理员删除成功');
    fetchList();
  });
};
</script>

<template>
  <div class="w-full p-4 flex flex-col gap-4">
    <!-- 筛选面板 -->
    <el-card shadow="never" class="w-full !border-gray-200/60 dark:!border-zinc-800">

      <el-form :inline="true" :model="queryParams" class="flex flex-wrap items-center gap-3">
        <el-form-item label="关键字" class="!mb-0">
          <el-input
            v-model="queryParams.keyword"
            placeholder="搜索账号/姓名/邮箱"
            clearable
            class="!w-56"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="所属部门" class="!mb-0">
          <el-tree-select
            v-model="queryParams.department_id"
            :data="userGlobalData.deptList"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            value-key="id"
            placeholder="全部部门"
            check-strictly
            clearable
            class="!w-48"
          />

        </el-form-item>

        <el-form-item label="账号状态" class="!mb-0">
          <el-select
            v-model="queryParams.status"
            placeholder="全部状态"
            clearable
            class="!w-32"
          >
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>

        <el-form-item class="!mb-0">
          <div class="flex gap-2">
            <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
            <el-button icon="Refresh" @click="handleReset">重置</el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据列表表格 -->
    <DataTable
      :table-data="{ list, total }"
      :columns="columns"
      :loading="loading"
      :table-query="queryParams"
      table-title="管理员账号列表"
      @page-change="handlePageChange"
      @size-change="handleSizeChange"
      @refresh="fetchList"
    >
      <template #options>
        <el-button
          v-auth="['system:user:create']"
          type="primary"
          icon="Plus"
          @click="handleCreate"
        >
          新增管理员
        </el-button>
      </template>

      <template #username="{ row }">
        <div class="flex items-center gap-1.5 font-medium">
          <span>{{ row.username }}</span>
          <el-tag v-if="row.is_super_admin" size="small" type="danger" effect="dark">超管</el-tag>
        </div>
      </template>

      <template #phone="{ row }">
        <span class="font-mono text-xs">{{ row.phone || '-' }}</span>
      </template>

      <template #dept="{ row }">
        <el-tag v-if="row.department_name" size="small" type="info">{{ row.department_name }}</el-tag>
        <span v-else class="text-gray-400">-</span>
      </template>

      <template #roles="{ row }">
        <div class="flex flex-wrap gap-1">
          <el-tag
            v-for="r in row.roles"
            :key="r.id"
            size="small"
            type="warning"
            effect="plain"
          >
            {{ r.name }}
          </el-tag>
          <span v-if="!row.roles?.length" class="text-gray-400 text-xs">无</span>
        </div>
      </template>

      <template #status="{ row }">
        <el-switch
          v-model="row.status"
          active-value="active"
          inactive-value="disabled"
          :disabled="row.is_super_admin"
          @change="handleStatusChange(row)"
        />
      </template>

      <template #last_login="{ row }">
        <span v-if="row.last_login_at" class="text-xs text-gray-500 font-mono">
          {{ row.last_login_at.slice(0, 19).replace('T', ' ') }}
        </span>
        <span v-else class="text-gray-400 text-xs">从未登录</span>
      </template>

      <template #actions="{ row }">
        <div class="flex justify-center items-center gap-1">
          <el-button
            v-auth="['system:user:update']"
            type="primary"
            link
            size="small"
            @click="handleEdit(row)"
          >
            编辑
          </el-button>
          <el-button
            v-auth="['system:user:reset_pwd']"
            type="warning"
            link
            size="small"
            @click="handleResetPwd(row)"
          >
            重置密码
          </el-button>
          <el-button
            v-if="!row.is_super_admin"
            v-auth="['system:user:delete']"
            type="danger"
            link
            size="small"
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </div>
      </template>
    </DataTable>

    <!-- 操作弹窗 -->
    <UserOpDialog
      v-model:is-visible="dialogVisible"
      :data="currentRow"
      :type="dialogType"
      @on-refresh="fetchList"
    />
  </div>
</template>
